#!/usr/bin/env python3
"""PI r6: harden s1_015 (explicit (1=2) jump coefficient Q) at SEVERAL (1=2) walls with
DIFFERENT gauge legs, using my batch oracle. General gauge detection. Exact."""
import subprocess, itertools
from fractions import Fraction as F
SIG=[-1,-1,-1,1,1,1]; MINUS={0,1,2}; PLUS={3,4,5}
def batch(tuples):
    inp="\n".join(",".join(str(x) for x in fw) for fw in tuples)+"\n"
    out=subprocess.run(["./bgb","--batch"],input=inp,stdout=subprocess.PIPE,universal_newlines=True).stdout.splitlines()
    return [None if l.strip()=="SKIP" else ([F(x) for x in l.split()[:6]],F(l.split()[6])) for l in out]
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
def is12(S):  # geometric (1=2): some rep has 1 minus + 2 plus
    return len(S)==3
def signvec(omg):
    return tuple(0 if sum(SIG[i]*omg[i]**2 for i in S)==0 else (1 if sum(SIG[i]*omg[i]**2 for i in S)>0 else -1) for S in MIX)
def e3mp(o): return o[0]*o[1]*o[2]+o[3]*o[4]*o[5]
# poly utils (Fraction)
def fd_degree(vals,maxd=30):
    cur=list(vals)
    for m in range(0,maxd+2):
        if all(x==0 for x in cur): return m-1
        if len(cur)<2: return None
        cur=[cur[i+1]-cur[i] for i in range(len(cur)-1)]
    return None
def newton(xs,ys):
    n=len(xs); c=list(ys)
    for j in range(1,n):
        for i in range(n-1,j-1,-1): c[i]=(c[i]-c[i-1])/(xs[i]-xs[i-j])
    poly=[F(0)]
    for i in range(n-1,-1,-1):
        new=[F(0)]*(len(poly)+1)
        for k,cc in enumerate(poly): new[k+1]+=cc; new[k]+=cc*(-xs[i])
        new[0]+=c[i]; poly=new
    while len(poly)>1 and poly[-1]==0: poly.pop()
    return poly
def ev(p,x):
    r=F(0)
    for c in reversed(p): r=r*x+c
    return r
def fit(xs,ys):
    d=fd_degree(ys)
    if d is None or d+1>len(xs): return None
    p=newton(xs[:d+1],ys[:d+1])
    return p if all(ev(p,xs[k])==ys[k] for k in range(len(xs))) else None
def psub(a,b):
    n=max(len(a),len(b)); r=[F(0)]*n
    for i,c in enumerate(a): r[i]+=c
    for i,c in enumerate(b): r[i]-=c
    while len(r)>1 and r[-1]==0: r.pop()
    return r
def pmul(a,b):
    r=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): r[i+j]+=x*y
    return r
def pdivmod(a,b):
    a=a[:]
    while len(b)>1 and b[-1]==0: b.pop()
    q=[F(0)]*max(len(a)-len(b)+1,1)
    while len(a)>=len(b) and not(len(a)==1 and a[0]==0):
        d=len(a)-len(b); c=a[-1]/b[-1]; q[d]=c
        for i in range(len(b)): a[d+i]-=c*b[i]
        while len(a)>1 and a[-1]==0: a.pop()
        if len(a)<len(b): break
    while len(q)>1 and q[-1]==0: q.pop()
    return q,a

def gauge(Sdedup):
    """return (i,j,k,l,p,q) legs for the (1=2) wall whose dedup subset is Sdedup."""
    comp=tuple(sorted(set(range(6))-set(Sdedup)))
    for rep in (Sdedup,comp):
        ms=[x for x in rep if x in MINUS]; ps=[x for x in rep if x in PLUS]
        if len(ms)==1 and len(ps)==2:
            i=ms[0]; j,k=ps; l=list(PLUS-set(ps))[0]; p,qq=sorted(MINUS-{i})
            return i,j,k,l,p,qq
    return None

def Qval(w,g):
    i,j,k,l,p,q=g
    A1=w[p]+w[q]; A2=w[p]*w[q]; B1=w[j]+w[k]; B2=w[j]*w[k]; y=w[l]
    return A2*B1*(y*y-A1*A1-A1*B1+A2-B2)+B2*y*(A2-B1*y-B2)

def test_slice(base,dirv,t0,t1,step):
    tts=[]; tt=t0
    while tt<=t1: tts.append(tt); tt+=step
    out=batch([[base[m]+x*dirv[m] for m in range(4)] for x in tts])
    runs=[]
    for x,r in zip(tts,out):
        if r is None: continue
        omg,aim=r; sv=signvec(omg)
        if runs and runs[-1][0]==sv: runs[-1][1].append((x,omg,aim))
        else: runs.append((sv,[(x,omg,aim)]))
    results=[]
    for c in range(len(runs)-1):
        sv1,pL=runs[c]; sv2,pR=runs[c+1]
        fl=[m for m in range(len(MIX)) if sv1[m]!=sv2[m]]
        if len(fl)!=1 or not is12(MIX[fl[0]]) or len(pL)<14 or len(pR)<14: continue
        S=MIX[fl[0]]; g=gauge(S)
        if g is None: continue
        xs=[x for (x,omg,aim) in pL]
        legp=[fit(xs,[omg[m] for (x,omg,aim) in pL]) for m in range(6)]
        if any(P is None for P in legp): continue
        # tilde N per chamber
        NL=fit([x for (x,o,a) in pL],[a*e3mp(o) for (x,o,a) in pL])
        NR=fit([x for (x,o,a) in pR],[a*e3mp(o) for (x,o,a) in pR])
        if NL is None or NR is None: continue
        i,j,k,l,p,q=g
        kijk=psub(pmul(legp[i],legp[i]),psub(pmul(legp[j],legp[j])+([F(0)]),[F(0)]))  # placeholder
        kijk=psub(pmul(legp[i],legp[i]), psub([F(0)],[F(0)]))
        # build k_ijk = wi^2 - wj^2 - wk^2 as poly
        kijk=psub(pmul(legp[i],legp[i]), pmul(legp[j],legp[j]))
        kijk=psub(kijk, pmul(legp[k],legp[k]))
        # Q(t) poly: evaluate via leg polys -> build symbolic product through values+interp
        # easier: sample Q on xs and interpolate
        Qpts=[Qval([ev(lp,x) for lp in legp], g) for x in xs]
        Qp=fit(xs,Qpts)
        midx=pL[len(pL)//2][0]; kmid=ev(kijk,midx)
        J = psub(NL,NR) if kmid>0 else psub(NR,NL)
        pred = pmul(pmul(kijk,pmul(kijk,kijk)), Qp)
        qq,rr = pdivmod(J,pred)
        ok = (len(rr)==1 and rr[0]==0) and (len(qq)==1)
        results.append((S,g,qq if ok else None, ok))
    return results

slices=[
 ([F(4),F(3),F(24,5),F(7)],(0,0,1,-1)),     # original wall (minus i=1)
 ([F(8),F(2),F(5),F(7)],(0,0,1,-1)),         # try to hit i=2 wall
 ([F(2),F(8),F(5),F(6)],(0,0,1,-1)),
 ([F(7),F(3),F(4),F(9)],(0,0,1,-1)),
 ([F(3),F(2),F(6),F(8)],(0,1,0,-1)),
]
print("Hardening s1_015: Delta/[k_ijk^3 * Q] should be the constant 32 at every clean (1=2) wall.")
seen_minus=set()
for base,dirv in slices:
    res=test_slice(base,dirv,F(-3),F(7),F(1,30))
    for S,g,const,ok in res:
        i=g[0]
        print(f"  wall dedup {S}: minus-leg i={i+1}, plus-pair=({g[1]+1},{g[2]+1}), excl-plus={g[3]+1}, "
              f"other-minus=({g[4]+1},{g[5]+1}) -> Delta/[k^3 Q] = {const if ok else 'NOT CONSTANT'}")
        seen_minus.add(i)
print("distinct minus-leg gauges tested:", sorted(x+1 for x in seen_minus))
