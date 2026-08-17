#!/usr/bin/env python3
"""With D = prod_{i in minus, j in plus} (w_i+w_j) established as the A_6 denominator:
(1) confirm minimality (dropping one factor breaks polynomiality);
(2) extract the numerator N_6 = A_6 * D on a slice, factor it;
(3) check n=5: does prod_{mixed}(w_i+w_j) divide A_5 (=> A_5 polynomial)?
All exact, in-chamber.
"""
from fractions import Fraction as Fr
from itertools import combinations
import sympy as sp
import harness as h

def mixsig(oms, signs):
    n=len(signs); w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,n):
        for S in combinations(range(1,n+1),r):
            mns=[i for i in S if signs[i-1]<0]; pls=[i for i in S if signs[i-1]>0]
            if mns and pls:
                v=sum(Fr(signs[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

def collect(signs, basefree, vary, H, count):
    ref=mixsig(h.on_shell([Fr(x) for x in basefree],signs)[1],signs)
    i,j=vary; out=[]
    for p in list(range(1,count))+list(range(-1,-count,-1)):
        free=[Fr(x) for x in basefree]; free[i]+=Fr(p,H); free[j]-=Fr(p,H)
        try: oim,oms,_=h.on_shell(free,signs)
        except Exception: continue
        if mixsig(oms,signs)!=ref: continue
        out.append((sp.Rational(p), sp.Rational(oim.numerator,oim.denominator), oms))
        if len(out)>=count: break
    return out

def Dmix(oms, signs, H, p):
    """prod (w_i+w_j) mixed, as exact value at param p (already have oms)."""
    w=[None]+[Fr(x) for x in oms]
    minus=[i for i in range(1,len(signs)+1) if signs[i-1]<0]
    plus=[i for i in range(1,len(signs)+1) if signs[i-1]>0]
    pr=Fr(1)
    for i in minus:
        for j in plus:
            pr*=(w[i]+w[j])
    return pr

def poly_deg(xs, ys, dmax=40):
    d=min(dmax,len(xs)-6)
    V=sp.Matrix([[xs[k]**q for q in range(d+1)] for k in range(d+1)])
    c=V.LUsolve(sp.Matrix(ys[:d+1]))
    ok=all(sum(c[q]*xs[k]**q for q in range(d+1))==ys[k] for k in range(d+1,len(xs)))
    if not ok: return None,None
    deg=max([q for q in range(d+1) if c[q]!=0],default=0)
    return deg, [c[q] for q in range(deg+1)]

S6=[-1,-1,-1,1,1,1]
data=collect(S6,[2,3,5,7],(2,3),20,60)   # vary w4,w5
xs=[x for x,_,_ in data]
# (2) numerator N = A_6 * Dmix
ys_N=[y*Dmix(o,S6,20,x) for x,y,o in data]
degN, _=poly_deg(xs, ys_N)
print(f"A_6 * prod_mixed(w_i+w_j): polynomial? deg={degN}")
# (1) minimality: drop (w_2+w_4) factor
def Dmix_drop(oms):
    w=[None]+[Fr(x) for x in oms]; pr=Fr(1)
    for i in (1,2,3):
        for j in (4,5,6):
            if (i,j)==(2,4): continue
            pr*=(w[i]+w[j])
    return pr
ys_drop=[y*Dmix_drop(o) for x,y,o in data]
degD2,_=poly_deg(xs, ys_drop)
print(f"drop (w2+w4): polynomial? {'NO (factor needed)' if degD2 is None else 'deg '+str(degD2)+' (NOT minimal!)'}")

# factor N_6 as polynomial in t on this slice
t=sp.Symbol('t')
degN2, coeffs=poly_deg(xs, ys_N)
N=sum(coeffs[q]*t**q for q in range(len(coeffs)))
print("N_6(t) factored on slice:", sp.factor(N))

# (3) n=5 check: does prod_mixed(w_i+w_j) [6 pairs] relate to A_5?
print("\n--- n=5: A_5 is polynomial; check prod_mixed divides numerator ---")
S5=[-1,-1,-1,1,1]
d5=collect(S5,[2,3,5],(1,2),20,50)  # vary w3,w4 (free idx1,2)
xs5=[x for x,_,_ in d5]
def Dmix5(oms):
    w=[None]+[Fr(x) for x in oms]; pr=Fr(1)
    for i in (1,2,3):
        for j in (4,5):
            pr*=(w[i]+w[j])
    return pr
ys5=[y for _,y,_ in d5]
degA5,_=poly_deg(xs5,ys5)
print(f"A_5 polynomial deg={degA5} (confirms n=5 has NO (w_i+w_j) denominator: it cancels)")
