#!/usr/bin/env python3
"""ROUND 7 (student-2, top-down): IDENTIFY the n=7 single-pair residue exactly.

At n>=7 a single mixed pair {w_i+w_j=0} vanishes ALONE (s2_019), so
   Res_{ij} := lim_{w_i+w_j->0} (w_i+w_j) * A_n
is accessible by a 1-parameter on-shell limit. We extract it EXACTLY (no float)
and try to recognize it.

Method: slice with w_j = t, other free legs fixed; A_7(t) = N(t)/Dfree(t) with
N(t)=A_7*Dfree polynomial on the slice (Dfree clears the denominator).
Res = lim (w_i+w_j) A_7 = N(t0)/prod_{(a,b)!=(i,j)}(w_a+w_b)(t0),  t0 where w_i+w_j=0.
"""
import sympy as sp, itertools
from fractions import Fraction as F
import harness as h
t=sp.Symbol('t')
def Qr(x): return sp.Rational(x.numerator,x.denominator)

def msubs_of(n,M,P):
    out=[]
    for r in range(1,n):
        for S in itertools.combinations(range(1,n+1),r):
            if any(i in M for i in S) and any(i in P for i in S): out.append(S)
    return out

def csig(oms,n,M,ms):
    w={i+1:oms[i] for i in range(n)}
    out=[]
    for S in ms:
        kk=sum((-1 if i in M else 1)*w[i]**2 for i in S)
        out.append(1 if kk>0 else (-1 if kk<0 else 0))
    return tuple(out)

def slice_pts(n,M,P,free_tmpl,ivar,vmin_step,maxk=40):
    """Vary free[ivar] = base + k*step (both directions); collect in-chamber pts."""
    SIG=[-1 if (i+1) in M else 1 for i in range(n)]
    ms=msubs_of(n,M,P); pts=[]; s0=None
    base=free_tmpl[ivar]
    for d in (1,-1):
        for k in range(0 if d==1 else 1,maxk):
            tv=base+d*vmin_step*k
            free=list(free_tmpl); free[ivar]=tv
            if sum(free)==0: continue
            try: im,oms,rep=h.on_shell([str(x) for x in free],SIG)
            except Exception: break
            if rep!=0: continue
            oms=[F(o) for o in oms]; s=csig(oms,n,M,ms)
            if 0 in s: continue
            if s0 is None: s0=s
            if s!=s0: break
            pts.append((tv,F(im),oms))
    return pts,s0

def Dfree(oms,M,P):
    w={i+1:Qr(oms[i]) for i in range(len(oms))}
    D=sp.Integer(1)
    for i in M:
        for j in P: D*=(w[i]+w[j])
    return D

def residue_pair(n,M,P,free_tmpl,ivar,iminus,jplus,step=F(1,12)):
    """Extract Res at wall {w_iminus + w_jplus = 0} on a slice varying free[ivar]."""
    pts,s0=slice_pts(n,M,P,free_tmpl,ivar,step)
    if len(pts)<30: return None
    xs=[Qr(tv) for (tv,_,_) in pts]
    Nv=[Qr(im)*Dfree(oms,M,P) for (_,im,oms) in pts]
    half=len(pts)*2//3
    Np=sp.Poly(sp.interpolate(list(zip(xs[:half],Nv[:half])),t),t)
    if not all(Np.eval(xs[i])==Nv[i] for i in range(half,len(pts))):
        return None  # not polynomial -> bad slice
    OM={a:sp.Poly(sp.interpolate(list(zip(xs,[Qr(o[a-1]) for (_,_,o) in pts])),t),t)
        for a in range(1,n+1)}
    pf=sp.Poly(OM[iminus].as_expr()+OM[jplus].as_expr(),t)
    if pf.degree()!=1: return None
    t0=sp.Rational(-pf.nth(0),pf.nth(1))
    R=sp.Integer(1)
    for a in M:
        for b in P:
            if (a,b)!=(iminus,jplus): R*=sp.Poly(OM[a].as_expr()+OM[b].as_expr(),t).eval(t0)
    res=sp.Rational(Np.eval(t0))/R
    w={a:OM[a].eval(t0) for a in range(1,n+1)}
    return res, {a:F(w[a]) for a in range(1,n+1)}, s0

def two_minus(minus_legs, w, n5_exp):
    """5pt+ two-minus amplitude A/i = 16 w_a w_b sum_S (-1)^|S|(min(wa^2,wb^2)-sumS)_+^exp.
    Here generic n: A^{2-}/i = 2^{n-1} g^{3-n} w_a w_b sum ... exp=n-3."""
    a,b=minus_legs
    others=[k for k in w if k not in minus_legs]
    beta2=min(w[a]**2,w[b]**2)
    tot=F(0)
    for r in range(len(others)+1):
        for S in itertools.combinations(others,r):
            v=beta2-sum(w[s]**2 for s in S)
            if v>0: tot+=F((-1)**r)*v**n5_exp
    return w[a]*w[b]*tot

if __name__=="__main__":
    n=7; M=(1,2,3); P=(4,5,6,7)
    # Drive pair (minus 2, plus 4): vary free[2] = w4. Fixed w2,w3,w5,w6.
    # free template positions: [w2,w3,w4,w5,w6]; ivar=2 is w4.
    print("=== Residue at pair (minus 2, plus 4): vary w4, others fixed ===")
    configs=[
        [F(2),F(3),F(5),F(7),F(11)],   # base
        [F(2),F(3),F(5),F(8),F(11)],
        [F(2),F(3),F(5),F(7),F(13)],
        [F(5,2),F(3),F(5),F(7),F(11)],
    ]
    for fr in configs:
        out=residue_pair(n,M,P,fr,2,2,4)
        if out is None: print(f"  cfg {fr}: bad slice"); continue
        res,w,s0=out
        # surviving: minus {1,3}, plus {5,6,7}; merged scale w2=-w4
        A2m=two_minus((1,3),w,2)   # n5-style exp=2 (two-minus 5pt is exp 2)
        ratio=sp.nsimplify(sp.Rational(res)/sp.Rational(F(16)*A2m)) if A2m!=0 else 'inf'
        print(f"  w(wall)= 1:{w[1]} 2:{w[2]} 3:{w[3]} 4:{w[4]} 5:{w[5]} 6:{w[6]} 7:{w[7]}")
        print(f"    Res/i = {res}")
        print(f"    16*A2m(min13) = {F(16)*A2m}   Res/(16A2m) = {ratio}")
