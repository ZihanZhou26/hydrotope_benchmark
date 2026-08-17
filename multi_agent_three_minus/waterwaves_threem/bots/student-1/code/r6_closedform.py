#!/usr/bin/env python3
"""SELF-CONTAINED closed form for A_6 in the three-minus sector (student-1, round 6).

    A_6 = i * 2^5 * g^{-3} * N_6(omega) / (e3m + e3p),   e3m=w1 w2 w3, e3p=w4 w5 w6,

with N_6 a degree-11, S_3(minus 1,2,3) x S_3(plus 4,5,6) x Z_2(swap)-symmetric, ODD,
CONTINUOUS truncated-power (box) SPLINE:

    N_6 = B                                          (smooth symmetric base, deg 11)
        + sum_{i in M, j in P} (b_j - a_i)_+ P_ij          (single (1=1) walls; exp 1)
        + sum_{disjoint matching pairs} (b_j-a_i)_+ (b_l-a_k)_+ R_{ij,kl}  (pair cross; exp 1,1)
        + sum_{(1=2) walls} (a_i - b_j - b_k)_+^3 Q_ijk     ((1=2) walls; exp 3)

a_i = w_i^2 (minus), b_j = w_j^2 (plus); (x)_+ = max(x,0); g=1 here.
NO triple-(1=1) cross-term is needed (verified: it adds nothing).

The base B, the single coefficient P_ij, and the pair coefficient R are the S_3xS_3xZ_2
orbit images of explicit reference polynomials B, P0, R0; Q is the PI-verified (1=2)
coefficient (s1_015). All coefficients are exact rationals (r6_coeffs.pkl); they were
fixed by an exact modular fit (rank 100) over the oracle and rational-reconstructed.

This module evaluates A_6 directly (imaginary coefficient, g=1) for cross-checking.
"""
from fractions import Fraction as F
import pickle, os, itertools
import r5_group as Gp, r5_basis as Bm, r5_global as G2, r5_corr as C, inv

_HERE=os.path.dirname(os.path.abspath(__file__))
_G=Gp.full_group()
_labels,_rcoef=pickle.load(open(os.path.join(_HERE,"r6_coeffs.pkl"),"rb"))

def _relabel_rows(o): return [[F(x) for x in Gp.apply_perm(p,o)] for p in _G]

def _col(label,o,rows):
    typ=label[0]
    if typ=='base': return F(G2.eval_base(label[1],o))
    if typ=='single':
        m=label[1]; s=F(0)
        for ro in rows:
            k=ro[3]**2-ro[0]**2
            if k>0: s+=k*Bm.eval_h(m,ro,'P')
        return s
    if typ=='pair':
        e=label[1]; s=F(0)
        for ro in rows:
            k03=ro[3]**2-ro[0]**2; k14=ro[4]**2-ro[1]**2
            if k03>0 and k14>0:
                v=k03*k14
                for i in range(6):
                    if e[i]: v*=ro[i]**e[i]
                s+=v
        return s
    raise ValueError(typ)

def N6(o):
    """o = [w1..w6] Fractions on the manifold. Returns N_6 (exact Fraction)."""
    o=[F(x) for x in o]; rows=_relabel_rows(o)
    return sum(c*_col(l,o,rows) for l,c in zip(_labels,_rcoef)) + C.corr12(o)

def A6_imag(o, g=F(1)):
    """imaginary coefficient of A_6 (A_6 = i * A6_imag). g general via homogeneity."""
    o=[F(x) for x in o]
    e=inv.invariants(o); denom=e[2]+e[3]
    if denom==0: raise ZeroDivisionError("on the pole e3m+e3p=0")
    # g=1 base; restore g: A_6 = i 2^5 g^-3 N/(e3m+e3p). N is g-independent on manifold (built from w only).
    return F(32, 1)*N6(o)/denom * (g**(-3) if g!=1 else 1)

if __name__=="__main__":
    import chambers_n6 as cn, harness as h, random
    rnd=random.Random(5); ok=ntot=0
    for _ in range(8):
        free=[F(rnd.randint(-90,90),10) for _ in range(4)]
        if 0 in free: continue
        o=cn.solve_squares(free)
        if o is None or any(w==0 for w in o): continue
        try:
            a=A6_imag(o); b,_,_=h.on_shell(free,[-1,-1,-1,1,1,1])
        except Exception as ex: print("skip",ex); continue
        ntot+=1; ok+=(a==b)
        print(f"free={[str(x) for x in free]}  A6/i closedform={a}  match={a==b}")
    print(f"\n{ok}/{ntot} exact")
