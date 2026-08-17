#!/usr/bin/env python3
# Scan general F-const slices base + t*dir (sum dir = 0) for a (1=1) wall crossed
# cleanly (single-flip) at >=2 t-values (different chambers).
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
    return [F(s) for s in m.group(1).split(",")]
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
def runs_of(base,dirv,t0,t1,step):
    runs=[]; tt=t0
    while tt<=t1:
        fw=[base[k]+tt*dirv[k] for k in range(4)]
        omg=oracle(fw)
        if omg is not None:
            sv=signvec(omg)
            if runs and runs[-1][0]==sv: runs[-1][1].append((tt,omg))
            else: runs.append((sv,[(tt,omg)]))
        tt+=step
    return runs

# free legs order: [w2,w3,w4,w5]; minus=w2,w3 ; plus=w4,w5
# direction varies one minus + one plus oppositely (F-const): d=(1,0,-1,0) etc
dirs=[(1,0,-1,0),(1,0,0,-1),(0,1,-1,0),(0,1,0,-1)]
bases=[
 [F(3),F(5,2),F(11,2),F(7)],
 [F(2),F(4),F(13,2),F(9)],
 [F(5,2),F(6),F(5),F(17,2)],
 [F(7,2),F(3),F(6),F(8)],
 [F(2),F(11,2),F(9,2),F(7)],
 [F(4),F(3),F(7),F(15,2)],
]
found=[]
for dirv in dirs:
    for base in bases:
        runs=runs_of(base,dirv,F(-3),F(7),F(1,25))
        bywall=defaultdict(list)
        for i in range(len(runs)-1):
            sv1,p1=runs[i]; sv2,p2=runs[i+1]
            flips=[k for k in range(len(MIX)) if sv1[k]!=sv2[k]]
            if len(flips)==1 and is11(MIX[flips[0]]) and len(p1)>=10 and len(p2)>=10:
                bywall[flips[0]].append(i)
        for w,iis in bywall.items():
            if len(iis)>=2:
                print(f"FOUND dir={dirv} base={base}: wall {MIX[w]} crossed at runs {iis} "
                      f"(chambers {len(runs)})")
                found.append((dirv,base,MIX[w],iis))
if not found: print("none found")
