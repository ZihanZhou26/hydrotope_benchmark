#!/usr/bin/env python3
"""Fast n=7 jump-EXPONENT probe (float). A_7 is analytic on each side of a difference-branch
wall (denominator smooth there); the kink exponent = order of first discontinuous derivative.
Fit a local polynomial (float) each side near t* and compare Taylor coefficients.
"""
import numpy as np, subprocess, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); BG=os.path.join(HERE,"bg")
SIG7="-1,-1,-1,1,1,1,1"
def A7d(free):
    cmd=[BG,"--double","-n","7","-w",",".join(str(F(x)) for x in free),"-s",SIG7,"-g","1"]
    out=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout.decode()
    import re
    m=re.search(r"A_7 \(double\) = ([-0-9.eE+]+) \+ ([-0-9.eE+]+) i",out)
    return float(m.group(2)) if m else None

def kink_exponent(base, iv, ic, A0, B0, tstar, h=2e-3, K=9, deg=7):
    def side(sgn):
        ts=[]; vs=[]
        for k in range(1,K+1):
            tt=tstar+sgn*h*k
            free=list(base); free[iv]=A0+tt; free[ic]=B0-tt
            v=A7d([F(x).limit_denominator(10**9)+0 for x in free]) if False else A7d([float(x)+sgn*0 for x in []] or _f(free,iv,ic,A0,B0,tt))
            if v is None: return None,None
            ts.append(tt); vs.append(v)
        return np.array(ts), np.array(vs)
    def _f(base,iv,ic,A0,B0,tt):
        free=list(map(float,base)); free[iv]=float(A0)+tt; free[ic]=float(B0)-tt; return free
    # local fit each side: shift by tstar, fit poly in (t-tstar)
    out={}
    cof={}
    for sgn,name in [(-1,'L'),(1,'R')]:
        ts=[]; vs=[]
        for k in range(1,K+1):
            tt=tstar+sgn*h*k
            free=list(map(float,base)); free[iv]=float(A0)+tt; free[ic]=float(B0)-tt
            v=A7d(free)
            if v is None: continue
            ts.append(tt-tstar); vs.append(v)
        c=np.polyfit(ts,vs,deg)[::-1]   # low->high coeffs of (t-tstar)
        cof[name]=c
    dL,dR=cof['L'],cof['R']
    # compare coefficients order by order; first order with relative diff > tol = exponent
    for e in range(deg+1):
        a,b=dL[e],dR[e]
        scale=max(abs(a),abs(b),1e-30)
        if abs(a-b)/scale>1e-4:
            return e,(a,b)
    return None,(dL,dR)

if __name__=="__main__":
    # (1=1): w2=3,w3=5,w4->3, vary w4(idx2) compensate w5(idx3)
    e1,info=kink_exponent([3,5,3,8,5.5],2,3,3.0,8.0,0.0)
    print(f"(1=1) wall {{a2=b4}}: kink exponent = {e1}")
    # (1=2): w2=3,w3=4,w4->5
    e2,_=kink_exponent([3,4,5,9,6.5],2,3,5.0,9.0,0.0)
    print(f"(1=2) wall {{a4=a2+a3 i.e. w4^2=w2^2+w3^2}}: kink exponent = {e2}")
    # (1=3): w2=2,w3=3,w6=6,w4->7 (4+9+36=49)
    e3,_=kink_exponent([2,3,7,9,6],2,3,7.0,9.0,0.0)
    print(f"(1=3) wall {{w4^2=w2^2+w3^2+w6^2}}: kink exponent = {e3}")
