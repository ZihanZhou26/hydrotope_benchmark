#!/usr/bin/env python3
"""Broad 1-parameter scan: vary one free frequency, watch A_6 (double) and all
D_S channel denominators. If A_6 has a factorization pole, it must blow up
exactly where some D_S crosses 0. If A_6 stays finite as D_S->0, that channel
does NOT produce a pole (residue cancels)."""
import numpy as np
import harness as h
import channels as ch

signs = [-1, -1, -1, 1, 1, 1]
CH = ch.all_channels(6)


def scan(free_template, vary_idx, lo, hi, npts=400):
    """free_template: 4 free freqs (legs 2,3,4,5); vary free_template[vary_idx]."""
    xs = np.linspace(lo, hi, npts)
    rows = []
    for x in xs:
        free = list(free_template)
        free[vary_idx] = float(x)
        try:
            im, oms, _ = h.on_shell(free, signs, double=True)
        except Exception:
            continue
        # D_S for all channels (use float)
        Ds = {}
        for S in CH:
            wS = sum(oms[i - 1] for i in S)
            kS = sum(signs[i - 1] * oms[i - 1] ** 2 for i in S)
            Ds[tuple(sorted(S))] = (abs(wS * wS / abs(kS) - 1.0)
                                    if abs(kS) > 1e-12 else np.nan)
        rows.append((x, im, Ds, oms))
    return rows


def report(free_template, vary_idx, lo, hi, label):
    rows = scan(free_template, vary_idx, lo, hi)
    print(f"\n=== scan {label}: leg{vary_idx+2} in [{lo},{hi}], "
          f"others(legs2,3,4,5)={free_template} ===")
    ims = np.array([abs(r[1]) for r in rows])
    print(f"  |A_6| range: {ims.min():.4g} .. {ims.max():.4g}")
    # for each channel, find min |D_S| over scan and the |A_6| there
    print(f"  {'channel':>16} {'min|D_S|':>12} {'|A_6| there':>14} "
          f"{'|A_6| nbr-avg':>14}")
    for S in CH:
        key = tuple(sorted(S))
        dvals = np.array([r[2][key] for r in rows])
        if np.all(np.isnan(dvals)):
            continue
        j = np.nanargmin(dvals)
        # neighbour average away from the min
        nbr = ims[max(0, j-20)], ims[min(len(ims)-1, j+20)]
        flag = ""
        if dvals[j] < 0.05:  # got close to channel
            ratio = ims[j] / (0.5*(nbr[0]+nbr[1]) + 1e-30)
            flag = "  <== POLE?" if ratio > 5 else "   (finite)"
        print(f"  {str(sorted(S)):>16} {dvals[j]:>12.4g} {ims[j]:>14.4g} "
              f"{0.5*(nbr[0]+nbr[1]):>14.4g}{flag}")


if __name__ == "__main__":
    # base free (legs 2,3,4,5) = [2,3,5,7]; scan each free leg widely
    report([2, 3, 5, 7], 0, -12, 12, "vary leg2")
    report([2, 3, 5, 7], 1, -12, 12, "vary leg3")
    report([2, 3, 5, 7], 2, -12, 12, "vary leg4")
    report([2, 3, 5, 7], 3, -12, 12, "vary leg5")
