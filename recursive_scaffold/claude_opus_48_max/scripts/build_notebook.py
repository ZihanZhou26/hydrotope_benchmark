"""Build the deliverable Jupyter notebook two_minus_amplitude.ipynb."""
import nbformat as nbf
import os

nb = nbf.v4.new_notebook()
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
code = lambda s: cells.append(nbf.v4.new_code_cell(s))

md(r"""# Two-minus-sector tree amplitude for 1D deep-water waves

**Closed-form result** (legs 1,2 are the minus legs, frequencies $\omega_1,\omega_2$; $g$ = gravity):

$$\boxed{\,A_n \;=\; i\,2^{\,n-1}\,\omega_1\omega_2\,\Big(\tfrac{\min(\omega_1^2,\omega_2^2)}{g}\Big)^{\,n-3}\,}$$

equivalently $A_n = i\,2^{n-1}\,\nu\,\mu^{2n-5}/g^{n-3}$ with $|\mu|\le|\nu|$ the two minus frequencies.

- $A_n$ is **purely imaginary**; it depends only on the two minus legs (not the plus distribution).
- Valid in the **interleaving region**: every plus leg $|\omega_j|$ lies between $\min(|\omega_1|,|\omega_2|)$ and $\max(|\omega_1|,|\omega_2|)$ (the full sector amplitude is piecewise / non-analytic — see `SCOPE.md`).

This notebook evaluates the formula and checks it against the exact Berends–Giele oracle.""")

code("""import sys, os
from fractions import Fraction as F
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))
sys.path.insert(0, "scripts")
from formula import two_minus_amplitude, two_minus_amplitude_im
from bg import bg_amplitude, make_kinematics, two_minus_sigmas

def interleaving(allW):
    lo = min(abs(allW[0]), abs(allW[1])); hi = max(abs(allW[0]), abs(allW[1]))
    return all(lo <= abs(w) <= hi for w in allW[2:])
print("loaded")""")

md("""## 1. Evaluate the formula
`two_minus_amplitude(n, w1, w2, g)` returns `(Re, Im)` of $A_n$ (Re is always 0).""")

code("""# example: n=5, minus legs (-9/2, 2), g=1
print("A_5 =", two_minus_amplitude(5, F(-9,2), F(2), 1), " (i.e. -2304 i)")
print("A_7 =", two_minus_amplitude(7, F(-371,50), F(3,2), 1))""")

md("""## 2. Verify against the exact BG oracle
We build on-shell two-minus kinematics with `make_kinematics`, run the exact
`bg_amplitude`, and compare to the formula across several $n$ and $g$
(interleaving points; exact rational arithmetic).""")

code("""cases = [
    (5, [F(2), F(5,2), F(3)], F(1)),
    (5, [F(1), F(2), F(3)], F(2)),
    (6, [F(3,2), F(2), F(5,2), F(3)], F(1)),
    (6, [F(1), F(2), F(3), F(4)], F(3)),
    (7, [F(3,2), F(2), F(5,2), F(3), F(7,2)], F(1)),
]
print(f"{'n':>2}{'g':>4}{'minus':>14}{'BG oracle A_n':>22}{'formula':>22}  ok")
allok = True
for n, fw, g in cases:
    allK, allW = make_kinematics(n, fw, two_minus_sigmas(n), g)
    assert interleaving(allW)
    A = bg_amplitude(allK, allW, g)
    re, im = two_minus_amplitude(n, allW[0], allW[1], g)
    ok = (A.re == re and A.im == im); allok &= ok
    print(f"{n:>2}{str(g):>4}{f'({allW[0]},{allW[1]})':>14}{f'{A.re}+{A.im}i':>22}{f'{re}+{im}i':>22}  {ok}")
print("ALL OK:", allok)""")

md("""## 3. The $n=4$ degenerate boundary
At $n=4$ the on-shell manifold is forced ($\\omega_3=-\\omega_1,\\omega_4=-\\omega_2$), so
`BGAmplitude` hits $0/0$. The formula gives the $\\varepsilon\\to0$ limit
$A_4 = i\\,8\\,\\omega_1\\omega_2\\min(\\omega_1^2,\\omega_2^2)/g$.""")

code("""# eps-deformation limit reproduces the formula value
def a4_eps(w1, w2, eps):
    w4 = -w2 + eps; w3 = -(w1+w2+w4)
    allW=[w1,w2,w3,w4]; sig=two_minus_sigmas(4)
    allK=[sig[i]*allW[i]**2 for i in range(4)]
    return bg_amplitude(allK, allW, 1).im
w1,w2 = F(-9), F(4)
print("formula a_4 =", two_minus_amplitude_im(4, w1, w2))
for e in [F(1,1000), F(1,1000000)]:
    print(f"  eps={float(e):.0e}: BG a_4 ~ {float(a4_eps(w1,w2,e)):.6f}")""")

md("""## 4. How it was found (summary)
1. Exact Python port of `OnShellBG.m`, validated to the oracle.
2. $A_n$ purely imaginary; $a_n=\\mathrm{Im}\\,A_n$ homogeneous degree $2n-4$; symmetric in the two minus legs.
3. A polynomial ansatz failed → the amplitude is rational/piecewise (the kernels contain $|k_S|$).
4. Holding the minus pair fixed and varying the plus legs: $a_n$ is **constant** in the interleaving region ⇒ depends only on $(\\omega_1,\\omega_2)$.
5. Fitting across minus pairs: $F_{n+1}/F_n = 2\\min(\\omega_1^2,\\omega_2^2)$, $F_5 = 16\\,\\omega_1\\,(\\text{smaller minus})^5$ ⇒ the boxed formula; $g$-power $g^{-(n-3)}$.
6. Verified exactly for $n=4$–$8$, multiple $g$, and a held-out batch.""")

nb["cells"] = cells
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3"},
}
out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "two_minus_amplitude.ipynb")
with open(out, "w") as f:
    nbf.write(nb, f)
print("wrote", out)
