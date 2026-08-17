#!/usr/bin/env python3
"""
PI round-6 DECISIVE independent test of s1_014 (N_6 is a box spline, NOT a simple
single-wall truncated-power sum), fit-free.

Logic: if N = B + sum_W (k_W)_+ P_W (simple sum, B & P_W GLOBAL polynomials), then on
ANY F-const slice the jump across a (1=1) wall W is EXACTLY k_W(t)*P_W(t) where P_W(t)
is the restriction of the one global P_W.  So if the SAME dedup wall W is crossed at TWO
different t (=> two different chambers) on one slice, the extracted P_W(t) MUST be the
IDENTICAL polynomial.  If they DIFFER, the jump coefficient is chamber-dependent =>
cross-terms => box spline (s1_014).  Control: a SYNTHETIC simple sum gives identical P_W.
"""
import subprocess, re, itertools
from fractions import Fraction as F
import sympy as sp
BG="./bg"; SIG=[-1,-1,-1,1,1,1]
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
def is11(S): return len(S)==2   # 2-element mixed dedup subset = (1=1) wall
def signvec(omg):
    out=[]
    for S in MIX:
        kS=sum(SIG[i]*omg[i]**2 for i in S)
        out.append(0 if kS==0 else (1 if kS>0 else -1))
    return tuple(out)
def e3mp(o): return o[0]*o[1]*o[2]+o[3]*o[4]*o[5]
def fd_degree(vals,maxd=26):
    cur=list(vals)
    for m in range(0,maxd+2):
        if all(x==0 for x in cur): return m-1
        if len(cur)<2: return None
        cur=[cur[i+1]-cur[i] for i in range(len(cur)-1)]
    return None
t=sp.symbols('t')
def fit_poly_t(pts):
    pts=sorted(pts,key=lambda x:x[0])
    deg=fd_degree([v for (_,v) in pts])
    if deg is None or deg+1>len(pts): return None
    rows=pts[:deg+1]
    M=sp.Matrix([[sp.Rational((tt**j).numerator,(tt**j).denominator) for j in range(deg+1)] for (tt,_) in rows])
    v=sp.Matrix([sp.Rational(vv.numerator,vv.denominator) for (_,vv) in rows])
    c=M.solve(v); P=sum(c[j]*t**j for j in range(deg+1))
    for (tt,vv) in pts:
        if sp.expand(P.subs(t,sp.Rational(tt.numerator,tt.denominator))-sp.Rational(vv.numerator,vv.denominator))!=0:
            return None
    return sp.Poly(P,t)

def slice_runs(w2,w3,a,b,t0,t1,step):
    runs=[]; tt=t0
    while tt<=t1:
        r=oracle([w2,w3,a+tt,b-tt])
        if r is not None:
            val,omg=r; sv=signvec(omg)
            if runs and runs[-1][0]==sv: runs[-1][1].append((tt,val,omg))
            else: runs.append((sv,[(tt,val,omg)]))
        tt+=step
    return runs

def analyze(label, w2,w3,a,b,t0,t1,step, value_fn):
    """value_fn(val,omg)->the N value to use.  Find a (1=1) dedup wall crossed at >=2
    clean single-wall boundaries; extract & compare jump coefficient polynomials."""
    runs=slice_runs(w2,w3,a,b,t0,t1,step)
    # collect clean single-flip boundaries
    bnds=[]
    for i in range(len(runs)-1):
        sv1,p1=runs[i]; sv2,p2=runs[i+1]
        flips=[k for k in range(len(MIX)) if sv1[k]!=sv2[k]]
        if len(flips)==1 and is11(MIX[flips[0]]) and len(p1)>=10 and len(p2)>=10:
            bnds.append((flips[0],i))
    # group by wall index
    from collections import defaultdict
    bywall=defaultdict(list)
    for (widx,i) in bnds: bywall[widx].append(i)
    target=None
    for widx,iis in bywall.items():
        if len(iis)>=2: target=(widx,iis); break
    if target is None:
        return None,"no (1=1) dedup wall crossed cleanly >=2x on this slice"
    widx,iis=target; S=MIX[widx]
    def kW(tt):  # k_S as poly value at slice param tt (use solved omg)
        return None
    # build k_W(t) symbolically via leg polynomials (fit legs on first chamber)
    _,p0=runs[iis[0]]
    legpts={j:[(tt,omg[j]) for (tt,val,omg) in p0] for j in range(6)}
    legpoly=[fit_poly_t(legpts[j]) for j in range(6)]
    w=[lp.as_expr() for lp in legpoly]
    kWt=sp.expand(sum(SIG[j]*w[j]**2 for j in S))
    Ppolys=[]
    for i in iis[:2]:
        sv1,pL=runs[i]; sv2,pR=runs[i+1]
        # order by sign of k_W on each side
        VL=[(tt,value_fn(val,omg)) for (tt,val,omg) in pL]
        VR=[(tt,value_fn(val,omg)) for (tt,val,omg) in pR]
        PL=fit_poly_t(VL); PR=fit_poly_t(VR)
        if PL is None or PR is None: return None,"per-chamber value not polynomial (contamination)"
        # jump = side(k>0) - side(k<0)
        midL=pL[len(pL)//2][0]; kL=kWt.subs(t,sp.Rational(midL.numerator,midL.denominator))
        if kL>0: J=sp.Poly(PL.as_expr()-PR.as_expr(),t)
        else:    J=sp.Poly(PR.as_expr()-PL.as_expr(),t)
        q,r=sp.div(J.as_expr(), kWt, t)
        if sp.expand(r)!=0: return None,"jump NOT divisible by k_W (exponent != 1?)"
        Ppolys.append(sp.expand(q))
    same = sp.expand(Ppolys[0]-Ppolys[1])==0
    return (S,iis[:2],same,Ppolys), "ok"

print("="*78)
print("DECISIVE TEST: jump coefficient of a (1=1) wall at two crossings on one slice")
print("  simple sum  => identical polynomial;  box spline => different.")
print("="*78)
def realN(val,omg): return val*e3mp(omg)
res,msg=analyze("realN", F(3),F(5,2),F(5,2),F(15,2),F(-2),F(6),F(1,40), realN)
if res is None:
    print("real N:",msg)
else:
    S,iis,same,Ppolys=res
    print(f"real N: (1=1) dedup wall S(0-idx legs)={S} crossed at runs {iis}")
    print(f"   jump-coefficient polynomials EQUAL across the two chambers? {same}")
    if not same:
        d=sp.Poly(Ppolys[0]-Ppolys[1],t)
        print(f"   they DIFFER (deg {d.degree()}): CHAMBER-DEPENDENT jump => CROSS-TERMS => box spline (s1_014 CONFIRMED)")

print()
print("CONTROL: synthetic SIMPLE SUM  Ntilde = sum_{(1=1) W} (k_W)_+ * p_W(omega)")
# p_W: a fixed polynomial per wall using leg values; same on every crossing by construction
def synth(val,omg):
    s=F(0)
    for Sd in MIX:
        if not is11(Sd): continue
        kw=sum(SIG[j]*omg[j]**2 for j in Sd)
        if kw>0:
            i,j=Sd
            p = omg[i]*omg[j] + omg[(i+2)%6]**2 - F(2)*omg[(j+1)%6]  # arbitrary global poly in legs
            s += kw*p
    return s
res2,msg2=analyze("synth", F(3),F(5,2),F(5,2),F(15,2),F(-2),F(6),F(1,40), synth)
if res2 is None:
    print("control:",msg2)
else:
    S,iis,same,Ppolys=res2
    print(f"control synthetic simple sum: wall {S} crossed at runs {iis}; coefficients EQUAL? {same}")
    print("   (must be True -> validates the test detects a genuine simple sum as 'equal')")
