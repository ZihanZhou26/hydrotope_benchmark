import sys
from fractions import Fraction as F
import sympy as sp
from collectlib import *
import inv
def pr(*a): print(*a, flush=True)

def ee(oms): e=inv.invariants(oms); return e[2]+e[3]

pr("(A) minimal-denom confirm (A_6*(e3m+e3p) -> pure sumFree denom):")
for base in [[F(2),F(3),F(5),F(7)],[F(-3),F(2),F(4),F(-5)],[F(3),F(-7,2),F(5,2),F(-4)]]:
    for vary in (4,5,2):
        pts,_=collect_contig(base,vary, lambda tt,oms,im: im*ee(oms))
        res=reconstruct(pts)
        if res is None: pr(f"  base {base} w{vary}: recon fail ({len(pts)}pts)"); continue
        dN,dD,Nc,Dc=res
        Dpoly=poly(Dc); sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
        pure=sp.simplify(Dpoly/sumF**dD)
        pr(f"  base {base} w{vary}: degN={dN} degD={dD} pureSF={bool(pure.is_number and pure!=0)} ({len(pts)}pts)")

pr("\n(B) factor numerator N along anchor [2,3,5,7], vary w4:")
base=[F(2),F(3),F(5),F(7)]
pts,_=collect_contig(base,4, lambda tt,oms,im: im*ee(oms))
res=reconstruct(pts); dN,dD,Nc,Dc=res
pr(f"  degN={dN} degD={dD}, npts={len(pts)}")
Npoly=poly(Nc); Dpoly=poly(Dc)
sf0=sum(base); sumF=sp.Rational(sf0.numerator,sf0.denominator)+t
pr(f"  D(t)/sumFree^{dD} = {sp.simplify(Dpoly/sumF**dD)}")
pr("  N(t) factored:"); sp.pprint(sp.factor(Npoly))
# wall roots
w2,w3,w5=sp.Integer(2),sp.Integer(3),sp.Integer(7); w4=sp.Integer(5)+t
sF=w2+w3+w4+w5; sSig=-w2**2-w3**2+w4**2+w5**2
w6=-(-sF**2+sSig)/(-2*sF); w1=-(sF+w6)
wsq={1:sp.cancel(w1**2),2:sp.Integer(4),3:sp.Integer(9),4:w4**2,5:sp.Integer(49),6:sp.cancel(w6**2)}
pr("  mixed (1=1) wall fn roots (k_ij=w_j^2-w_i^2):")
for i in (1,2,3):
    for j in (4,5,6):
        nn,_=sp.fraction(sp.cancel(wsq[j]-wsq[i]))
        pr(f"    k_{i}{j}: {sp.solve(nn,t)}")
pr("  (1=2) wall fn roots (w_i^2 - w_j^2 - w_k^2):")
for i in (1,2,3):
    for (j,k) in [(4,5),(4,6),(5,6)]:
        nn,_=sp.fraction(sp.cancel(wsq[i]-wsq[j]-wsq[k]))
        pr(f"    {i}-{j}{k}: {sp.solve(nn,t)}")
