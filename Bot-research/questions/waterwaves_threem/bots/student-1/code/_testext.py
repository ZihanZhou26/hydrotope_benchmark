from fractions import Fraction as F
import sympy as sp, r5_walls as W
t=W.t
# A clean (1=2) crossing, vary span to find when fit stabilizes
w2,w3,a,b=F(3),F(11,2),F(9,2),F(15,2)
crs=W.find_crossings(w2,w3,a,b,F(1,40),F(6))
for (lo,hi,key) in crs:
    if key[0]!='2': continue
    for span in (14,20,28):
        r=W.extract_bracket(w2,w3,a,b,lo,hi,key,F(1,120),span)
        if r[0]=='fitfail': print(f"  {key} span{span}: FITFAIL {r[2:]}"); continue
        kk,jump,kp,coef,isp=r
        print(f"  {key} span{span}: ok={isp} jump_deg={sp.degree(jump,t)} coef_deg={sp.degree(coef,t) if isp else '-'}")
    break
