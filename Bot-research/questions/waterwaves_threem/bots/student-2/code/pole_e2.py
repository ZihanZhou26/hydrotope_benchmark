#!/usr/bin/env python3
"""Does A_6 blow up where e2(plus)=w4 w5 + w4 w6 + w5 w6 = 0 (the same-type
triple-propagator denominator)?  Group only tested D_S=0 channels and |k_S|=0
walls; e2=0 was never checked.  Scan a 1-D manifold family, watch e2(plus) cross
zero, and see if |A_6| diverges (genuine pole) or stays finite (cancels)."""
from fractions import Fraction as Fr
import harness as h

SIG=[-1,-1,-1,1,1,1]
def e2(vals):
    w=[None]+[float(x) for x in vals]
    return w[4]*w[5]+w[4]*w[6]+w[5]*w[6]
def e2m(vals):
    w=[None]+[float(x) for x in vals]
    return w[1]*w[2]+w[1]*w[3]+w[2]*w[3]

# vary w5; keep w2=2,w3=3,w4=5.  Scan to find e2(plus) sign change.
prev=None
print("scanning w5; reporting e2(plus), e2(minus), A_6 (double):")
w5=Fr(1)
hits=[]
for k in range(1,400):
    w5=Fr(k,20)   # 0.05 .. 19.95
    try:
        im,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5),w5], SIG, double=True)
    except Exception:
        continue
    e=e2(oms); em=e2m(oms)
    if prev is not None and prev[1]*e<0:
        hits.append((prev,(float(w5),e,em,im)))
    prev=(float(w5),e,em,im)

for (w5a,ea,ema,ia),(w5b,eb,emb,ib) in hits:
    print(f"  e2(plus) crosses 0 between w5={w5a:.3f}(e2={ea:.4g},A={ia:.5g}) and "
          f"w5={w5b:.3f}(e2={eb:.4g},A={ib:.5g})")
    # zoom near the crossing with exact arithmetic
    lo,hi=Fr(int(w5a*20),20),Fr(int(w5b*20)+1,20)
    for j in range(1,10):
        w5z=lo+(hi-lo)*Fr(j,10)
        try:
            imz,omsz,_=h.on_shell([Fr(2),Fr(3),Fr(5),w5z], SIG, double=True)
            print(f"     w5={float(w5z):.5f}: e2(plus)={e2(omsz):+.5g}  e2(minus)={e2m(omsz):+.5g}  A_6={imz:.6g}")
        except Exception:
            print(f"     w5={float(w5z):.5f}: SIGFPE")
if not hits:
    print("  no e2(plus) sign change in scanned range")
