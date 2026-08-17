#!/usr/bin/env python3
"""Determine the R_spline jump ORDER across Q_T=0 exactly (root multiplicity of
J(t) at t0), and confirm it is a systematic S3xS3 ORBIT by testing several
independent on-shell lines each crossing a DIFFERENT single Q_{m;pq} channel."""
from fractions import Fraction as F
from r4_verify import R_spline, SIG, _fmt, M, P
from r4_line_test import nullspace, omega_of_t, word_of, poly_fit, poly_eval
from r4_line_test3 import gen_dirs, find_base, order_changes, qt_roots
import itertools

def poly_mul(a,b):
    r=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            r[i+j]+=x*y
    return r
def poly_sub(a,b):
    n=max(len(a),len(b)); a=a+[F(0)]*(n-len(a)); b=b+[F(0)]*(n-len(b))
    return [a[i]-b[i] for i in range(n)]
def root_mult(coeffs,t0):
    """multiplicity of root t0 in polynomial coeffs (list c0..cn)."""
    c=coeffs[:]
    m=0
    while c and all(x==0 for x in c)==False:
        # evaluate at t0
        val=sum(c[j]*t0**j for j in range(len(c)))
        if val!=0: break
        m+=1
        # derivative
        c=[c[j]*j for j in range(1,len(c))]
        if not c: break
    return m

def test_line(Pt,d,t0,ch,lo,hi,label):
    span=hi-lo; Ns=13
    ts=[lo+span*F(k,2*Ns) for k in range(1,2*Ns) if lo+span*F(k,2*Ns)!=t0]
    left=[t for t in ts if t<t0]; right=[t for t in ts if t>t0]
    o0=word_of(omega_of_t(Pt,d,ts[0]))
    for t in ts:
        if word_of(omega_of_t(Pt,d,t))!=o0: return None
    if len(left)<9 or len(right)<9: return None
    RS={t:R_spline(omega_of_t(Pt,d,t)) for t in ts}
    cL=poly_fit(left[:9],[RS[t] for t in left[:9]],8)
    if not all(poly_eval(cL,t)==RS[t] for t in left[9:]): return None   # left control
    cR=poly_fit(right[:9],[RS[t] for t in right[:9]],8)
    if not all(poly_eval(cR,t)==RS[t] for t in right[9:]): return None  # right control
    J=poly_sub(cR,cL)             # right poly - left poly (degree<=8)
    if all(x==0 for x in J):
        return (label,ch,0,None)  # no jump
    mult=root_mult(J,t0)
    # leading coefficient of J/(t-t0)^mult at t0 (the "brick" value on this line)
    Jd=J[:]
    for _ in range(mult):
        Jd=[Jd[j]*j for j in range(1,len(Jd))]
    lead=sum(Jd[j]*t0**j for j in range(len(Jd)))
    import math
    lead=lead/F(math.factorial(mult))
    return (label,ch,mult,lead)

if __name__=="__main__":
    # line 1 (the one already used)
    Pt1=[F(8),F(2),F(-3),F(-5),F(4),F(-6)]; d1=[F(-2),F(1),F(0),F(2),F(-1),F(0)]
    r=test_line(Pt1,d1,F(1,4),(0,(3,5)),F(-1,2),F(1),"line1")
    print("line1:",r, " channel Q_{m=leg%d; p,q=leg%d,leg%d}"%(r[1][0]+1,r[1][1][0]+1,r[1][1][1]+1))

    # search several more distinct lines crossing different channels
    dirs=gen_dirs(box=5)
    found_channels={}
    count=0
    for d in dirs:
        Pt=find_base(d,box=6)
        if Pt is None: continue
        oc=order_changes(Pt,d); qr=qt_roots(Pt,d)
        for (t0,ch) in qr:
            lo=max([t for t in oc if t<t0],default=None)
            hi=min([t for t in oc if t>t0],default=None)
            if lo is None or hi is None: continue
            if any(lo<t<hi and t!=t0 for (t,c) in qr): continue
            if not (lo<t0<hi): continue
            res=test_line(Pt,d,t0,ch,lo,hi,f"d={[int(x) for x in d]}")
            if res is None: continue
            lbl,cch,mult,lead=res
            key=(cch[0],cch[1])
            if key in found_channels: continue
            found_channels[key]=(mult,lead)
            print(f"  channel Q_(m=leg{cch[0]+1};{cch[1][0]+1},{cch[1][1]+1}): jump order in (t-t0) = {mult}, lead={_fmt(lead) if lead is not None else None}   [{lbl}, t0={_fmt(t0)}]")
            count+=1
        if count>=8: break
    print(f"\nDistinct Q-channels exhibiting an R_spline jump: {len(found_channels)}")
    orders=set(v[0] for v in found_channels.values())
    print("jump orders observed:",sorted(orders))
    print("=> R_spline jumps across the Q_{m;pq}=0 (3-leg k_S=0) walls as a systematic orbit"
          if len(found_channels)>=3 else "=> insufficient orbit coverage")
