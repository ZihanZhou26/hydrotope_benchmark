import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s))
co = lambda s: cells.append(nbf.v4.new_code_cell(s))

md(r"""# Two-minus sector: closed-form $A_n$ for 1-D deep-water waves

**Result.** For the two-minus sector $\sigma=(-1,-1,+1,\dots,+1)$ (legs $1,2$ are
the "minus" legs), the tree amplitude is

$$\boxed{\,A_n \;=\; i\,\cdot 2^{\,n-1}\,g^{\,3-n}\,\big(\omega_1\omega_2\big)\,
\big[\min(\omega_1^2,\omega_2^2)\big]^{\,n-3}\,}$$

equivalently, with $\omega_<,\omega_>$ the smaller/larger-$|\cdot|$ minus-leg
frequencies, $\;A_n = i\,2^{n-1}g^{3-n}\,\omega_>\,\omega_<^{\,2n-5}$.

It depends only on the two minus legs (the plus legs enter solely through the
on-shell constraints).  This cell loads a self-contained Python port of the
Berends–Giele recursion in `OnShellBG.m` and the closed form.""")

co("""import mpmath as mp
from fractions import Fraction as F
from waterwave_bg import (bg_amplitude_hp, closed_form_A, two_minus_kinematics,
                          in_physical_regime)
mp.mp.dps = 50

def report(n, free_w, g=1, label=""):
    k, w, sig = two_minus_kinematics(n, [F(x) for x in free_w], F(g))
    A_bg  = bg_amplitude_hp(k, w, F(g), dps=50)
    A_cf  = closed_form_A(w, sig, F(g))
    rel   = abs(A_bg - A_cf)/abs(A_bg)
    ok    = rel < mp.mpf(10)**-10
    print(f"  {label:22s} n={n} g={str(g):4s}  BG={mp.nstr(A_bg.imag,10)}i  "
          f"closed={mp.nstr(mp.mpf(A_cf.imag),10)}i  rel={mp.nstr(rel,2)}  "
          f"{'PASS' if ok else 'FAIL'}")
    return ok
""")

md("## 1. Standard kinematics (the patterns used in `OnShellBG.m`'s tests)")
co("""ok = []
ok.append(report(5, [3/2, 2, 5/2],          label="A5 {3/2,2,5/2}"))
ok.append(report(5, [1, 3, 5],              label="A5 {1,3,5}"))
ok.append(report(6, [3/2, 2, 5/2, 3],       label="A6 {3/2,2,5/2,3}"))
ok.append(report(6, [1, 3, 5, 7],           label="A6 {1,3,5,7}"))
ok.append(report(7, [3/2, 2, 5/2, 3, 7/2],  label="A7 {3/2,2,5/2,3,7/2}"))
ok.append(report(7, [1, 2, 3, 5, 7],        label="A7 {1,2,3,5,7}"))
print("all pass:", all(ok))
""")

md("""## 2. Non-generic regimes
"one frequency much larger / much smaller than the others" — kept in the
physical regime (a minus leg carries the smallest momentum).""")
co("""ok = []
ok.append(report(5, [2, 3, 1000],   label="plus leg huge"))      # plus 1000 >> rest
ok.append(report(6, [3/2,2,5/2,5000],label="plus leg huge"))
ok.append(report(7, [1,2,5/2,3,10**4],label="plus leg huge"))
# a minus leg made tiny: feed it as the first free frequency (w2 = minus leg)
ok.append(report(5, [F(1,1000), 3, 5], label="minus leg tiny"))
ok.append(report(6, [F(1,500), 3, 5, 7], label="minus leg tiny"))
print("all pass:", all(ok))
""")

md("## 3. Coupling dependence $g\\neq 1$  (checks the $g^{3-n}$ factor)")
co("""ok = []
ok.append(report(5, [1,3,5], g=2,        label="g=2"))
ok.append(report(5, [2,3,5], g=F(7,3),   label="g=7/3"))
ok.append(report(6, [1,3,5,7], g=2,      label="g=2"))
ok.append(report(7, [1,2,3,5,7], g=5,    label="g=5"))
print("all pass:", all(ok))
""")

md("""## 4. The $n=4$ base case (limit)
At $n=4$ the two-minus on-shell manifold collapses to $\\{\\omega_1,\\omega_2\\}=
\\{-\\omega_3,-\\omega_4\\}$, which puts an internal line exactly on-shell ($0/0$
in the propagator).  Approaching it off the momentum-conservation surface
($\\epsilon\\to0$) gives a finite limit equal to the closed form
$A_4=i\\,2^{3}g^{-1}\\,\\omega_1\\omega_2\\min(\\omega_1^2,\\omega_2^2)$.""")
co("""from waterwave_bg import bg_amplitude
def A4_limit(w3, w4, eps):
    # deform off momentum-conservation: w = (-w3, -w4-eps, w3+eps, w4)
    w = [-w3, -w4-eps, w3+eps, w4]
    k = [s*x*x for s, x in zip([-1,-1,1,1], w)]
    return bg_amplitude(k, w, 1)
for (w3, w4) in [(3,2),(5,2),(7,3)]:
    cf = 1j*2**3*( (-w3)*(-w4) )*min(w3**2, w4**2)   # closed form, g=1
    print(f"  w3={w3} w4={w4}: closed={cf.imag:.0f}i   limit:",
          [f"{A4_limit(w3,w4,e).imag:.4f}" for e in (1e-2,1e-3,1e-4,1e-5)])
""")

md("""## 5. Domain note
The closed form is exact whenever a **minus** leg carries the smallest momentum
(`in_physical_regime`).  This covers all the kinematics above.  Because the
Berends–Giele kernels contain $|k|$ (the dispersion is $\\omega^2=g|k|$), the
full amplitude is *piecewise*-rational: in the (non-physical) chambers where a
**plus** leg is the softest, $A_n$ takes a different rational form.  The cell
below flags the regime.""")
co("""for fw in [[2,3,5],[2,3,F(1,1000)]]:
    k,w,sig = two_minus_kinematics(5,[F(x) for x in fw],1)
    print(f"  free={fw}: physical regime (minus leg softest)? {in_physical_regime(w,sig)}")
""")

nb["cells"] = cells
nb["metadata"] = {"kernelspec": {"name": "python3", "display_name": "Python 3"},
                  "language_info": {"name": "python"}}
nbf.write(nb, "two_minus_closed_form.ipynb")
print("wrote two_minus_closed_form.ipynb")
