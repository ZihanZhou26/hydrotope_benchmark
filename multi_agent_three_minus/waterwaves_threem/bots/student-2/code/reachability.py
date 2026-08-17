#!/usr/bin/env python3
"""Random-sample the n=6 three-minus resonant manifold and, for each channel S,
record the range of D_S and whether D_S can cross 0 (i.e. the channel is
reachable as a potential factorization pole). Also record range of A_6.
Uses --double for speed. Legs 2,3 are minus (free), legs 4,5 are plus (free);
legs 1,6 solved."""
import numpy as np
import harness as h
import channels as ch

signs = [-1, -1, -1, 1, 1, 1]
CH = ch.all_channels(6)
rng = np.random.default_rng(20260626)


def sample(nsamp=4000, span=(-10, 10)):
    stats = {tuple(sorted(S)): {"min": np.inf, "max": -np.inf, "neg": 0, "pos": 0}
             for S in CH}
    a6 = []
    good = 0
    for _ in range(nsamp):
        free = rng.uniform(span[0], span[1], 4)
        # avoid near-degenerate (equal magnitudes) to dodge walls
        try:
            im, oms, _ = h.on_shell(list(free), signs, double=True)
        except Exception:
            continue
        if not np.isfinite(im):
            continue
        ok = True
        ds = {}
        for S in CH:
            wS = sum(oms[i - 1] for i in S)
            kS = sum(signs[i - 1] * oms[i - 1] ** 2 for i in S)
            if abs(kS) < 1e-9:
                ok = False; break
            ds[tuple(sorted(S))] = wS * wS / abs(kS) - 1.0
        if not ok:
            continue
        good += 1
        a6.append(abs(im))
        for k, d in ds.items():
            st = stats[k]
            st["min"] = min(st["min"], d); st["max"] = max(st["max"], d)
            if d < 0: st["neg"] += 1
            else: st["pos"] += 1
    return stats, np.array(a6), good


if __name__ == "__main__":
    stats, a6, good = sample()
    print(f"good samples: {good};  |A_6| range: {a6.min():.3g} .. {a6.max():.3g}; "
          f"median {np.median(a6):.3g}")
    print(f"\n{'channel':>16} {'type':>6} {'D_min':>9} {'D_max':>9} "
          f"{'crosses0?':>10}")
    for S in CH:
        k = tuple(sorted(S))
        st = stats[k]
        minus = sum(1 for i in S if i <= 3)
        typ = f"{minus}m{len(S)-minus}p"
        crosses = "YES" if (st["neg"] > 0 and st["pos"] > 0) else "no"
        print(f"{str(k):>16} {typ:>6} {st['min']:>9.3f} {st['max']:>9.3f} "
              f"{crosses:>10}")
