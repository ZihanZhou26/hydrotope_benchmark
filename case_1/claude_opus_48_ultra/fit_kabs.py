"""Global fit for n=5: A = P0(w) + sum_{mu in {1,2}, j in plus} P(w_mu,w_j; w_mu', e1',e2')*|w_j^2 - w_mu^2|
P0 symmetric S2xS3 deg 6; P symmetric in the 'other plus' legs, deg 4.
Exact rational linear solve; check consistency across all chambers."""
from bg import amp_two_minus
from fractions import Fraction as Q
from itertools import combinations, permutations, product as iproduct
import itertools, sys
from fit_global import pick_and_solve

def amag(x): return x if x>=0 else -x

# ---- symmetric monomial helpers ----
def sym2(a, vars2):  # sum over distinct perms of exponent (a,0)?? we want sym poly basis of 2 vars degree a
    # basis element: m_{(p,q)} for partition p>=q, p+q=a ; value = sum of distinct perms of (p,q)
    out=[]
    for p in range(a, (a)//2 -1, -1):
        q=a-p
        if p<q: break
        exps=(p,q)
        perms=set(permutations(exps))
        out.append(sum(vars2[0]**e[0]*vars2[1]**e[1] for e in perms))
    return out

def sym2_count(a):
    return a//2+1

def msym_list(b, vars3):  # all monomial-symmetric of degree b in 3 vars, as values
    out=[]
    # partitions of b into <=3 parts
    parts=[]
    def rec(rem,maxp,cur):
        if rem==0: parts.append(tuple(cur)); return
        if len(cur)==3: return
        for p in range(min(maxp,rem),0,-1): rec(rem-p,p,cur+[p])
    rec(b,b,[])
    for lam in parts:
        exps=tuple(list(lam)+[0]*(3-len(lam)))
        ps=set(permutations(exps))
        out.append(sum(vars3[0]**e[0]*vars3[1]**e[1]*vars3[2]**e[2] for e in ps))
    if b==0: out=[Q(1)]
    return out

def P0_basis_vals(w):  # w: (w0,w1 | w2,w3,w4)
    minus=(w[0],w[1]); plus=(w[2],w[3],w[4])
    vals=[]
    for a in range(0,7):
        b=6-a
        s2=sym2(a,minus) if a>0 else [Q(1)]
        s3=msym_list(b,plus)
        for u in s2:
            for v in s3:
                vals.append(u*v)
    return vals

# P monomials: w_mu^a * w_j^b * w_mup^c * e1'^d * e2'^e  with a+b+c+d+2e=4
def P_mono_exps():
    res=[]
    for a in range(0,5):
        for b in range(0,5-a):
            for c in range(0,5-a-b):
                for d in range(0,5-a-b-c):
                    rem=4-a-b-c-d
                    if rem%2==0:
                        res.append((a,b,c,d,rem//2))
    return res

PEXPS=P_mono_exps()

def kabs_basis_vals(w):
    # for each P monomial type, basis function = sum_{mu,j} mono * |w_j^2-w_mu^2|
    minus_idx=[0,1]; plus_idx=[2,3,4]
    vals=[Q(0)]*len(PEXPS)
    for mu in minus_idx:
        wmu=w[mu]; mup=w[1-mu]
        for j in plus_idx:
            wj=w[j]
            others=[w[p] for p in plus_idx if p!=j]
            e1=others[0]+others[1]; e2=others[0]*others[1]
            kab=amag(wj*wj-wmu*wmu)
            for idx,(a,b,c,d,e) in enumerate(PEXPS):
                term=(wmu**a)*(wj**b)*(mup**c)*(e1**d)*(e2**e)*kab
                vals[idx]+=term
    return vals

def collect(grid, target=400):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=3):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(5,free)
        except Exception: continue
        if any(v==0 for v in wL): continue
        key=tuple(sorted(wL))
        if key in seen: continue
        seen.add(key); pts.append((tuple(wL),A.im))
        if len(pts)>=target: break
    return pts

if __name__=="__main__":
    grid=[Q(1),Q(3,2),Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(-1),Q(-2),Q(1,2),Q(5,4),Q(-3,2),Q(11,4),Q(-3),Q(9,2),Q(13,4)]
    pts=collect(grid,target=400)
    nb0=len(P0_basis_vals(pts[0][0])); nbk=len(PEXPS)
    nb=nb0+nbk
    print(f"P0 basis {nb0}, |k| basis {nbk}, total {nb}; pts {len(pts)}",flush=True)
    rows=[]; rhs=[]
    for (w,Aim) in pts:
        rows.append(P0_basis_vals(w)+kabs_basis_vals(w)); rhs.append(Aim)
    if len(pts)<nb+10: print("need more pts"); sys.exit()
    # Exact RREF of augmented [M | rhs]; check consistency (no [0..0|nonzero] row).
    M=[ [Q(x) for x in r]+[Q(b)] for r,b in zip(rows,rhs) ]
    ncol=nb  # last col is rhs
    pivcols=[]; r=0; rows_n=len(M)
    for c in range(ncol):
        piv=None
        for rr in range(r,rows_n):
            if M[rr][c]!=0: piv=rr;break
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]; pv=M[r][c]; M[r]=[a/pv for a in M[r]]
        for rr in range(rows_n):
            if rr!=r and M[rr][c]!=0:
                f=M[rr][c]; M[rr]=[a-f*b for a,b in zip(M[rr],M[r])]
        pivcols.append(c); r+=1
        if r==rows_n: break
    # consistency: any row with all-zero in cols 0..nb-1 but nonzero rhs?
    inconsistent=False
    for rr in range(rows_n):
        if all(M[rr][c]==0 for c in range(ncol)) and M[rr][ncol]!=0:
            inconsistent=True; break
    rank=len(pivcols)
    print(f"rank={rank} of {nb} cols; {'INCONSISTENT' if inconsistent else 'CONSISTENT'}",flush=True)
    if not inconsistent:
        print(">>> LINEAR-|k| ansatz fits A_5 everywhere (global formula exists)!")
        # particular solution: free cols =0
        sol=[Q(0)]*nb
        for i,c in enumerate(pivcols):
            sol[c]=M[i][ncol]
        # verify
        bad=sum(1 for rr,bb in zip(rows,rhs) if sum(sol[j]*rr[j] for j in range(nb))!=bb)
        print("verify particular solution bad=",bad)
        print("nonzero P0 terms:", sum(1 for j in range(nb0) if sol[j]!=0),
              " nonzero |k| terms:", sum(1 for j in range(nb0,nb) if sol[j]!=0))
        import pickle
        with open("kabs_sol5.pkl","wb") as f: pickle.dump([str(s) for s in sol],f)
