#!/usr/bin/env python3
"""
PI round-6 DECISIVE, fit-free test of s1_014 (N_6 is a box spline, not a simple
single-wall truncated-power sum), using my own fast exact batch oracle (bgb --batch,
verified == ./bg).

If N = B + sum_W (k_W)_+ P_W  with B,P_W GLOBAL polynomials (the simple-sum/ round-5
premise), then on ANY F-const slice the jump across a (1=1) wall W is EXACTLY
k_W(t)*P_W(t), the restriction of the ONE global P_W.  So if the SAME dedup wall W is
crossed (cleanly, single-flip) at two different t on one slice -> two different chambers,
the extracted P_W(t) MUST be the SAME polynomial.  Differ => chamber-dependent jump =>
cross-terms => box spline.  Control: a synthetic simple sum gives identical P_W.
"""
import subprocess, itertools
from fractions import Fraction as F
import sympy as sp
SIG=[-1,-1,-1,1,1,1]; t=sp.symbols('t')

def batch(tuples):
    inp="\n".join(",".join(str(x) for x in fw) for fw in tuples)+"\n"
    out=subprocess.run(["./bgb","--batch"],input=inp,stdout=subprocess.PIPE,universal_newlines=True).stdout.splitlines()
    res=[]
    for line in out:
        if line.strip()=="SKIP": res.append(None)
        else:
            p=line.split(); res.append(([F(x) for x in p[:6]], F(p[6])))  # (omega[1..6], A_im)
    return res

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
def is11(S): return len(S)==2
def signvec(omg):
    out=[]
    for S in MIX:
        kS=sum(SIG[i]*omg[i]**2 for i in S)
        out.append(0 if kS==0 else (1 if kS>0 else -1))
    return tuple(out)
def e3mp(o): return o[0]*o[1]*o[2]+o[3]*o[4]*o[5]
def fd_degree(vals,maxd=28):
    cur=list(vals)
    for m in range(0,maxd+2):
        if all(x==0 for x in cur): return m-1
        if len(cur)<2: return None
        cur=[cur[i+1]-cur[i] for i in range(len(cur)-1)]
    return None
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

def runs_on(base,dirv,t0,t1,step):
    tts=[]; tt=t0
    while tt<=t1: tts.append(tt); tt+=step
    tuples=[[base[k]+x*dirv[k] for k in range(4)] for x in tts]
    out=batch(tuples)
    runs=[]
    for x,r in zip(tts,out):
        if r is None: continue
        omg,aim=r; sv=signvec(omg)
        if runs and runs[-1][0]==sv: runs[-1][1].append((x,omg,aim))
        else: runs.append((sv,[(x,omg,aim)]))
    return runs

def decisive(base,dirv,t0,t1,step, value_fn, want_print=True):
    runs=runs_on(base,dirv,t0,t1,step)
    from collections import defaultdict
    bywall=defaultdict(list)
    for i in range(len(runs)-1):
        sv1,p1=runs[i]; sv2,p2=runs[i+1]
        flips=[k for k in range(len(MIX)) if sv1[k]!=sv2[k]]
        if len(flips)==1 and is11(MIX[flips[0]]) and len(p1)>=12 and len(p2)>=12:
            bywall[flips[0]].append(i)
    target=None
    for w,iis in bywall.items():
        if len(iis)>=2: target=(w,iis); break
    if target is None: return None
    w,iis=target; S=MIX[w]
    # leg polys (fit on the first involved chamber)
    _,p0=runs[iis[0]]
    legpts={j:[(x,omg[j]) for (x,omg,aim) in p0] for j in range(6)}
    legpoly=[fit_poly_t(legpts[j]) for j in range(6)]
    if any(P is None for P in legpoly): return ("legfit_fail",S,iis)
    wsym=[P.as_expr() for P in legpoly]
    kWt=sp.expand(sum(SIG[j]*wsym[j]**2 for j in S))
    Ppolys=[]
    for i in iis[:2]:
        sv1,pL=runs[i]; sv2,pR=runs[i+1]
        VL=[(x,value_fn(omg,aim)) for (x,omg,aim) in pL]
        VR=[(x,value_fn(omg,aim)) for (x,omg,aim) in pR]
        PL=fit_poly_t(VL); PR=fit_poly_t(VR)
        if PL is None or PR is None: return ("valfit_fail",S,iis)
        midL=pL[len(pL)//2][0]; kL=kWt.subs(t,sp.Rational(midL.numerator,midL.denominator))
        J = (PL.as_expr()-PR.as_expr()) if kL>0 else (PR.as_expr()-PL.as_expr())
        q,r=sp.div(sp.expand(J),kWt,t)
        if sp.expand(r)!=0: return ("not_divisible",S,iis)
        Ppolys.append(sp.expand(q))
    same=sp.expand(Ppolys[0]-Ppolys[1])==0
    return (S,iis[:2],same,Ppolys,kWt)

def realN(omg,aim): return aim*e3mp(omg)         # tilde-N = (A_6/i)*(e3m+e3p)
def synth(omg,aim):
    s=F(0)
    for Sd in MIX:
        if not is11(Sd): continue
        kw=sum(SIG[j]*omg[j]**2 for j in Sd)
        if kw>0:
            i,j=Sd
            p=omg[i]*omg[j]+omg[(i+3)%6]**2-F(2)*omg[(j+2)%6]   # arbitrary GLOBAL poly in legs
            s+=kw*p
    return s

# slice family: vary one minus (idx in 0,1 of freeW=[w2,w3,w4,w5]) and one plus oppositely
dirs=[(1,0,-1,0),(1,0,0,-1),(0,1,-1,0),(0,1,0,-1)]
bases=[[F(3),F(5,2),F(11,2),F(7)],[F(2),F(4),F(13,2),F(9)],[F(5,2),F(6),F(5),F(17,2)],
       [F(7,2),F(3),F(6),F(8)],[F(4),F(3),F(7),F(15,2)],[F(2),F(11,2),F(9,2),F(7)],
       [F(9,2),F(2),F(8),F(13,2)],[F(3),F(7),F(5),F(10)]]
print("="*78)
print("DECISIVE: same (1=1) wall, two crossings on one F-const slice")
print("="*78)
done_real=False
for dirv in dirs:
    for base in bases:
        res=decisive(base,dirv,F(-4),F(7),F(1,20), realN)
        if res is None: continue
        if isinstance(res[0],str):  # a soft failure
            continue
        S,iis,same,Ppolys,kWt=res
        print(f"real N: dir={dirv} base={base}")
        print(f"  (1=1) dedup wall S(0-idx)={S} crossed cleanly at runs {iis} (two chambers)")
        print(f"  jump coefficient P_W(t) IDENTICAL across the two chambers? {same}")
        if not same:
            d=sp.Poly(Ppolys[0]-Ppolys[1],t)
            print(f"  -> they DIFFER (difference deg {d.degree()}): jump is CHAMBER-DEPENDENT")
            print(f"  -> CROSS-TERMS present => N_6 is a BOX SPLINE, NOT a simple sum.  s1_014 CONFIRMED.")
        done_real=True
        break
    if done_real: break
if not done_real: print("real N: no clean double-crossing found in slice set")

print()
print("CONTROL (synthetic simple sum must give IDENTICAL coefficients):")
done=False
for dirv in dirs:
    for base in bases:
        res=decisive(base,dirv,F(-4),F(7),F(1,20), synth)
        if res is None or isinstance(res[0],str): continue
        S,iis,same,Ppolys,kWt=res
        print(f"  synthetic: wall {S} crossed at runs {iis}; coefficients IDENTICAL? {same}  (expect True)")
        done=True; break
    if done: break
if not done: print("  control: no clean double-crossing found")
