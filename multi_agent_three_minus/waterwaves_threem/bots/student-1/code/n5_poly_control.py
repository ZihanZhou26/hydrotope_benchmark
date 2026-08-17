# Validate the poly-vs-rational test on n=5 (KNOWN polynomial: A5=2^4 w4 w5 P(w^2)).
# If A5*sumFree^p IS polynomial for some p<=6 (full chamber), the method is sound,
# and the n=6 'rational' conclusion (no such p) is real.
from fractions import Fraction as F
import harness as h, chambers_n6 as cn
from exactfit import exact_solve
SIG5=[-1,-1,-1,1,1]
def solve5(free):
    free=[F(x) for x in free]; sumF=sum(free)
    if sumF==0: return None
    sumSig=-free[0]**2-free[1]**2+free[2]**2
    w5=-((-1)*sumF**2+sumSig)/(2*(-1)*sumF); w1=-(sumF+w5)
    return [w1,free[0],free[1],free[2],w5]
def fullsig5(oms):
    a=[oms[0]**2,oms[1]**2,oms[2]**2]; b=[oms[3]**2,oms[4]**2]
    s=[]
    for i in range(3):
        for j in range(2):
            v=a[i]-b[j]
            if v==0: return None
            s.append(1 if v>0 else -1)
    # same-type orderings
    if 0 in [a[0]-a[1],a[0]-a[2],a[1]-a[2],b[0]-b[1]]: return None
    sa=tuple(1 if a[i]>a[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    sb=(1 if b[0]>b[1] else -1,)
    return tuple(s)+sa+sb
# slice: free=(w2,w3,w4), vary w4
import random
rnd=random.Random(5); base=None
for _ in range(3000):
    f0=tuple(F(rnd.randint(-40,40),10) for _ in range(3))
    if any(x==0 for x in f0): continue
    o=solve5(f0)
    if o is None or any(w==0 for w in o): continue
    s0=fullsig5(o)
    if s0 is None: continue
    # count slice pts varying w4
    pts=[]
    for k in range(-30,31):
        t=F(k,60); free=(f0[0],f0[1],f0[2]+t)
        oo=solve5(free)
        if oo is None or any(w==0 for w in oo): continue
        if fullsig5(oo)!=s0: continue
        try: im,_,_=h.on_shell(list(free),SIG5)
        except Exception: continue
        pts.append((t,sum(free),im))
    if len(pts)>=30: base=(f0,pts,s0); break
f0,pts,s0=base
print(f"n=5 full-chamber slice: base={[str(x) for x in f0]} pts={len(pts)}")
for p in range(0,7):
    deg=6+p
    if len(pts)<deg+3: print(f"p={p}: few"); continue
    rows=[[t**i for i in range(deg+1)] for (t,sF,im) in pts]
    ys=[im*sF**p for (t,sF,im) in pts]
    sol=exact_solve(rows[:deg+1],ys[:deg+1])
    if sol is None: print(f"p={p}: INCONSISTENT"); continue
    bad=sum(1 for row,y in zip(rows[deg+1:],ys[deg+1:]) if sum(c*v for c,v in zip(sol,row))!=y)
    print(f"n=5 p={p}: deg{deg} mismatch {bad}{'  <<< POLYNOMIAL' if bad==0 else ''}")
