#!/usr/bin/env python3
"""n=7 structural probe (student-1, round 6): measure A_7's jump exponents across a (1=1)
and a (1=2) wall, by exact per-side RATIONAL reconstruction (the denominator D_7 is smooth
across a difference-branch wall). Also verify the algebraic fact that at n=7 two disjoint
(1=1) edges force a (1=2) relation (not a third (1=1) edge) -> the cross-term structure
differs from n=6.

n=7: minus {1,2,3}, plus {4,5,6,7}; free legs 2..6 (5 of them), legs 1,7 solved.
F-const slice: w4=A+t, w5=B-t (sumFree fixed) -> A_7(t) rational in t.
"""
from fractions import Fraction as F
import sympy as sp
import harness as h
t=sp.Symbol('t')
SIG7=[-1,-1,-1,1,1,1,1]

def A7(free):
    try: im,_,_=h.on_shell(free,SIG7); return im
    except Exception: return None

def D12(free):
    """prod_{i in minus} prod_{j in plus} (w_i+w_j) = Res(p_-,Q_7); A_7*D12 is polynomial/chamber."""
    om=h.solve_legs_1n(free,SIG7)   # [w1..w7]
    if any(om[i]==0 for i in range(7)): return None,None
    M=[om[0],om[1],om[2]]; P=[om[3],om[4],om[5],om[6]]
    d=F(1)
    for wi in M:
        for wj in P: d*=(wi+wj)
    return d,om

def A7D12(free):
    d,om=D12(free)
    if d is None: return None
    a=A7(free)
    if a is None: return None
    return a*d

def fit_poly_auto(pts, dmax=40):
    """fit value(t) as polynomial in t (low->high), exact; None if not poly up to dmax."""
    import r5lib as L
    return L.fit_poly(pts, dmax)

def pade(pts, P, Q):
    """reconstruct v(t)=num/den, deg num<=P, deg den<=Q, den(0)=1; needs P+Q+1 pts."""
    n=P+Q+1
    if len(pts)<n: return None
    rows=[]; rhs=[]
    for (ti,vi) in pts[:n]:
        ti=sp.Rational(ti.numerator,ti.denominator); vi=sp.Rational(vi.numerator,vi.denominator)
        row=[ti**k for k in range(P+1)]+[-vi*ti**k for k in range(1,Q+1)]
        rows.append(row); rhs.append(vi)   # vi*den0(=1) term moved: num - vi*sum den_k t^k =0 => num - vi*(1+...)=0
    # unknowns: a0..aP (num), b1..bQ (den, b0=1). Equation: sum a_k t^k - vi*(1+ sum b_k t^k)=0
    M=[[F(sp.Rational(x)) for x in row]+[F(sp.Rational(rhs[i]))] for i,row in enumerate(rows)]
    nun=P+1+Q
    # gaussian
    for c in range(nun):
        piv=next((r for r in range(c,nun) if M[r][c]!=0),None)
        if piv is None: return None
        M[c],M[piv]=M[piv],M[c]; pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for r in range(nun):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[M[r][k]-f*M[c][k] for k in range(nun+1)]
    sol=[M[i][nun] for i in range(nun)]
    a=sol[:P+1]; b=[F(1)]+sol[P+1:]
    num=sum(sp.Rational(a[k].numerator,a[k].denominator)*t**k for k in range(P+1))
    den=sum(sp.Rational(b[k].numerator,b[k].denominator)*t**k for k in range(Q+1))
    # validate on remaining points
    for (ti,vi) in pts[n:n+4]:
        tr=sp.Rational(ti.numerator,ti.denominator)
        if sp.simplify(num.subs(t,tr)-sp.Rational(vi.numerator,vi.denominator)*den.subs(t,tr))!=0:
            return None
    return sp.cancel(num/den)

def jump_order(base_free, idx_vary, idx_comp, A0, B0, tstar, hstep=F(1,60), npts=46):
    """fit A_7*D12(t) as POLYNOMIAL each side of t=tstar; jump order at tstar."""
    import r5lib as L
    def side(direction):
        pts=[]
        for k in range(1,npts+1):
            tt=tstar+direction*hstep*k
            free=list(base_free); free[idx_vary]=A0+tt; free[idx_comp]=B0-tt
            v=A7D12(free)
            if v is None: break
            pts.append((tt,v))
        return pts
    pl=side(-1); pr=side(+1)
    cl=L.fit_poly(pl,40); cr=L.fit_poly(pr,40)
    if cl is None or cr is None: return None,None,(len(pl),len(pr)),('polyL?' if cl is None else '', 'polyR?' if cr is None else '')
    NL=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cl))
    NR=sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(cr))
    d=sp.expand(NR-NL)
    if d==0: return d,'SMOOTH(0)',(len(pl),len(pr)),(len(cl)-1,len(cr)-1)
    P=sp.Poly(d,t); ts=sp.Rational(tstar.numerator,tstar.denominator)
    order=0; nn=P
    while nn.eval(ts)==0 and nn.degree()>0:
        nn=nn.diff(t); order+=1
    return d, order, (len(pl),len(pr)),(len(cl)-1,len(cr)-1)

if __name__=="__main__":
    print("=== algebraic: at n=7 two disjoint (1=1) edges a2=b4 & a3=b5 force a (1=2) ===")
    print("    a1 = Q - a2 - a3 = (b4+b5+b6+b7) - b4 - b5 = b6 + b7  => {a1=b6+b7} is a (1=2) wall.")
    print("    (so n=6's 'pairs complete a matching of (1=1) edges' does NOT hold at n=7.)\n")

    # (1=1) wall {a2=b4}: vary w4 (idx 2 in free=[w2,w3,w4,w5,w6]); compensate w5 (idx 3).
    # base point: free=[w2,w3, w4=w2 at t=0, w5, w6]; choose generic to avoid other walls.
    print("=== (1=1) wall {a2=b4} (w4->w2): jump exponent of A_7 ===",flush=True)
    base=[F(3),F(5),F(3),F(8),F(11,2)]  # w4=A0=3=w2 at t=0
    d,order,cnt,deg=jump_order(base, 2, 3, F(3), F(8), F(0))
    print(f"  pts={cnt}  per-side poly deg={deg}  jump order at wall = {order}",flush=True)

    print("\n=== (1=2) wall: w4^2 -> w2^2+w3^2 (w2=3,w3=4 -> w4=5) ===",flush=True)
    base2=[F(3),F(4),F(5),F(9),F(13,2)]  # w4=5 at t=0, w2^2+w3^2=25=w4^2
    d2,order2,cnt2,deg2=jump_order(base2, 2, 3, F(5), F(9), F(0))
    print(f"  pts={cnt2}  per-side poly deg={deg2}  jump order at wall = {order2}",flush=True)

    print("\n=== (1=3) wall: w4^2 -> w2^2+w3^2+w6^2 (vary w4) ===",flush=True)
    # choose w2,w3,w6 with w2^2+w3^2+w6^2 a perfect square for w4 at t=0
    # 2^2+3^2+6^2=49 -> w4=7
    base3=[F(2),F(3),F(7),F(9),F(6)]  # free=[w2,w3,w4,w5,w6]; w4=7 at t=0; w2^2+w3^2+w6^2=4+9+36=49
    d3,order3,cnt3,deg3=jump_order(base3, 2, 3, F(7), F(9), F(0))
    print(f"  pts={cnt3}  per-side poly deg={deg3}  jump order at wall = {order3}",flush=True)
