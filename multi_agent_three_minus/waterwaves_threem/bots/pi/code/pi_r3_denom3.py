#!/usr/bin/env python3
"""PI round-3: pin the denominator cleanly on ONE line by EXACT factorization.

Get the minimal N(t)/D(t) on line A, print D(t), factor it over Q into linear
factors (rational roots) / irreducible quadratics, and identify each factor by
evaluating, at the same parameter, the candidate omega-level forms.  Then check
the pole question: can the identified linear factors (w_i + w_j) vanish anywhere
on the real resonant manifold in this sector (would-be pole) or not?
"""
import subprocess, re
from fractions import Fraction as F
from itertools import combinations

BG = "./bg"; SIG = [-1, -1, -1, 1, 1, 1]

def onshell(freeW):
    s0 = SIG[0]; sF = sum(freeW); sS = sum(SIG[i+1]*freeW[i]**2 for i in range(4))
    wn = -(s0*sF**2 + sS)/(2*s0*sF); w1 = -(sF+wn)
    W = [w1]+list(freeW)+[wn]; K = [SIG[i]*W[i]**2 for i in range(6)]
    return W, K

def amp(K, W):
    Ks=",".join(str(F(k)) for k in K); Ws=",".join(str(F(w)) for w in W)
    o=subprocess.run([BG,"--amp","-K",Ks,"-W",Ws,"-g","1"],stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", o.stdout)
    if m: return F(m.group(1))
    m=re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", o.stdout)
    if m: assert F(m.group(1))==0; return F(m.group(2))
    raise RuntimeError(o.stdout)

def nullvec(rows):
    M=[r[:] for r in rows]; nr=len(M); nc=len(M[0]); piv=[]; r=0
    for c in range(nc):
        pr=next((i for i in range(r,nr) if M[i][c]!=0),None)
        if pr is None: continue
        M[r],M[pr]=M[pr],M[r]; inv=M[r][c]; M[r]=[x/inv for x in M[r]]
        for i in range(nr):
            if i!=r and M[i][c]!=0:
                f=M[i][c]; M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        piv.append(c); r+=1
        if r==nr: break
    fc=[c for c in range(nc) if c not in piv]
    if not fc: return None
    x=[F(0)]*nc; x[fc[0]]=F(1)
    for idx,c in enumerate(piv): x[c]=-M[idx][fc[0]]
    return x

def peval(c,t): return sum(ci*t**i for i,ci in enumerate(c))
def ptrim(c):
    c=c[:]
    while len(c)>1 and c[-1]==0: c.pop()
    return c

def gather(base,direction,npts=70,denom=240):
    pts=[]; sig0=None
    for k in range(-npts,npts+1):
        t=F(k,denom); free=[base[i]+t*direction[i] for i in range(4)]
        W,K=onshell(free)
        if any(w==0 for w in W): continue
        if any(sum(K[i] for i in S)==0 for r in range(1,6) for S in combinations(range(6),r)): continue
        cs=tuple(1 if sum(K[i] for i in S)>0 else -1 for r in range(1,6) for S in combinations(range(6),r))+tuple(1 if w>0 else -1 for w in W)
        if sig0 is None: sig0=cs
        if cs!=sig0: continue
        a=amp(K,W)
        if a is None: continue
        pts.append((t,a))
    return pts

def rat_interp(ts,ys,dN,dD):
    rows=[[t**i for i in range(dN+1)]+[-y*t**j for j in range(dD+1)] for t,y in zip(ts,ys)]
    x=nullvec(rows)
    if x is None: return None
    N,D=x[:dN+1],x[dN+1:]
    if all(d==0 for d in D): return None
    return N,D

def rational_roots(D):
    """rational roots of integer/rational poly D via factor search on a degree<=2 poly."""
    D=ptrim(D)
    deg=len(D)-1
    roots=[]
    if deg==1:
        roots.append(-D[0]/D[1])
    elif deg==2:
        a,b,c=D[2],D[1],D[0]
        disc=b*b-4*a*c
        # check perfect square of a rational
        if disc>=0:
            def isqrt(x):
                if x<0: return -1
                r=int(x**0.5)
                while r*r>x: r-=1
                while (r+1)*(r+1)<=x: r+=1
                return r
            num=disc.numerator; den=disc.denominator
            rn=isqrt(num); rd=isqrt(den)
            if rn*rn==num and rd*rd==den:
                s=F(rn,rd)
                roots=[(-b+s)/(2*a),(-b-s)/(2*a)]
            else:
                return None  # irrational/complex
        else:
            return None
    return roots

def main():
    base=[F(2),F(3),F(5),F(7)]; direction=[F(1),F(-1),F(1),F(-1)]
    pts=gather(base,direction)
    print(f"line A in-chamber points: {len(pts)}")
    ts=[p[0] for p in pts]; ys=[p[1] for p in pts]
    # minimal dD
    model=None
    for dD in range(0,8):
        dN=dD+18; need=dN+dD+2
        if len(pts)<need+4: break
        res=rat_interp(ts[:need],ys[:need],dN,dD)
        if res is None: continue
        N,D=res
        if all(peval(N,t)==y*peval(D,t) for t,y in zip(ts[need:],ys[need:])):
            model=(N,D,dD); break
    N,D,dD=model
    Dt=ptrim(D)
    # normalize D monic
    lead=Dt[-1]; Dt=[c/lead for c in Dt]
    print(f"minimal dD={dD};  D(t) (monic) = {[str(c) for c in Dt]}")
    rts=rational_roots(Dt)
    print(f"rational roots of D(t): {[str(r) for r in rts] if rts else 'none (irrational/complex)'}")
    if rts:
        for r in rts:
            free=[base[i]+r*direction[i] for i in range(4)]
            W,K=onshell(free)
            print(f"\n  at root t*={r}:  omega = {[str(w) for w in W]}")
            # which linear / propagator forms vanish?
            zer=[]
            for i,j in combinations(range(6),2):
                if W[i]+W[j]==0: zer.append(f"w{i+1}+w{j+1}")
                if W[i]-W[j]==0: zer.append(f"w{i+1}-w{j+1}")
            for rr in range(2,5):
                for S in combinations(range(6),rr):
                    wS=sum(W[s] for s in S); kS=sum(K[s] for s in S)
                    if kS!=0 and wS**2-abs(kS)==0:
                        zer.append("D_"+"".join(str(s+1) for s in S))
            print(f"    vanishing forms at this root: {zer}")
    # Pole question: does (w_i + w_j) (mixed pair) vanish on a real on-shell point in-chamber?
    print("\n  POLE CHECK: is (w_i+w_j)=0 reachable on the real manifold near line A's chamber?")
    print("  (the would-be pole locus of the identified linear denominator factors)")
    # scan along the line: track sign of each mixed-pair (w_i+w_j); does any cross zero while in chamber?
    signs={}
    for k in range(-300,301):
        t=F(k,200); free=[base[i]+t*direction[i] for i in range(4)]
        W,K=onshell(free)
        if any(w==0 for w in W): continue
        for i in range(3):
            for j in range(3,6):
                key=f"w{i+1}+w{j+1}"; v=W[i]+W[j]
                s=1 if v>0 else (-1 if v<0 else 0)
                signs.setdefault(key,set()).add(s)
    print("    sign-sets of mixed-pair sums over a wide param sweep:")
    for k in sorted(signs): print(f"      {k}: {sorted(signs[k])}")

if __name__=="__main__":
    main()
