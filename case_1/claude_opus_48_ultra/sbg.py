"""Symbolic Berends-Giele with sign-resolved |k|: gives the EXACT rational
function for A_n in the chamber of a chosen reference point.

mag(expr) -> +expr or -expr depending on sign(expr) at reference numeric point.
All momenta are k_i = sigma_i * w_i^2 with w_i symbolic; reference fixes the signs.
"""
import sympy as sp
from itertools import permutations
from functools import lru_cache
import math, sys

def build(n, ref_w, sigmas):
    w = sp.symbols(f'w1:{n+1}')           # w[0]..w[n-1]
    sig = list(sigmas)
    k = [sig[i]*w[i]**2 for i in range(n)]
    refsub = {w[i]: sp.Rational(ref_w[i]) for i in range(n)}

    sign_cache = {}
    def mag(expr):
        e = sp.expand(expr)
        key = sp.srepr(e)
        s = sign_cache.get(key)
        if s is None:
            val = e.subs(refsub)
            val = sp.nsimplify(val)
            if val == 0:
                raise ValueError(f"mag of zero at reference: {e}")
            s = 1 if val > 0 else -1
            sign_cache[key] = s
        return e if s==1 else -e

    Ecache = {}
    def EKernel(ps):
        key = tuple(sp.srepr(sp.expand(p)) for p in ps)
        if key in Ecache: return Ecache[key]
        m = len(ps)
        if m == 3:
            r = sp.Rational(-1,2)*(mag(ps[0])*mag(ps[1]) + ps[0]*ps[1])
        else:
            p1,p2,rest = ps[0],ps[1],ps[2:]
            qp2 = mag(p2); trest = sum(rest)
            r = qp2**(m-3)*EKernel((p1,p2,trest))/math.factorial(m-2)
            for mm in range(1,m-3+1):
                sub=(p1,p2+sum(rest[:mm]))+rest[mm:]
                r -= qp2**mm/math.factorial(mm)*EKernel(sub)
        r = sp.expand(r); Ecache[key]=r; return r

    Fcache = {}
    def FKernel(ps):
        key = tuple(sp.srepr(sp.expand(p)) for p in ps)
        if key in Fcache: return Fcache[key]
        m=len(ps)
        if m==3:
            r = sp.Integer(-1) - ps[0]*ps[1]/(mag(ps[0])*mag(ps[1]))
        else:
            p1,p2,rest=ps[0],ps[1],ps[2:]
            qp1=mag(p1); qp2=mag(p2)
            r = 2*EKernel(ps)/qp1
            for mm in range(1,m-3+1):
                sigM=p2+sum(rest[:mm])
                a=(-sigM,p2)+rest[:mm]
                b=(p1,sigM)+rest[mm:]
                r -= 2*EKernel(a)*FKernel(b)
            r = r/qp2
        r=sp.together(sp.expand(r)); Fcache[key]=r; return r

    def Vertex(moms, omegas):
        nn=len(moms); acc=sp.Integer(0)
        for p in permutations(range(nn)):
            pm=tuple(moms[i] for i in p)
            acc += omegas[p[0]]*omegas[p[1]]*FKernel(pm)
        return sp.I*sp.Rational(-1,2)*acc

    def Propagator(wS,kS):
        return -sp.I/(wS**2/mag(kS) - 1)

    # set partitions of list S into exactly r blocks
    @lru_cache(maxsize=None)
    def setparts(S, r):
        S=list(S)
        if r==1: return [[tuple(S)]]
        if r>len(S): return []
        res=[]; mn=min(S); others=[x for x in S if x!=mn]
        from itertools import combinations
        for size in range(0,len(S)-r+1):
            for sub in combinations(others,size):
                fp=(mn,)+sub; rem=[x for x in S if x not in fp]
                if len(rem)>=r-1:
                    for sp_ in setparts(tuple(rem),r-1):
                        res.append([fp]+sp_)
        return res

    curcache={}
    def total_k(S): return sum(k[i] for i in S)
    def total_w(S): return sum(w[i] for i in S)
    def current(S):
        key=tuple(sorted(S))
        if len(key)==1: return sp.Integer(1)
        if key in curcache: return curcache[key]
        wS=total_w(key); kS=total_k(key); res=sp.Integer(0)
        for m in range(2,len(key)+1):
            for part in setparts(key,m):
                sM=tuple(total_k(b) for b in part)
                sO=tuple(total_w(b) for b in part)
                vM=(-kS,)+sM; vO=(-wS,)+sO
                v=Vertex(vM,vO)
                prod=sp.Integer(1)
                for b in part: prod*=current(b)
                res += v*prod
        val=sp.together(res*Propagator(wS,kS))
        curcache[key]=val; return val

    def amplitude():
        rest=tuple(range(1,n)); res=sp.Integer(0)
        for m in range(2,n):
            for part in setparts(rest,m):
                sM=tuple(total_k(b) for b in part); sO=tuple(total_w(b) for b in part)
                vM=(k[0],)+sM; vO=(w[0],)+sO
                v=Vertex(vM,vO); prod=sp.Integer(1)
                for b in part: prod*=current(b)
                res += v*prod
        return res
    return w, sig, refsub, amplitude

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    ref={5:[-sp.Rational(9,2),2,sp.Rational(5,2),3,-3]}[n] if n==5 else None
    sig=[-1,-1]+[1]*(n-2)
    w,sigl,refsub,amp=build(n,ref,sig)
    print("computing symbolic amplitude (off-shell, chamber-fixed)...",flush=True)
    A=amp()
    A=sp.together(A)
    print("numeric check at reference:", sp.simplify(A.subs(refsub)), " (expect -2304 I)")
    sp.srepr  # keep
    # Save the off-shell symbolic A for later manifold reduction
    import pickle
    with open(f"sbg_A{n}.pkl","wb") as f:
        pickle.dump(sp.srepr(A), f)
    print("saved sbg_A%d.pkl"%n)
    # quick: divide by I, show as function; restrict to manifold w1=-(w2+..+wn), w_n solved
    print("A/I (off-shell) leading form:")
    num,den=sp.fraction(sp.together(A/sp.I))
    print("  denom factors:", sp.factor(den))
