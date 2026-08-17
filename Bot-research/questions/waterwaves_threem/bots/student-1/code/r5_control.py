#!/usr/bin/env python3
"""CONTROL: synthetic SIMPLE (1=1) spline must fit CONSISTENT with the M-fit machinery.
Mtest(o) = sum_{9 (1=1) walls} |w_j^2-w_i^2| * tmpl(relabel(i,j) o)  for a fixed template tmpl.
If machinery is sound -> CONSISTENT. (Validates that the real-M inconsistency is genuine.)"""
from fractions import Fraction as F
import random
import chambers_n6 as cn, r5_group as Gp, r5_basis as B, r5_global as G2
PR=2**61-1
def minv(a): return pow(a%PR,PR-2,PR)
def fm(fr): return (fr.numerator%PR)*minv(fr.denominator%PR)%PR
M=[0,1,2]; P=[3,4,5]; W11=[(i,j) for i in M for j in P]
PERM={(i,j):Gp.relabel_11_to_ref(i,j) for (i,j) in W11}
gdeg=(1,1,1,2,1,2)
monsP,_=B.independent_subset(B.hinv_mons(9,gdeg),'P')
baseC=G2.base_classes()
# pick a synthetic template = a couple of monomials
tmpl=[monsP[0],monsP[5],monsP[20]]; tco=[F(2),F(-3),F(1)]
def Mtest(o):
    s=F(0)
    for (i,j) in W11:
        k=abs(o[j]**2-o[i]**2)
        if k!=0:
            ro=Gp.apply_perm(PERM[(i,j)],o)
            s+= k*sum(c*B.eval_h(m,ro,'P') for c,m in zip(tco,tmpl))
    return s
def phi11(m,o):
    s=F(0)
    for (i,j) in W11:
        k=abs(o[j]**2-o[i]**2)
        if k!=0: s+= k*B.eval_h(m,Gp.apply_perm(PERM[(i,j)],o),'P')
    return s
def cols(o): return [G2.eval_base(cl,o) for cl in baseC]+[phi11(m,o) for m in monsP]
ncol=len(baseC)+len(monsP)
rnd=random.Random(5); data=[]
while len(data)<ncol+40:
    free=[F(rnd.randint(-90,90),10) for _ in range(4)]
    if 0 in free: continue
    o=cn.solve_squares(free)
    if o is None or any(w==0 for w in o): continue
    data.append((o,Mtest(o)))
rows=[[fm(x) for x in cols(o)] for (o,_) in data]; rhs=[fm(v) for (_,v) in data]
nrow=len(rows)
Mx=[rows[i][:]+[rhs[i]] for i in range(nrow)]; piv=[]; r=0
for c in range(ncol):
    p=next((i for i in range(r,nrow) if Mx[i][c]%PR!=0),None)
    if p is None: continue
    Mx[r],Mx[p]=Mx[p],Mx[r]; iv=minv(Mx[r][c]); Mx[r]=[(x*iv)%PR for x in Mx[r]]
    for i in range(nrow):
        if i!=r and Mx[i][c]%PR!=0:
            f=Mx[i][c]; Mx[i]=[(Mx[i][k]-f*Mx[r][k])%PR for k in range(ncol+1)]
    piv.append(c); r+=1
    if r==nrow: break
incons=any(Mx[i][ncol]%PR!=0 and all(Mx[i][k]%PR==0 for k in range(ncol)) for i in range(r,nrow))
print(f"CONTROL synthetic simple (1=1) spline: rank {r}, CONSISTENT={not incons} (expect True)")
