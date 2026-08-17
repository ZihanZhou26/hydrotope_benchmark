"""General-n test of the global ansatz:
   A_n = P0(w) + sum_{mu in {1,2}, j in plus} P(w_mu,w_j; w_mu'; elemsym(other plus)) |w_j^2 - w_mu^2|
P0 symmetric S2 x S_{n-2} deg 2(n-2); P deg 2(n-3).  Exact RREF consistency check."""
from bg import amp_two_minus
from fractions import Fraction as Q
from itertools import combinations, permutations
import itertools, sys

def amag(x): return x if x>=0 else -x

def sym2_vals(a, v):  # symmetric basis of 2 vars, degree a -> list of values
    out=[]
    for p in range(a, a//2 -1, -1):
        q=a-p
        if p<q: break
        ps=set(permutations((p,q)))
        out.append(sum(v[0]**e[0]*v[1]**e[1] for e in ps))
    return out if a>0 else [Q(1)]

def parts_le(b, k):
    res=[]
    def rec(rem,maxp,cur):
        if rem==0: res.append(tuple(cur)); return
        if len(cur)==k: return
        for p in range(min(maxp,rem),0,-1): rec(rem-p,p,cur+[p])
    rec(b,b,[]); return res

def msym_vals(b, v):  # monomial symmetric of deg b in len(v) vars
    m=len(v)
    if b==0: return [Q(1)]
    out=[]
    for lam in parts_le(b,m):
        exps=tuple(list(lam)+[0]*(m-len(lam)))
        ps=set(permutations(exps))
        out.append(sum( __import__('functools').reduce(lambda acc,ie: acc*v[ie[0]]**ie[1], enumerate(e), Q(1)) for e in ps))
    return out

def P0_vals(n, w):
    minus=(w[0],w[1]); plus=tuple(w[2:]); D=2*(n-2)
    vals=[]
    for a in range(0,D+1):
        b=D-a
        for u in sym2_vals(a,minus):
            for vv in msym_vals(b,plus):
                vals.append(u*vv)
    return vals

def P_mono_exps(n):
    # exps (a,b,c, lam) : w_mu^a w_j^b w_mu'^c * msym(other plus)_{deg=rest}; total deg = 2(n-3)
    D=2*(n-3); res=[]
    nother=n-3
    for a in range(D+1):
        for b in range(D-a+1):
            for c in range(D-a-b+1):
                rest=D-a-b-c
                for lam in ([()] if rest==0 else parts_le(rest, nother) if nother>0 else ([()] if rest==0 else [])):
                    res.append((a,b,c,lam))
    return res

def kabs_vals(n, w, pexps):
    minus_idx=[0,1]; plus_idx=list(range(2,n)); nother=n-3
    vals=[Q(0)]*len(pexps)
    for mu in minus_idx:
        wmu=w[mu]; mup=w[1-mu]
        for j in plus_idx:
            wj=w[j]; others=[w[p] for p in plus_idx if p!=j]
            kab=amag(wj*wj-wmu*wmu)
            for idx,(a,b,c,lam) in enumerate(pexps):
                ms=Q(1)
                if lam:
                    exps=tuple(list(lam)+[0]*(nother-len(lam)))
                    s=Q(0)
                    for e in set(permutations(exps)):
                        t=Q(1)
                        for oi,ee in zip(others,e):
                            if ee: t*=oi**ee
                        s+=t
                    ms=s
                vals[idx]+= (wmu**a)*(wj**b)*(mup**c)*ms*kab
    return vals

def collect(n, grid, target):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        if any(v==0 for v in wL): continue
        key=tuple(sorted(wL))
        if key in seen: continue
        seen.add(key); pts.append((tuple(wL),A.im))
        if len(pts)>=target: break
    return pts

def rref_consistency(rows, rhs, nb):
    M=[ [Q(x) for x in r]+[Q(b)] for r,b in zip(rows,rhs) ]
    rows_n=len(M); piv=[]; r=0
    for c in range(nb):
        p=None
        for rr in range(r,rows_n):
            if M[rr][c]!=0: p=rr;break
        if p is None: continue
        M[r],M[p]=M[p],M[r]; pv=M[r][c]; M[r]=[a/pv for a in M[r]]
        for rr in range(rows_n):
            if rr!=r and M[rr][c]!=0:
                f=M[rr][c]; M[rr]=[a-f*b for a,b in zip(M[rr],M[r])]
        piv.append(c); r+=1
        if r==rows_n: break
    inc=any(all(M[rr][c]==0 for c in range(nb)) and M[rr][nb]!=0 for rr in range(rows_n))
    return (not inc), len(piv)

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 6
    tgt=int(sys.argv[2]) if len(sys.argv)>2 else 500
    grid=[Q(1),Q(3,2),Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(-1),Q(-2),Q(1,2),Q(5,4),Q(-3,2),Q(9,2),Q(11,4),Q(13,4),Q(-3),Q(5),Q(-5,2)]
    pexps=P_mono_exps(n)
    pts=collect(n,grid,tgt)
    nb0=len(P0_vals(n,pts[0][0])); nbk=len(pexps); nb=nb0+nbk
    print(f"n={n}: P0 basis {nb0}, |k| basis {nbk}, total {nb}, pts {len(pts)}",flush=True)
    if len(pts)<nb+10:
        print("NEED MORE POINTS (have %d, need >%d)"%(len(pts),nb)); sys.exit()
    rows=[]; rhs=[]
    for (w,Aim) in pts:
        rows.append(P0_vals(n,w)+kabs_vals(n,w,pexps)); rhs.append(Aim)
    ok,rank=rref_consistency(rows,rhs,nb)
    print(f"rank={rank}; ansatz {'CONSISTENT -> global formula exists for n=%d'%n if ok else 'INCONSISTENT'}",flush=True)
