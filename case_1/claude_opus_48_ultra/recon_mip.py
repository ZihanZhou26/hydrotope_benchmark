"""Reconstruct A_5 in the 'smallest leg is a PLUS leg' region.
Distinguish smallest plus leg a; other plus legs symmetric (s1=sum,s2=prod...);
minus legs enter via e2(plus)=w1 w2 etc. Fit polynomial/rational."""
from bg import amp_two_minus
from fractions import Fraction as Q
import itertools, sys
from recon import rref_nullspace

def collect_mip(n, grid, target=600):
    pts=[]; seen=set()
    for combo in itertools.product(grid, repeat=n-2):
        free=[Q(c) for c in combo]
        try: A,kL,wL=amp_two_minus(n,free)
        except Exception: continue
        w=list(wL)
        if any(v==0 for v in w): continue
        w2=[v*v for v in w]
        mn=min(w2); argmn=w2.index(mn)
        if argmn<2: continue  # want smallest is plus
        # plus legs are indices 2..n-1
        plus=w[2:]; minus=w[:2]
        # smallest plus = the plus leg with min square
        ap=min(plus, key=lambda v:v*v)
        others=list(plus); others.remove(ap)
        key=tuple(sorted(w))
        if key in seen: continue
        seen.add(key)
        pts.append((ap, tuple(others), tuple(minus), A.im))
        if len(pts)>=target: break
    return pts

def mono_basis(deg, others_n):
    # monomials a^i * m_lambda(others) * (minus invariants) ...
    # We'll use: a^i * p_sym(others) * q_sym(minus). Represent generally below.
    pass

# Use variables: a, and elementary symmetric of others (eo1.., ), and of minus (m1=sum,m2=prod)
# But minus determined: m1=-(a+sum(others)), m2 = e2(plus)=a*sum(others)+e2(others).
# So everything is a function of a and others. A is symmetric in others.
# Fit A as polynomial in (a, eo1, eo2, ..., eo_{n-3}) homogeneous degree 2(n-2).
import sympy as sp
def run(n):
    grid=[Q(1),Q(3,2),Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(9,2),Q(5),Q(1,2),Q(5,4),Q(7,4),Q(11,4),Q(13,4),Q(6)]
    pts=collect_mip(n,grid,target=700)
    print(f"n={n}: {len(pts)} min-is-plus points",flush=True)
    nplus=n-2; nother=nplus-1
    dA=2*(n-2)
    # symmetric functions of others: power sums p1..p_nother (use elementary e1..e_nother)
    # build monomials a^i * prod e_j(others)^{c_j} of total degree dA (deg e_j=j)
    # enumerate
    from itertools import product as iproduct
    def others_elem(vals,k):
        from itertools import combinations
        if k==0: return Q(1)
        s=Q(0)
        for c in combinations(range(len(vals)),k):
            t=Q(1)
            for idx in c: t*=vals[idx]
            s+=t
        return s
    # exponent tuples (i, c1..c_nother) with i + sum(j*cj)=dA
    monos=[]
    def rec(rem, j, cur):
        if j>nother:
            if rem>=0:
                monos.append((rem, tuple(cur)))  # i=rem for a
            return
        maxc=rem//j
        for c in range(maxc+1):
            rec(rem-j*c, j+1, cur+[c])
    rec(dA,1,[])
    nb=len(monos)
    print(f"  numerator-only basis size (poly ansatz) = {nb}",flush=True)
    # try polynomial fit (D=1) first
    def mval(mono, a, others):
        i,cs=mono
        v=a**i
        for j,c in enumerate(cs, start=1):
            if c: v*=others_elem(others,j)**c
        return v
    rows=[]; rhs=[]
    for (a,others,minus,Aim) in pts:
        rows.append([mval(m,a,others) for m in monos]); rhs.append(Aim)
    # solve exactly
    if len(pts)<nb+8:
        print("  not enough pts for poly ansatz");
    else:
        # use rref of [rows | -rhs] homogeneous? No, inhomogeneous. Solve square subsystem.
        from fit_global import pick_and_solve
        sol,sub=pick_and_solve(rows,rhs,nb)
        if sol is None:
            print("  poly ansatz singular")
        else:
            bad=sum(1 for r,b in zip(rows,rhs) if sum(sol[j]*r[j] for j in range(nb))!=b)
            print(f"  POLY ansatz: {'CONSISTENT' if bad==0 else f'inconsistent ({bad}/{len(pts)})'}",flush=True)
            if bad==0:
                a,e1,e2=sp.symbols('a e1 e2')  # e1,e2 = elem sym of others (n=5 -> 2 others)
                expr=0
                for m,co in zip(monos,sol):
                    if co==0: continue
                    i,cs=m
                    term=sp.Rational(co)*a**i
                    syms=[e1,e2]
                    for j,c in enumerate(cs,start=1):
                        if c: term*=syms[j-1]**c
                    expr+=term
                print("  A =", sp.factor(expr))
    return pts

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 5
    run(n)
