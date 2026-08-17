#!/usr/bin/env python3
"""Locate the walls where A_6 is non-smooth (kinks) by scanning one free
frequency finely and detecting jumps in the high-order finite difference.
Cubic truncations (x)_+^3 give a 3rd-derivative discontinuity, so a kink shows
as a spike in the 4th finite difference. Then match kink locations to k_S=0
(momentum subset walls) to read off which channels enter the truncated powers."""
import numpy as np
import harness as h
import channels as ch

signs = [-1, -1, -1, 1, 1, 1]
CH2 = [S for S in ch.all_channels(6) if len(S) in (2, 3)]


def scan(template, idx, lo, hi, npts):
    xs = np.linspace(lo, hi, npts)
    A = np.full(npts, np.nan)
    for i, x in enumerate(xs):
        free = list(template); free[idx] = float(x)
        try:
            im, oms, _ = h.on_shell(free, signs, double=True)
            if np.isfinite(im):
                A[i] = im
        except Exception:
            pass
    return xs, A


def wall_crossings(template, idx, lo, hi):
    """Return list of (x_wall, channel) where some k_S crosses 0."""
    xs = np.linspace(lo, hi, 4000)
    out = []
    prev = None
    for x in xs:
        free = list(template); free[idx] = float(x)
        oms = h.solve_legs_1n([__import__('fractions').Fraction(v).limit_denominator(10**9) for v in free], signs)
        cur = {}
        for S in CH2:
            k = float(ch.omega_k_S(S, oms, signs)[1])
            cur[tuple(sorted(S))] = k
        if prev is not None:
            for k_, v in cur.items():
                if prev[1].get(k_, 0) * v < 0:
                    out.append((0.5 * (prev[0] + x), k_))
        prev = (x, cur)
    return out


if __name__ == "__main__":
    template = [3, 5, 4, 8]  # legs 2,3,4,5 ; vary leg4 (idx 2)
    lo, hi, npts = 0.3, 12.0, 1201
    xs, A = scan(template, 2, lo, hi, npts)
    # 4th finite difference (normalized) to expose 3rd-derivative jumps
    d4 = np.full_like(A, np.nan)
    for i in range(2, npts - 2):
        if np.all(np.isfinite(A[i-2:i+3])):
            d4[i] = A[i-2] - 4*A[i-1] + 6*A[i] - 4*A[i+1] + A[i+2]
    # robust scale
    med = np.nanmedian(np.abs(d4))
    kink_idx = [i for i in range(npts) if np.isfinite(d4[i]) and abs(d4[i]) > 25*med]
    # cluster adjacent kink indices
    kinks = []
    for i in kink_idx:
        if not kinks or i - kinks[-1][-1] > 3:
            kinks.append([i])
        else:
            kinks[-1].append(i)
    print(f"Scan leg4 in [{lo},{hi}], legs(2,3,5)=({template[0]},{template[1]},{template[3]})")
    print(f"median |d4|={med:.3g}; detected {len(kinks)} kink clusters at leg4 ~:")
    kink_x = [xs[int(np.mean(c))] for c in kinks]
    for kx in kink_x:
        print(f"   leg4 = {kx:.4f}")
    print("\nWall crossings (k_S=0) in the same range:")
    wc = wall_crossings(template, 2, lo, hi)
    # dedupe by rounding
    seen = set()
    for xw, chan in wc:
        key = (round(xw, 3), chan)
        if key in seen: continue
        seen.add(key)
        # is there a kink near here?
        near = any(abs(xw - kx) < 0.05 for kx in kink_x)
        print(f"   leg4={xw:.4f}  channel {list(chan)}   {'<-- KINK' if near else '(smooth, no kink)'}")
