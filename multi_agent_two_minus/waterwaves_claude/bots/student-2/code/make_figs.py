"""make_figs.py — figures documenting the conjecture A_n = i 2^{n-1} w1 w2^{2n-5}."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractions import Fraction as F
from engine import build_onshell, Engine

FIG = "../figures/"
DATA = "../data/"

def exact(n, free):
    W, K = build_onshell(n, free, [-1, -1] + [1]*(n-2))
    re, im = Engine('frac').BGAmplitude(n, K, W)
    return re, im, W

def conj(n, W):
    return 2**(n-1) * W[1] * W[2]**(2*n-5)

# ---- Panel A: n=4 delta-limit convergence to formula ----
def n4_limit_seq(w2, w3):
    w1, w4 = -w3, -w2
    base = [F(w1), F(w2), F(w3), F(w4)]; d = [F(-1), F(1), F(0), F(0)]; sig = [-1,-1,1,1]
    xs, ys = [], []
    for k in range(1, 7):
        eps = F(1, 10**k)
        Wl = [base[i]+eps*d[i] for i in range(4)]
        W = {i+1: Wl[i] for i in range(4)}; K = {i+1: F(sig[i])*Wl[i]*Wl[i] for i in range(4)}
        re, im = Engine('frac').BGAmplitude(4, K, W)
        xs.append(float(eps)); ys.append(float(im))
    return xs, ys

fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for (w2, w3), col in [((1,3),'C0'), ((2,5),'C1'), ((3,7),'C2')]:
    xs, ys = n4_limit_seq(w2, w3)
    pred = float(8*F(-w3)*F(w2)**3)
    ax[0].plot(xs, [abs((y-pred)/pred) for y in ys], 'o-', color=col,
               label=f"ω=({-w3},{w2},{w3},{-w2}), formula={pred:.0f}")
ax[0].set_xscale('log'); ax[0].set_yscale('log')
ax[0].set_xlabel('δ (off-shell relaxation)'); ax[0].set_ylabel('|a₄(δ) − formula| / |formula|')
ax[0].set_title('n=4 (singular): δ→0 limit → formula  a₄ = 8 ω₁ω₂³')
ax[0].legend(fontsize=8); ax[0].grid(True, which='both', alpha=0.3)

# ---- Panel B: exact relative residuals n=5,6,7 (all 0) ----
pts = {5:[[1,2,4],[2,3,5],[1,2,1000],[2,5,100000],[1,1000,1001]],
       6:[[1,2,3,4],[1,2,3,1000000],[1,5,2,8],[1,100,2,3]],
       7:[[1,2,3,4,5],[1,3,4,5,6],[1,2,3,4,1000],[1,9,2,8,3]]}
rows = []
xlab = []; relerrs = []; colors=[]; cmap={5:'C0',6:'C1',7:'C2'}
for n in (5,6,7):
    for free in pts[n]:
        re, im, W = exact(n, free); pr = conj(n, W)
        r = 0.0 if im==pr else float(abs((im-pr)/pr))
        relerrs.append(max(r,1e-17)); xlab.append(f"n{n}:{free}"); colors.append(cmap[n])
        rows.append(dict(n=n, free=[str(x) for x in free], a_oracle=str(im), a_formula=str(pr),
                         Re=str(re), exact_match=(im==pr and re==0)))
ax[1].bar(range(len(relerrs)), relerrs, color=colors)
ax[1].axhline(1e-10, color='r', ls='--', label='pass bar 1e-10')
ax[1].set_yscale('log'); ax[1].set_ylim(1e-17, 1e-2)
ax[1].set_xticks(range(len(xlab))); ax[1].set_xticklabels(xlab, rotation=90, fontsize=6)
ax[1].set_ylabel('relative residual (exact rational)')
ax[1].set_title('n=5,6,7: a_n vs oracle — exact (residual ≡ 0)')
ax[1].legend(fontsize=8)
plt.tight_layout()
plt.savefig(FIG+"verification.png", dpi=130)
print("wrote", FIG+"verification.png")

with open(DATA+"verification_table.json","w") as f:
    json.dump(rows, f, indent=2)
print("wrote", DATA+"verification_table.json")
