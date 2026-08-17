#!/usr/bin/env python3
"""ROUND 8 deliverable-1/2: resolve the (1=2) jump exponent at n=7 (uses ./bg --batch, exact).

Round-7 conjecture s1_022: PURE single-wall (1=2) exponent is n-3=4; observed order 2 is a
(1=1)x(1=1) matching cross-term forced onto the (1=2) wall.

New geometric analysis: on {a_2=b_4+b_5} the manifold forces a_1+a_3=b_6+b_7, so the forcing
cross-term factors X=b_6-a_1, Y=b_7-a_3 satisfy X+Y = v (the wall coordinate v:=a_2-b_4-b_5).
ON the wall v=0 => X=-Y; at a GENERIC wall point X_0!=0 => one of (X)_+,(Y)_+ is pinned 0 in a
neighbourhood => the cross-term is locally identically 0 and contributes NOTHING. So (1=2)->2
should be the PURE exponent, contradicting s1_022.

(A) shows the two forcing matchings' cross-terms are locally 0 near a generic (1=2) crossing.
(B) confirms jump order 2 and that J(t)/v(t)^2 is an EXACT polynomial (a clean exp-2 coeff).
"""
from fractions import Fraction as F
import sympy as sp
import n7lib as L, r5lib as RL

SIG = L.SIG7
t = sp.Symbol('t')

def sig_at(bf, p, q, A, B, tt):
    o = L.solve_squares(L.fc_free(bf, p, q, A, B, tt))
    if o is None or any(w == 0 for w in o): return None
    return L.signature(o, with_orderings=True)

def collect_side(bf, p, q, A, B, direction, step, maxn, refsig):
    """contiguous in-chamber points one side; returns [(t, N7, oms)] via batch oracle."""
    tvals, frees, omsl = [], [], []
    for k in range(1, maxn+1):
        tt = direction*step*k
        fr = L.fc_free(bf, p, q, A, B, tt)
        o = L.solve_squares(fr)
        if o is None or any(w == 0 for w in o): break
        s = L.signature(o, with_orderings=True)
        if s is None or s != refsig: break
        tvals.append(tt); frees.append(fr); omsl.append(o)
    if not frees: return []
    ims = L.batch_amp(frees)
    return [(tt, L.N7_from_im(o, im), o) for tt, o, im in zip(tvals, omsl, ims) if im is not None]

def crossterm_diag(name, bf, p, q, A, B, wall_minus, wall_plus, step=F(1,90)):
    mi = wall_minus
    others_m = [x for x in L.MINUS if x != mi]
    others_p = [x for x in L.PLUS if x not in wall_plus]
    print(f"\n--- {name}: forcing (1=1)^2 cross-term activity near the (1=2) wall ---")
    for tt in [-3*step, -step, step, 3*step]:
        o = L.solve_squares(L.fc_free(bf, p, q, A, B, tt))
        if o is None: print(f"  t={tt}: degenerate"); continue
        sq = [w*w for w in o]
        v = sq[mi] - sum(sq[j] for j in wall_plus)
        m1, m2 = others_m; pp1, pp2 = others_p
        X1, Y1 = sq[pp1]-sq[m1], sq[pp2]-sq[m2]
        X2, Y2 = sq[pp2]-sq[m1], sq[pp1]-sq[m2]
        ct1 = (X1 if X1 > 0 else 0)*(Y1 if Y1 > 0 else 0)
        ct2 = (X2 if X2 > 0 else 0)*(Y2 if Y2 > 0 else 0)
        print(f"  t={str(tt):>8}  v={float(v):+.4f}  matchA(X1,Y1)=({float(X1):+.3f},{float(Y1):+.3f}) ct={float(ct1):.4g}"
              f"   matchB(X2,Y2)=({float(X2):+.3f},{float(Y2):+.3f}) ct={float(ct2):.4g}")

def measure_e(name, bf, p, q, A, B, wall_minus, wall_plus, exp_guess, step=F(1,90), maxn=80, dmax=46):
    sL = sig_at(bf, p, q, A, B, -step/3); sR = sig_at(bf, p, q, A, B, +step/3)
    if sL is None or sR is None: print(f"[{name}] degenerate"); return None
    sd = sum(1 for a, b in zip(sL[:42], sR[:42]) if a != b)
    ptsL = collect_side(bf, p, q, A, B, -1, step, maxn, sL)
    ptsR = collect_side(bf, p, q, A, B, +1, step, maxn, sR)
    cL = RL.fit_poly([(x, y) for (x, y, _) in ptsL], dmax)
    cR = RL.fit_poly([(x, y) for (x, y, _) in ptsR], dmax)
    if cL is None or cR is None:
        print(f"[{name}] fit fail nL={len(ptsL)} nR={len(ptsR)} L={cL is not None} R={cR is not None}"); return None
    NL = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cL))
    NR = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cR))
    J = sp.expand(NR - NL)
    if J == 0:
        print(f"[{name}] sd={sd} JUMP=0 (not a wall of N_7)"); return None
    Pj = sp.Poly(J, t); order = min(m for (m,), _ in Pj.terms())
    # wall coordinate v(t) (use the side with more pts)
    side = ptsR if len(ptsR) >= len(ptsL) else ptsL
    vpts = [(tt, [w*w for w in o][wall_minus]-sum([w*w for w in o][j] for j in wall_plus)) for (tt, _, o) in side[:8]]
    cv = RL.fit_poly(vpts, 6)
    vt = sum(sp.Rational(c.numerator, c.denominator)*t**j for j, c in enumerate(cv))
    quo, rem = sp.div(J, sp.expand(vt**exp_guess), t)
    ok = sp.simplify(rem) == 0
    print(f"[{name}] sd={sd} nL={len(ptsL)} nR={len(ptsR)} JUMP ORDER={order}; "
          f"J/v^{exp_guess} exact-divides={ok}")
    return order, ok

if __name__ == "__main__":
    cfgs = [
        ("chamber #1", [F(5), F(11,3), F(3), F(4), F(15,2)], 2, 4, F(3), F(15,2)),
        ("chamber #2", [F(13), F(7,2), F(5), F(12), F(9)], 2, 4, F(5), F(9)),
        ("chamber #3", [F(10), F(9,2), F(6), F(8), F(11,2)], 2, 4, F(6), F(11,2)),
        ("chamber #4", [F(17,2), F(23,5), F(4), F(7), F(21,2)], 2, 4, F(4), F(21,2)),
    ]
    print("="*72)
    print("(A) forcing (1=1)^2 cross-term activity at GENERIC (1=2) crossings (expect ct=0)")
    print("="*72)
    for (nm, bf, p, q, A, B) in cfgs:
        crossterm_diag(nm, bf, p, q, A, B, wall_minus=1, wall_plus=[3, 4])
    print("\n" + "="*72)
    print("(B) jump order + J/v^2 polynomial (=> genuine PURE exp-2 (1=2) term)")
    print("="*72)
    for (nm, bf, p, q, A, B) in cfgs:
        measure_e(nm, bf, p, q, A, B, wall_minus=1, wall_plus=[3, 4], exp_guess=2)
