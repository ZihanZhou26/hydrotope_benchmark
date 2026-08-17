import time
from fractions import Fraction as F
from engine import build_onshell, Engine
pts=[[1,2,3,4,5],[1,3,4,5,6],[1,2,3,4,1000]]   # principal chamber (w2=1 smallest)
for free in pts:
    t=time.time()
    W,K=build_onshell(7,free,[-1,-1,1,1,1,1,1])
    re,im=Engine('frac').BGAmplitude(7,K,W)
    pred=2**6*W[1]*W[2]**(2*7-5)
    print(f"free={free} dt={time.time()-t:.1f}s Re={re} a={im} pred={pred} EXACT_MATCH={im==pred and re==0}",flush=True)
