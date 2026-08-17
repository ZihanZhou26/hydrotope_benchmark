#!/usr/bin/env python3
"""Targeted pole search for n=6 three-minus. For each genuine (size-3) channel
S, approach D_S -> 0 along an exact-rational family and report whether A_6
diverges (pole) or converges (removable / no pole).

We use that for a channel S whose legs are all free (subset of {2,3,4,5}),
D_S depends ONLY on the frequencies of legs in S. So we tune one leg in S to a
known exact root of D_S=0 and approach it; the remaining free leg is a spectator.
"""
import harness as h
import channels as ch
from fractions import Fraction as F

signs = [-1, -1, -1, 1, 1, 1]


def approach(S, free_of_eps, label, ks=range(1, 8)):
    """free_of_eps(eps) -> list of 4 free freqs (legs 2,3,4,5). Approach eps->0."""
    print(f"\n--- channel {sorted(S)}  [{label}] ---")
    print(f"  {'eps':>8} {'D_S':>12} {'A6':>15} {'A6*D':>14} {'A6*D^2':>12}")
    last = None
    for k in ks:
        eps = F(1, 10 ** k)
        free = free_of_eps(eps)
        oms = h.solve_legs_1n(free, signs)
        D = ch.D_S(S, oms, signs)
        if D is None:
            print(f"  10^-{k:<3}  |k_S|=0 WALL (skip)")
            continue
        # check no OTHER channel is simultaneously ~0 (would confound)
        others = [(tuple(sorted(T)), float(ch.D_S(T, oms, signs)))
                  for T in ch.all_channels(6)
                  if T != S and ch.D_S(T, oms, signs) is not None]
        near = [(t, d) for t, d in others if abs(d) < 0.02]
        try:
            im, _, _ = h.on_shell(free, signs)
        except Exception:
            print(f"  10^-{k:<3}  oracle SIGFPE (on a wall) -- skip")
            continue
        warn = f"  [also near0: {near}]" if near else ""
        print(f"  10^-{k:<3} {float(D):>12.3e} {float(im):>15.6e} "
              f"{float(im*D):>14.5e} {float(im*D*D):>12.3e}{warn}")
        last = float(im)
    if last is not None:
        print(f"  => A_6 limit ~ {last:.6e}  ({'FINITE (no pole)' if abs(last) < 1e12 else 'DIVERGES'})")


if __name__ == "__main__":
    # {2,3,4}: 2m1p, omega_4* = -19/5 (legs2,3=2,3), spectator leg5=7
    approach(frozenset([2, 3, 4]),
             lambda e: [F(2), F(3), F(-19, 5) + e, F(7)], "2m1p, tune leg4")

    # {2,3,5}: 2m1p, omega_5* = -19/5 (legs2,3=2,3), spectator leg4=7
    approach(frozenset([2, 3, 5]),
             lambda e: [F(2), F(3), F(7), F(-19, 5) + e], "2m1p, tune leg5")

    # {2,4,5}: 1m2p, leg2 minus dominant. legs4,5=(1,2), omega_2*=-7/3, spectator leg3=3
    approach(frozenset([2, 4, 5]),
             lambda e: [F(-7, 3) + e, F(3), F(1), F(2)], "1m2p, tune leg2 (minus-dominant branch)")

    # {3,4,5}: 1m2p, leg3 minus dominant. legs4,5=(1,2), omega_3*=-7/3, spectator leg2=3
    approach(frozenset([3, 4, 5]),
             lambda e: [F(3), F(-7, 3) + e, F(1), F(2)], "1m2p, tune leg3 (minus-dominant branch)")
