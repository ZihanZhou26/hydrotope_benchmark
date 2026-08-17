#!/usr/bin/env python3
"""Batched exact oracle wrapper: amortizes subprocess startup over many points."""
import subprocess, os
from fractions import Fraction as F
HERE=os.path.dirname(os.path.abspath(__file__)); BG=os.path.join(HERE,"bg")
def batch_onshell(reqs):
    """reqs = list of (N, free_list, signs_list). Returns list of (re,im) Fractions (or None on ERR)."""
    lines=[]
    for (N,free,sig) in reqs:
        lines.append(f"{N}|{','.join(str(F(x)) for x in free)}|{','.join(str(int(s)) for s in sig)}")
    out=subprocess.run([BG,"--batch"],input="\n".join(lines).encode(),
                       stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout.decode()
    res=[]
    for ln in out.strip().split("\n"):
        if ln=="ERR" or ln=="": res.append(None); continue
        re_s,im_s=ln.split(";"); res.append((F(re_s),F(im_s)))
    return res
if __name__=="__main__":
    import time, random
    rnd=random.Random(1); reqs=[]
    while len(reqs)<1000:
        free=[F(rnd.randint(-80,80),10) for _ in range(4)]
        if 0 in free: continue
        reqs.append((6,free,[-1,-1,-1,1,1,1]))
    t0=time.time(); res=batch_onshell(reqs)
    ok=sum(1 for r in res if r is not None)
    print(f"batched 1000 n=6 points: {round(time.time()-t0,2)}s, {ok} ok")
