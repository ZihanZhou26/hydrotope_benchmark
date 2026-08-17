"""Scan a_n along a 1-parameter on-shell family (vary one free freq) and fit
a rational function in that parameter to expose degree, numerator, poles.
"""
import sympy as sp
import bgio

def scan(n, base_freew, vary_idx, tvals):
    """base_freew: list of n-2 free freqs; replace entry vary_idx by t."""
    t=sp.symbols('t')
    pts=[]
    full=[]
    for tv in tvals:
        fw=list(base_freew); fw[vary_idx]=tv
        r=bgio.onshell(n, fw)
        if not r["ok"]:
            continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        pts.append((sp.Rational(tv) if not isinstance(tv,sp.Rational) else tv, a))
        full.append((fw, [sp.Rational(x.numerator,x.denominator) for x in r["omega"]], a))
    return pts, full

def rational_fit(pts, t, maxden=4):
    """Try to fit a rational function P(t)/Q(t) with small denominator degree."""
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    N=len(pts)
    for dq in range(0, maxden+1):
        dp = N-1-dq   # so total unknowns = (dp+1)+(dq) = N (Q monic-ish: set Q const=1)
        if dp<0: continue
        pcoef=sp.symbols(f'p0:{dp+1}')
        qcoef=sp.symbols(f'q1:{dq+1}')  # q0=1
        P=sum(pcoef[i]*t**i for i in range(dp+1))
        Q=sp.Integer(1)+sum(qcoef[i]*t**(i+1) for i in range(dq))
        eqs=[ (P - y*Q).subs(t,x) for x,y in zip(xs,ys)]
        sol=sp.solve(eqs, list(pcoef)+list(qcoef), dict=True)
        if sol:
            Pf=P.subs(sol[0]); Qf=Q.subs(sol[0])
            expr=sp.simplify(Pf/Qf)
            # verify on all points
            if all(sp.simplify(expr.subs(t,x)-y)==0 for x,y in zip(xs,ys)):
                return expr, dp, dq
    return None, None, None

if __name__=="__main__":
    t=sp.symbols('t')
    # n=5, vary the LAST free freq (a plus leg, omega_4)
    tvals=[sp.Rational(k) for k in (3,4,5,6,7,8,9,10,11,12,13,14)]
    pts, full = scan(5,[1,2,3],2,tvals)
    print("n=5 vary omega_4 (plus leg), omega_2=1,omega_3=2:")
    for (fw,om,a) in full[:6]:
        print("   t=",fw[2]," omega=",om," a=",a)
    expr,dp,dq=rational_fit(pts,t)
    print("  fit P/Q degrees (numer,denom)=",dp,dq)
    print("  a_5(t)=", expr)
    if expr is not None:
        print("  factored:", sp.factor(expr))
