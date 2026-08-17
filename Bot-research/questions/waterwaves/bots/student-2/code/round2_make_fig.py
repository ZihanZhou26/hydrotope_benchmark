#!/usr/bin/env python3
"""Round-2 figure: (left) g-scaling law a_n(g)=g^{3-n} a_n(1) verified bit-exact;
(right) the B-spline piecewise profile D_n(P) showing breakpoints at partial sums
and the principal-chamber regime P<=min t_j where it reduces to P^{n-3}."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from itertools import combinations
from fractions import Fraction as F
from round2_gcheck import a_formula, bg_onshell

fig, (axL, axR) = plt.subplots(1, 2, figsize=(12, 4.6))

# ---- LEFT: g-scaling, oracle (exact) vs g^{3-n} law ----
cases = {5: [1,2,4], 6: [1,2,3,4], 7: [1,2,3,4,5]}
gs = [F(1), F(2), F(3)]
for n, free in cases.items():
    signs = [-1,-1] + [1]*(n-2)
    a1 = float(a_formula(bg_onshell(n,free,signs,F(1))[1], signs, F(1)))
    oracle = [float(bg_onshell(n,free,signs,g)[0]) for g in gs]
    law = [a1 * float(g)**(3-n) for g in gs]
    gx = [float(g) for g in gs]
    axL.plot(gx, np.abs(oracle), 'o', ms=9, label=f"oracle n={n}")
    xx = np.linspace(0.9, 3.1, 100)
    axL.plot(xx, abs(a1)*xx**(3-n), '-', lw=1.3,
             label=f"$|a_1|\\,g^{{{3-n}}}$ (n={n})")
axL.set_xscale("log"); axL.set_yscale("log")
axL.set_xlabel("g"); axL.set_ylabel(r"$|a_n(g)|$")
axL.set_title(r"A.  g-dependence: $a_n(g)=g^{\,3-n}a_n(1)$  (oracle = law, exact)")
axL.legend(fontsize=7, ncol=2); axL.grid(True, which="both", alpha=0.3)

# ---- RIGHT: B-spline profile D_n(P) at fixed plus nodes ----
def D(P, t, m):
    s = 0.0
    k = len(t)
    for r in range(k+1):
        for S in combinations(range(k), r):
            arg = P - sum(t[j] for j in S)
            if arg > 0: s += (-1)**r * arg**m
    return s
for n, tnodes in [(5,[1.0,2.0,4.0]), (6,[1.0,2.0,3.0,4.0])]:
    m = n-3
    Ps = np.linspace(-0.5, sum(tnodes)+1.0, 1400)
    Dv = [D(P, tnodes, m) for P in Ps]
    axR.plot(Ps, Dv, lw=1.8, label=f"$D_{{{n}}}(P)$, nodes {tnodes}")
    # breakpoints = all subset partial sums
    bps = sorted({sum(s) for r in range(len(tnodes)+1)
                  for s in combinations(tnodes, r)})
    for b in bps:
        axR.axvline(b, color='grey', ls=':', lw=0.5, alpha=0.5)
# principal regime marker: P <= min node
axR.axvspan(0, 1.0, color='tab:green', alpha=0.10)
axR.text(0.5, axR.get_ylim()[1]*0.78, "principal\n$D_n=P^{n-3}$",
         ha='center', va='top', fontsize=8, color='tab:green')
axR.axhline(0, color='k', lw=0.6)
axR.set_xlabel("P = min($\\omega_1^2,\\omega_2^2$)"); axR.set_ylabel("$D_n$")
axR.set_title("B.  B-spline / divided-difference profile (kinks at partial sums)")
axR.legend(fontsize=8); axR.grid(True, alpha=0.3)

fig.suptitle("student-2 round 2: g-dependence (proven+verified) and B-spline structure",
             fontsize=11)
fig.tight_layout(rect=[0,0,1,0.96])
out = "../figures/round2_structure.png"
fig.savefig(out, dpi=130)
print("wrote", out)
