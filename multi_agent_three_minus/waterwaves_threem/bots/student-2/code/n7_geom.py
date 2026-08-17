#!/usr/bin/env python3
"""Geometric reason there is NO n=6-style collapse at n=7: a SINGLE mixed pair can
vanish ALONE on the manifold (so the 12 sum-branch walls are DISTINCT codim-1 loci).
Contrast: at n=6 one pair vanishing forces a full perfect matching (s2_011), so all
9 sum-walls coincide on the single hypersurface {e3m+e3p=0}.  No oracle needed."""
import sympy as sp
M=(1,2,3)

def check_point(oms, n, plus):
    sumc=sum(oms)
    sig=sum((-1 if (k+1) in M else 1)*oms[k]**2 for k in range(n))
    pairs0=[(i,j) for i in M for j in plus if sp.simplify(oms[i-1]+oms[j-1])==0]
    return sp.simplify(sumc), sp.simplify(sig), pairs0

print("=== n=7: exhibit w1+w4=0 with NO other mixed pair zero ===")
# w1=-w4=-5; minus w2=3,w3=8. plus trio w5,w6,w7: sum=-(3+8)=-11, sumsq=9+64=73.
# w5=-2 => w6+w7=-9, w6w7=6 => w6,w7 = roots of z^2+9z+6.
w1,w2,w3,w4=sp.Integer(-5),sp.Integer(3),sp.Integer(8),sp.Integer(5)
w5=sp.Integer(-2)
w6=(-9+sp.sqrt(57))/2; w7=(-9-sp.sqrt(57))/2
oms=[w1,w2,w3,w4,w5,w6,w7]
sc,sg,p0=check_point(oms,7,(4,5,6,7))
print(f"  omega = {oms}")
print(f"  sum omega={sc}, sum sigma omega^2={sg}  (both 0 => on manifold)")
print(f"  vanishing mixed pairs: {p0}")
print(f"  => exactly ONE pair (1,4) vanishes; 11 others nonzero: {p0==[(1,4)]}")

print("\n=== n=6 contrast: impose w1+w4=0, show it FORCES a full matching ===")
# n=6 manifold: 3 minus (1,2,3), 3 plus (4,5,6). Set w1+w4=0 and solve.
w1s,w2s,w3s,w4s,w5s,w6s=sp.symbols('w1 w2 w3 w4 w5 w6',real=True)
eqs=[w1s+w2s+w3s+w4s+w5s+w6s,
     -w1s**2-w2s**2-w3s**2+w4s**2+w5s**2+w6s**2,
     w1s+w4s]  # impose pair (1,4)=0
# free choose w2,w3,w5 ; solve w1(=-w4),w4,w6 ? Use a concrete generic slice:
# substitute w2=3,w3=8 wait keep symbolic minus; pick w5 param, solve.
sol=sp.solve([e.subs({w2s:3,w3s:8,w5s:-2}) for e in eqs],[w1s,w4s,w6s],dict=True)
for srec in sol:
    w=[srec[w1s],sp.Integer(3),sp.Integer(8),srec[w4s],sp.Integer(-2),srec[w6s]]
    p0=[(i,j) for i in M for j in (4,5,6) if sp.simplify(w[i-1]+w[j-1])==0]
    e3m=w[0]*w[1]*w[2]; e3p=w[3]*w[4]*w[5]
    print(f"  solution omega={[sp.nsimplify(x) for x in w]}")
    print(f"    vanishing pairs: {p0};  e3m+e3p={sp.simplify(e3m+e3p)} (=0 => matching locus)")
