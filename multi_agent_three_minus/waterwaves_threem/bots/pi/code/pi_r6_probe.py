#!/usr/bin/env python3
"""PI round-6 probe: find a clean base point for the cross-term box test.
Box crosses (1=1) walls W1={2,4} and W2={2,5} (share leg 2). Their intersection
omega_2^2=omega_4^2=omega_5^2 does NOT force a third (1=1) mixed wall (omega_4=omega_5
is a plus-plus ANALYTIC ordering), so there is NO W_3 confound -- unlike {2,4}&{3,5}.
Goal: a base with omega_2=omega_4=omega_5=v on-shell, e3m+e3p != 0, no other wall in a
small box, legs 1,6 real."""
import subprocess, re, itertools
from fractions import Fraction as F
BG="./bg"
SIG=[-1,-1,-1,1,1,1]
def oracle(freeW):
    ws=",".join(str(x) for x in freeW)
    o=subprocess.run([BG,"-n","6","-w",ws,"-s","-1,-1,-1,1,1,1","-g","1"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"omega = \{([^}]*)\}",o.stdout)
    if not m: return None
    omg=[F(s) for s in m.group(1).split(",")]
    m=re.search(r"A_6 = i \* \(([^)]*)\)",o.stdout)
    return (F(m.group(1)), omg)
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
def e3(t): return t[0]*t[1]*t[2]

# base: free legs (w2,w3,w4,w5) = (v, w3, v, v); perturb w4,w5
for v,w3 in [(F(5),F(2)),(F(5),F(11,3)),(F(4),F(3)),(F(7),F(3)),(F(5),F(13,7))]:
    eps=F(1,10)
    corners={}
    ok=True
    svs={}
    for s1 in (eps,-eps):
        for s2 in (eps,-eps):
            r=oracle([v,w3,v+s1,v+s2])
            if r is None: ok=False; break
            A,omg=r
            corners[(s1,s2)]=(A,omg)
            svs[(s1,s2)]=signvec(omg)
        if not ok: break
    if not ok:
        print(f"v={v} w3={w3}: oracle failed at a corner"); continue
    # which walls flip between corners? compare to base sign vector via all four
    # determine per-wall whether it depends on s1, s2
    base_sv=None
    print(f"\nv={v} w3={w3} eps={eps}:")
    for k in corners:
        A,omg=corners[k]
        ep=e3(omg[:3])+e3(omg[3:])
        print(f"  s=({k[0]},{k[1]}): e3m+e3p={ep}  signvec={svs[k]}")
    # find walls whose sign differs across corners
    allsv=list(svs.values())
    flip_idx=[i for i in range(len(MIX)) if len(set(sv[i] for sv in allsv))>1]
    print("  walls that flip in box:", [MIX[i] for i in flip_idx])
