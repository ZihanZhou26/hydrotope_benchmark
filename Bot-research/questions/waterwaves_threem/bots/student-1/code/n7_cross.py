#!/usr/bin/env python3
"""n=7 CROSS-TERM detector (student-1, round 7), base-free & single-free.

On a 2-parameter slice keeping sumFree (=w4+w5+w6 part) fixed so N_7(s,u) is a
polynomial, pick the base point so two target walls W1,W2 vanish at (s,u)=(0,0),
with W1 ~ linear in s and W2 ~ linear in u. The MIXED second difference
   D2 = N(+,+) - N(+,-) - N(-,+) + N(-,-)
kills the smooth base AND all single-wall truncated powers (each smooth in the
OTHER variable), leaving only CROSS-terms containing BOTH W1 and W2. We reconstruct
N_7 as a bivariate polynomial on each of the 4 quadrant-chambers and read off the
cross-term: its joint order in (s,u) at the corner = the per-factor exponents.

2-param family: free = [w2, w3, w4=A+s, w5=B+u, w6=C-s-u]   (w4+w5+w6 = A+B+C fixed
=> sumFree fixed => w1,w7 polynomial in (s,u) => N_7 polynomial in (s,u)).
"""
from fractions import Fraction as F
import sympy as sp, itertools
import n7lib as L

s, u = sp.symbols('s u')

def free_su(w2, w3, A, B, C, sv, uv):
    return [F(w2), F(w3), F(A)+sv, F(B)+uv, F(C)-sv-uv]

def Nval(free):
    o = L.solve_squares(free)
    if o is None or any(w == 0 for w in o):
        return None, None
    return o, None  # value filled by batch

def collect_quadrant(w2, w3, A, B, C, ds, du, step, npts, refsig):
    """grid of points in one quadrant (signs ds,du), staying in one chamber."""
    grid = []
    omsl = []
    frees = []
    for i in range(1, npts+1):
        for j in range(1, npts+1):
            sv = ds*step*i; uv = du*step*j
            fr = free_su(w2, w3, A, B, C, sv, uv)
            o = L.solve_squares(fr)
            if o is None or any(w == 0 for w in o):
                continue
            sig = L.signature(o, with_orderings=False)
            if sig != refsig:
                continue
            grid.append((sv, uv)); omsl.append(o); frees.append(fr)
    if not frees:
        return []
    ims = L.batch_amp(frees)
    out = []
    for (sv, uv), o, im in zip(grid, omsl, ims):
        if im is None: continue
        out.append((sv, uv, L.N7_from_im(o, im)))
    return out

def fit_biv(pts, dmax_s, dmax_u):
    """fit N(s,u)=sum c_ab s^a u^b, a<=dmax_s, b<=dmax_u, exact; validate on extra pts."""
    monos = [(a, b) for a in range(dmax_s+1) for b in range(dmax_u+1)]
    nm = len(monos)
    if len(pts) < nm + 5:
        return None
    # exact solve with first nm pts, validate on rest
    import r5lib as RL
    A = [[F(sv)**a * F(uv)**b for (a, b) in monos] for (sv, uv, _) in pts[:nm]]
    rhs = [v for (_, _, v) in pts[:nm]]
    sol = RL.solve_exact(A, rhs)
    if sol is None:
        return None
    for (sv, uv, v) in pts[nm:nm+8]:
        if sum(c*F(sv)**a*F(uv)**b for c, (a, b) in zip(sol, monos)) != v:
            return None
    return dict(zip(monos, sol))

def order_at_corner(poly_dict):
    """lowest total (a+b) with nonzero coeff, plus min a and min b among nonzero."""
    nz = [(a, b) for (a, b), c in poly_dict.items() if c != 0]
    if not nz:
        return None
    return (min(a+b for a, b in nz), min(a for a, b in nz), min(b for a, b in nz))

def detect(name, w2, w3, A, B, C, step=F(1,50), npts=10, dmax=14):
    """W1 crossed by s, W2 crossed by u; compute mixed 2nd diff structure."""
    # reference signatures of the 4 quadrants
    refs = {}
    for ds in (-1, 1):
        for du in (-1, 1):
            fr = free_su(w2, w3, A, B, C, ds*step/3, du*step/3)
            o = L.solve_squares(fr)
            if o is None or any(w == 0 for w in o):
                print(f"  [{name}] degenerate quadrant ({ds},{du})"); return None
            refs[(ds, du)] = L.signature(o, with_orderings=False)
    # how many walls differ between the 4 quadrants (want exactly the 2 target walls)
    allsig = list(refs.values())
    nwall = len(allsig[0])
    diffcount = sum(1 for k in range(nwall) if len({sg[k] for sg in allsig}) > 1)
    polys = {}
    for ds in (-1, 1):
        for du in (-1, 1):
            pts = collect_quadrant(w2, w3, A, B, C, ds, du, step, npts, refs[(ds, du)])
            pd = fit_biv(pts, dmax, dmax)
            polys[(ds, du)] = (pd, len(pts))
    if any(pd is None for (pd, _) in polys.values()):
        ns = {k: v[1] for k, v in polys.items()}
        print(f"  [{name}] fit fail; #pts/quadrant={ns}; walls-differing={diffcount}")
        return None
    # mixed 2nd difference of the polynomial pieces (as polynomials in s,u)
    def P(k): return sum(c*s**a*u**b for (a, b), c in polys[k][0].items())
    D2 = sp.expand(P((1, 1)) - P((1, -1)) - P((-1, 1)) + P((-1, -1)))
    if D2 == 0:
        print(f"  [{name}] walls-differing={diffcount}  MIXED 2nd DIFF = 0  -> NO (W1xW2) cross-term")
        return ('none',)
    pd = sp.Poly(D2, s, u).as_dict()
    nz = [(a, b) for (a, b), c in pd.items() if c != 0]
    mina = min(a for a, b in nz); minb = min(b for a, b in nz); mint = min(a+b for a, b in nz)
    print(f"  [{name}] walls-differing={diffcount}  MIXED 2nd DIFF != 0 -> CROSS-TERM present; "
          f"min s-order={mina}, min u-order={minb}, min total={mint}")
    return ('cross', mina, minb)

if __name__ == "__main__":
    # W1: (1=1) {a2=b4}: vary s = w4 around w2=3.  W2: (1=1) {a3=b5}: vary u = w5 around w3.
    # base: w2=3,w3=4; A=w4=3(=w2), B=w5=4(=w3), C=w6 free. At (0,0): a2=b4 and a3=b5.
    print("=== (1=1) x (1=1):  {a2=b4} & {a3=b5}  (disjoint mixed edges) ===")
    detect("11x11 a2b4,a3b5", 3, 4, 3, 4, 8)

    # W1: (1=1) {a2=b4} (s=w4 around w2=3); W2: (1=2) {a3=b5+b6} (u: tune so w3^2=w5^2+w6^2).
    # need a3=b5+b6 at (0,0): w3^2 = B^2 + C^2. pick w3=5, B=w5=3, C=w6=4 -> 9+16=25 ✓.
    # but u shifts w5=B+u and w6=C-s-u; at s=0, W2 = w5^2+w6^2-w3^2 = (3+u)^2+(4-u)^2-25.
    print("\n=== (1=1) x (1=2):  {a2=b4} & {a3=b5+b6} ===")
    detect("11x12 a2b4,a3b5b6", 3, 5, 3, 3, 4)
