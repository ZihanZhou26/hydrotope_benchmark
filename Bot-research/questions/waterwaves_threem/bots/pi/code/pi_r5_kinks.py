#!/usr/bin/env python3
"""
PI round-5: independent confirmation of the spline JUMP EXPONENTS (s1_013) with
proper SINGLE-WALL discipline (the multi-wall contamination hazard, s1_dec_008 /
s2_014, is real -- a naive window crosses walls involving the solved legs 1,6).

Method: along an F-const slice, classify every sample by the sign vector of ALL
mixed wall functions k_S.  A maximal run with constant sign vector = ONE chamber.
Take the two chambers adjacent to a target wall, fit the per-chamber polynomial
N(t)=A_6(t)*(e3m+e3p)(t) exactly on each, compare Taylor coefficients at the wall.
Lowest differing order = jump exponent p of N (= kink order of A_6, since
(e3m+e3p)!=0 at these walls).  Expect (1=1)->1, (1=2)->3.
"""
import subprocess, re, itertools
from fractions import Fraction as F
import sympy as sp
BG="./bg"

def oracle(freeW):
    ws=",".join(str(x) for x in freeW)
    o=subprocess.run([BG,"-n","6","-w",ws,"-s","-1,-1,-1,1,1,1","-g","1"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"omega = \{([^}]*)\}",o.stdout); omg=[F(s) for s in m.group(1).split(",")]
    m=re.search(r"A_6 = i \* \(([^)]*)\)",o.stdout)
    return (F(m.group(1)), omg)

SIG=[-1,-1,-1,1,1,1]   # legs 1..6
def mixed_subsets():
    """mixed subsets, deduped against complement (k_S=-k_{S^c} -> same geometric wall)."""
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

def chamber_runs(fixed,a,b,t0,t1,step):
    """sample t in [t0,t1]; return list of (sign_vector, [(t,A,omg),...]) runs."""
    samples=[]
    t=t0
    while t<=t1:
        r=oracle(fixed+[a+t,b-t])
        if r is not None:
            A,omg=r; samples.append((t,A,omg,signvec(omg)))
        t+=step
    runs=[]
    for (t,A,omg,sv) in samples:
        if runs and runs[-1][0]==sv: runs[-1][1].append((t,A,omg))
        else: runs.append((sv,[(t,A,omg)]))
    return runs

def fit_N(side):
    """exact interpolating polynomial in s=t-twall through side points; return Taylor coeffs."""
    s0=side[0][0]   # use first point's t as anchor offset handled by caller; here s already = t
    deg=len(side)-1
    S=sp.Matrix([[sp.Rational((s**j).numerator,(s**j).denominator) for j in range(deg+1)] for (s,_) in side])
    v=sp.Matrix([sp.Rational(N.numerator,N.denominator) for (_,N) in side])
    return list(S.solve(v))

def fd_degree(vals,maxd=20):
    cur=list(vals)
    for m in range(0,maxd+2):
        if all(x==0 for x in cur): return m-1
        if len(cur)<2: return None
        cur=[cur[i+1]-cur[i] for i in range(len(cur)-1)]
    return None

def fit_poly_t(pts):
    """pts: equally spaced (t,N). detect degree by finite differences, interpolate
       exact sympy Poly in t through deg+1 points; verify on all. Returns Poly or None."""
    pts=sorted(pts,key=lambda x:x[0])
    deg=fd_degree([N for (_,N) in pts],18)
    if deg is None: return None
    t=sp.symbols('t'); rows=pts[:deg+1]
    M=sp.Matrix([[sp.Rational((tt**j).numerator,(tt**j).denominator) for j in range(deg+1)] for (tt,_) in rows])
    v=sp.Matrix([sp.Rational(NN.numerator,NN.denominator) for (_,NN) in rows])
    c=M.solve(v)
    P=sum(c[j]*t**j for j in range(deg+1))
    for (tt,NN) in pts:
        if sp.simplify(P.subs(t,sp.Rational(tt.numerator,tt.denominator))-sp.Rational(NN.numerator,NN.denominator))!=0:
            return None
    return sp.Poly(P,t)

def root_mult(P,r):
    t=sp.symbols('t'); m=0; Q=P
    while not Q.is_zero and sp.simplify(Q.eval(sp.Rational(r.numerator,r.denominator)))==0:
        m+=1; Q=Q.diff(t)
    return m

def analyze(name,fixed,a,b,t0,t1,step,twall):
    runs=chamber_runs(fixed,a,b,t0,t1,step)
    print(" %s: %d chambers in window; sizes %s"%(name,len(runs),[len(r[1]) for r in runs]))
    best=None
    for i in range(len(runs)-1):
        sv1,p1=runs[i]; sv2,p2=runs[i+1]
        nflip=sum(1 for x,y in zip(sv1,sv2) if x!=y)
        bt=(p1[-1][0]+p2[0][0])/2
        if nflip==1 and len(p1)>=10 and len(p2)>=10:
            if best is None or abs(bt-twall)<abs(best[0]-twall): best=(bt,i)
    if best is None:
        print("   no clean single-flip boundary with >=10 pts each side"); return None
    bt,i=best; sv1,p1=runs[i]; sv2,p2=runs[i+1]
    flipped=[MIX[k] for k in range(len(MIX)) if sv1[k]!=sv2[k]]
    print("   clean single-wall boundary; flipped geometric wall S=%s ; t_wall=%s"%(flipped[0],twall))
    t=sp.symbols('t')
    Lp=[(tt,A*(e3(omg[:3])+e3(omg[3:]))) for (tt,A,omg) in p1]
    Rp=[(tt,A*(e3(omg[:3])+e3(omg[3:]))) for (tt,A,omg) in p2]
    PL=fit_poly_t(Lp); PR=fit_poly_t(Rp)
    if PL is None or PR is None:
        print("   per-chamber N not polynomial on a run (contamination)"); return None
    print("   per-chamber N degrees: L=%d R=%d"%(PL.degree(),PR.degree()))
    diff=sp.Poly(PL.as_expr()-PR.as_expr(),t)
    if diff.is_zero:
        print("   N_L==N_R (no jump)"); return 0
    p=root_mult(diff,twall)
    print("   jump N_L-N_R = (t-t_wall)^p * (...); multiplicity p=%d"%p)
    print("   jump factored:",sp.factor(diff.as_expr()))
    return p

# (1=1) wall w4=w2:  fixed=(w2,w3)=(3,5/2), w4=5/2+t crosses 3 at t=1/2
print("(1=1) wall (w4=w2): expect p=1 (C^0, first-derivative kink)")
o11=analyze("(1=1)",[F(3),F(5,2)],F(5,2),F(7),F(35,100),F(65,100),F(1,200),F(1,2))
# (1=2) wall w4^2=w2^2+w3^2: (w2,w3)=(4,3) -> w4=5; w4=24/5+t crosses 5 at t=1/5
print("(1=2) wall (w4^2=w2^2+w3^2): expect p=3 (C^2, cubic kink)")
o12=analyze("(1=2)",[F(4),F(3)],F(24,5),F(7),F(10,100),F(30,100),F(1,300),F(1,5))
print()
print("RESULT: (1=1) p=%s  (1=2) p=%s   (expect 1 and 3, confirming s1_013)"%(o11,o12))
