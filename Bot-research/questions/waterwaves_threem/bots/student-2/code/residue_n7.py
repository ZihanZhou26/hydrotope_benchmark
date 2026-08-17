#!/usr/bin/env python3
"""NEW n=7 handle: residue of A_7 at a SINGLE mixed-pair wall {w_i+w_j=0}.
At n=7 one pair vanishes alone (n7_geom) -> Res = lim (w_i+w_j) A_7 accessible by a
1-param limit (impossible at n=6: triple collision). Recognize the residue structure."""
import sympy as sp, itertools
from fractions import Fraction as F
import harness as h
from n7_mindenom import collect, Dfree_val, Qr
t=sp.Symbol('t'); M=(1,2,3); P=(4,5,6,7)

pts=collect(7,M,P,[F(2),F(3),F(5),F(0),F(0)],F(7),F(11),3,4,step=F(1,20),maxk=24)
print(f"chamber-A slice points: {len(pts)}")
xs=[Qr(tv) for (tv,_,_) in pts]
Nv=[Qr(im)*Dfree_val(oms,M,P) for (_,im,oms) in pts]
Nfull=sp.Poly(sp.interpolate(list(zip(xs,Nv)),t),t)
def omp(a):  # omega_a(t) as poly
    return sp.Poly(sp.interpolate(list(zip(xs,[Qr(o[a-1]) for (_,_,o) in pts])),t),t)
OM={a:omp(a) for a in range(1,8)}
def pairp(i,j): return sp.Poly(OM[i].as_expr()+OM[j].as_expr(),t)

print("\nResidues at single-pair walls (linear factors -> rational t0):")
for i in M:
    for j in P:
        pf=pairp(i,j)
        if pf.degree()!=1: continue
        t0=sp.Rational(-pf.nth(0),pf.nth(1))
        R=sp.Integer(1)
        for a in M:
            for b in P:
                if (a,b)!=(i,j): R*=pairp(a,b).eval(t0)
        res=sp.Rational(Nfull.eval(t0))/R
        w={a:OM[a].eval(t0) for a in range(1,8)}
        rm=[a for a in M if a!=i]; rp=[b for b in P if b!=j]
        a,b=rm
        beta2=min(w[a]**2,w[b]**2); tot=F(0)
        for r in range(len(rp)+1):
            for S in itertools.combinations(rp,r):
                v=F(beta2)-sum(F(w[s])**2 for s in S)
                if v>0: tot+=F((-1)**r)*v**2
        A2m=F(16)*F(w[a])*F(w[b])*tot
        print(f"  {{{i}+{j}=0}} t0={t0}: Res/i={res}")
        print(f"     rem minus {rm}={[w[a] for a in rm]} plus {rp}={[w[b] for b in rp]}")
        print(f"     2minus-5pt(rem)={A2m}  Res/2m={sp.nsimplify(sp.Rational(res)/sp.Rational(A2m)) if A2m else 'inf'}")
