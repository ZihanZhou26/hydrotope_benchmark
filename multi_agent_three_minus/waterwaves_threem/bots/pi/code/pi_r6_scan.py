#!/usr/bin/env python3
import subprocess, re, itertools
from fractions import Fraction as F
from collections import defaultdict
BG="./bg"; SIG=[-1,-1,-1,1,1,1]
def oracle(freeW):
    ws=",".join(str(x) for x in freeW)
    o=subprocess.run([BG,"-n","6","-w",ws,"-s","-1,-1,-1,1,1,1","-g","1"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"omega = \{([^}]*)\}",o.stdout)
    if not m: return None
    omg=[F(s) for s in m.group(1).split(",")]
    return omg
def mixed_subsets():
    legs=set(range(6)); subs=[]; seen=set()
    for r in range(2,6):
        for S in itertools.combinations(range(6),r):
            sg=[SIG[i] for i in S]
            if not(-1 in sg and 1 in sg): continue
            comp=frozenset(legs-set(S))
            if frozenset(S) in seen or comp in seen: continue
            seen.add(frozenset(S)); subs.append(S)
    return subs
MIX=mixed_subsets()
def signvec(omg):
    out=[]
    for S in MIX:
        kS=sum(SIG[i]*omg[i]**2 for i in S)
        out.append(0 if kS==0 else (1 if kS>0 else -1))
    return tuple(out)
def is11(S): return len(S)==2

def runs_of(w2,w3,a,b,t0,t1,step):
    runs=[]; tt=t0
    while tt<=t1:
        omg=oracle([w2,w3,a+tt,b-tt])
        if omg is not None:
            sv=signvec(omg)
            if runs and runs[-1][0]==sv: runs[-1][1].append((tt,omg))
            else: runs.append((sv,[(tt,omg)]))
        tt+=step
    return runs

slices=[
 (F(3),F(5,2),F(5,2),F(15,2)),
 (F(2),F(7),F(3),F(11)),
 (F(5),F(2),F(1),F(13)),
 (F(7),F(11,3),F(2),F(12)),
 (F(4),F(9,2),F(1),F(14)),
 (F(6),F(5,2),F(1),F(15)),
 (F(8),F(3),F(2),F(16)),
 (F(5,2),F(9),F(3),F(13)),
]
for (w2,w3,a,b) in slices:
    runs=runs_of(w2,w3,a,b,F(-3),F(8),F(1,30))
    bywall=defaultdict(list)
    for i in range(len(runs)-1):
        sv1,p1=runs[i]; sv2,p2=runs[i+1]
        flips=[k for k in range(len(MIX)) if sv1[k]!=sv2[k]]
        if len(flips)==1 and is11(MIX[flips[0]]) and len(p1)>=8 and len(p2)>=8:
            bywall[flips[0]].append((i,len(p1),len(p2)))
    twice=[(MIX[w],v) for w,v in bywall.items() if len(v)>=2]
    print(f"slice w2={w2} w3={w3} a={a} b={b}: {len(runs)} chambers; "
          f"(1=1) walls crossed >=2x: {[(s, [x[0] for x in v]) for s,v in twice]}")
