#!/usr/bin/env python3
"""
PI round-6 INDEPENDENT verification (own oracle, own evaluator; no student code).

Re-verifies the load-bearing NEW round-5 claims:
  (A) foundation re-confirm: A_6*(e3m+e3p) polynomial on an F-const slice (pole order 1),
      N_6 ODD under omega->-omega.
  (B) s1_015: the EXPLICIT (1=2) jump coefficient Q. On a clean single-(1=2)-wall
      crossing, N_+(t)-N_-(t) == k_{ijk}(t)^3 * Q(t) with student-1's explicit Q.
  (C) s1_014: the SIMPLE single-wall truncated-power sum FAILS (N_6 is a box spline w/
      cross-terms).  Decisive, fit-free: mixed 2nd difference across the two (1=1) walls
      {2,4} and {2,5} (whose intersection forces NO third mixed wall) scales as eps^1
      (singular cross-term), while a synthetic SIMPLE SUM scales as eps^2 (control).
"""
import subprocess, re, itertools
from fractions import Fraction as F
import sympy as sp
BG="./bg"
SIG=[-1,-1,-1,1,1,1]   # legs 1..6 (0-indexed 0..5)

def oracle(freeW):
    ws=",".join(str(x) for x in freeW)
    o=subprocess.run([BG,"-n","6","-w",ws,"-s","-1,-1,-1,1,1,1","-g","1"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"omega = \{([^}]*)\}",o.stdout)
    if not m: return None
    omg=[F(s) for s in m.group(1).split(",")]
    m=re.search(r"A_6 = i \* \(([^)]*)\)",o.stdout)
    return (F(m.group(1)), omg)        # returns (A_6/i  value, omega list)

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
def e3mp(omg): return e3(omg[:3])+e3(omg[3:])
def Nval(val,omg):   # N = A_6*(e3m+e3p)/(i 2^5 g^-3) = val*(e3m+e3p)/32 ; use unscaled tilde-N=val*(e3m+e3p)
    return val*e3mp(omg)

def fd_degree(vals,maxd=24):
    cur=list(vals)
    for m in range(0,maxd+2):
        if all(x==0 for x in cur): return m-1
        if len(cur)<2: return None
        cur=[cur[i+1]-cur[i] for i in range(len(cur)-1)]
    return None
def fit_poly_t(pts):
    """pts: (t, value). interpolate exact poly in t; verify on all points. None if not poly."""
    pts=sorted(pts,key=lambda x:x[0])
    deg=fd_degree([v for (_,v) in pts],22)
    if deg is None or deg+1>len(pts): return None
    t=sp.symbols('t'); rows=pts[:deg+1]
    M=sp.Matrix([[sp.Rational((tt**j).numerator,(tt**j).denominator) for j in range(deg+1)] for (tt,_) in rows])
    v=sp.Matrix([sp.Rational(vv.numerator,vv.denominator) for (_,vv) in rows])
    c=M.solve(v); P=sum(c[j]*t**j for j in range(deg+1))
    for (tt,vv) in pts:
        if sp.expand(P.subs(t,sp.Rational(tt.numerator,tt.denominator))-sp.Rational(vv.numerator,vv.denominator))!=0:
            return None
    return sp.Poly(P,t)

print("="*78)
print("PART A  foundation re-confirm")
print("="*78)
# F-const slice in one chamber: free (w2,w3)=(2,5), (w4,w5)=(13/3+t, 4-t) sumFree const
fixed=[F(2),F(5)]; a,b=F(13,3),F(4)
pts_AS=[]; pts_A=[]; sv0=None; clean=True
t=F(0)
while t<=F(40,100):
    r=oracle(fixed+[a+t,b-t])
    if r is not None:
        val,omg=r; sv=signvec(omg)
        if sv0 is None: sv0=sv
        if sv!=sv0: clean=False; break
        pts_A.append((t,val))                # A_6/i alone
        pts_AS.append((t,val*e3mp(omg)))     # (A_6/i)*(e3m+e3p)
    t+=F(1,100)
print(f" one-chamber slice, {len(pts_A)} pts, single chamber: {clean}")
PA=fit_poly_t(pts_A); PAS=fit_poly_t(pts_AS)
print(f"  A_6/i polynomial on slice?            -> {None if PA is None else 'deg '+str(PA.degree())}")
print(f"  (A_6/i)*(e3m+e3p) polynomial on slice? -> {None if PAS is None else 'deg '+str(PAS.degree())}")
print("  => A_6 has a genuine simple pole at e3m+e3p=0 (pole order 1) iff first is None, second is poly.")
# parity: N_6 odd under omega->-omega.  A_6(-w)=A_6(w) (even); e3m+e3p odd => N odd.
r1=oracle([F(2),F(3),F(5),F(7)]); rm=oracle([F(-2),F(-3),F(-5),F(-7)])
if r1 and rm:
    v1,o1=r1; vm,om=rm
    print(f"  A_6/i(w)={v1}  A_6/i(-w)={vm}  even? {v1==vm}")
    N1=Nval(v1,o1); Nm=Nval(vm,om)
    print(f"  N(w)={N1}  N(-w)={Nm}   N odd (N(-w)=-N(w))? {Nm==-N1}")

print()
print("="*78)
print("PART B  s1_015: explicit (1=2) jump coefficient Q")
print("="*78)
# clean single-(1=2) crossing: wall S={2,3,4}: w4^2=w2^2+w3^2.  (w2,w3)=(4,3)->w4=5.
# F-const slice: w4=24/5+t, w5=7-t, wall at t=1/5.
fixed=[F(4),F(3)]; a,b=F(24,5),F(7); twall=F(1,5)
runs=[]; t=F(5,100)
while t<=F(35,100):
    r=oracle(fixed+[a+t,b-t])
    if r is not None:
        val,omg=r; sv=signvec(omg)
        if runs and runs[-1][0]==sv: runs[-1][1].append((t,val,omg))
        else: runs.append((sv,[(t,val,omg)]))
    t+=F(1,400)
# pick the two runs adjacent to twall with single-wall flip
print(f" {len(runs)} chambers in window; sizes {[len(r[1]) for r in runs]}")
pair=None
for i in range(len(runs)-1):
    sv1,p1=runs[i]; sv2,p2=runs[i+1]
    nflip=sum(1 for x,y in zip(sv1,sv2) if x!=y)
    bt=(p1[-1][0]+p2[0][0])/2
    if nflip==1 and len(p1)>=8 and len(p2)>=8 and abs(bt-twall)<F(1,50):
        pair=(i,sv1,sv2); flippedW=[MIX[k] for k in range(len(MIX)) if sv1[k]!=sv2[k]][0]
if pair is None:
    print("  no clean single-wall (1=2) boundary found"); 
else:
    i,sv1,sv2=pair; _,p1=runs[i]; _,p2=runs[i+1]
    print(f"  clean single-wall crossing; flipped wall (0-idx legs) = {flippedW}")
    t=sp.symbols('t')
    # which side has k_{234}=w4^2-w2^2-w3^2 > 0 ?  k_{234}=(24/5+t)^2-16-9
    def k234(tt): return (a+tt)**2 - F(16) - F(9)
    Lp=[(tt,Nval(val,omg)) for (tt,val,omg) in p1]
    Rp=[(tt,Nval(val,omg)) for (tt,val,omg) in p2]
    PL=fit_poly_t(Lp); PR=fit_poly_t(Rp)
    print(f"  per-chamber tildeN deg: L={None if PL is None else PL.degree()}, R={None if PR is None else PR.degree()}")
    # order so that '+' = k>0 side
    kL=k234(p1[len(p1)//2][0]); 
    if kL>0: Pp,Pm=PL,PR
    else:    Pp,Pm=PR,PL
    Delta=sp.Poly(Pp.as_expr()-Pm.as_expr(),t)               # = (k234)^3 * Q  (* 32 from tilde convention)
    # build k234(t) and Q(t) symbolically along the slice using solved legs 1,6
    # need omega(t): legs 2,3 fixed; 4,5 on slice; solve 1,6 (poly on F-const slice)
    # interpolate each leg as poly in t -- use ONE chamber (p1), equally spaced; legs are
    # globally polynomial on the F-const slice (chamber-independent), so p1 suffices.
    legpts={i:[] for i in range(6)}
    for (tt,val,omg) in p1:
        for i in range(6): legpts[i].append((tt,omg[i]))
    legpoly=[]
    for i in range(6):
        P=fit_poly_t(legpts[i]); legpoly.append(P.as_expr() if P else None)
    w=[lp for lp in legpoly]
    print(f"  leg polys deg: {[ (None if e is None else sp.Poly(e,t).degree()) for e in w]}")
    k234t=sp.expand(w[3]**2 - w[1]**2 - w[2]**2)   # legs idx:0=1,1=2,2=3,3=4,4=5,5=6
    # student-1 gauge (complement {1,5,6}): i=1(minus), {j,k}={5,6}, l=4, {p,q}={2,3}
    A1=w[1]+w[2]; A2=w[1]*w[2]; B1=w[4]+w[5]; B2=w[4]*w[5]; y=w[3]
    Q = A2*B1*(y**2 - A1**2 - A1*B1 + A2 - B2) + B2*y*(A2 - B1*y - B2)
    Q=sp.expand(Q)
    pred = sp.expand(k234t**3 * Q)
    ratio = sp.simplify(Delta.as_expr()/pred)
    print(f"  k_ijk(t)=w4^2-w2^2-w3^2; Q(t) from s1_015 explicit formula.")
    print(f"  Delta(t)/[k_ijk^3 * Q]  = {ratio}   (constant => formula confirmed; =32 is the i2^5 g^-3 convention)")
    # double-check it's truly constant (deg 0)
    rr=sp.nsimplify(ratio)
    print(f"  ratio is constant: {sp.simplify(sp.diff(ratio, t))==0}")

print()
print("="*78)
print("PART C  s1_014: simple single-wall sum FAILS (box spline cross-terms)")
print("="*78)
v,w3=F(5),F(2)
# wall functions in the box: W1={2,4}: k=w4^2-w2^2 ; W2={2,5}: k=w5^2-w2^2
def corner(s1,s2):
    r=oracle([v,w3,v+s1,v+s2]); 
    return None if r is None else (r[0],r[1])
print(" box base: (w2,w3,w4,w5)=(5,2,5,5); cross W1={2,4},W2={2,5}; NO third mixed wall forced.")
print(f" {'eps':>10} | {'D_realN/eps^2':>22} | {'D_realN/eps^1':>22}")
prev=None
import math
for k in range(1,7):
    eps=F(1,10)/ (2**(k-1))
    c={}
    ok=True
    for s1 in (eps,-eps):
        for s2 in (eps,-eps):
            cc=corner(s1,s2)
            if cc is None: ok=False; break
            c[(1 if s1>0 else -1,1 if s2>0 else -1)]=cc
        if not ok: break
    if not ok: print(f"{float(eps):>10.5f} | corner failed"); continue
    # tilde-N = val*(e3m+e3p)
    def tN(key): val,omg=c[key]; return val*e3mp(omg)
    D = tN((1,1)) - tN((1,-1)) - tN((-1,1)) + tN((-1,-1))
    print(f"{float(eps):>10.6f} | {float(D/eps**2):>22.6g} | {float(D/eps**1):>22.6g}")
print(" If D/eps^2 -> finite nonzero : simple-sum-compatible (eps^2).")
print(" If D/eps^1 -> finite nonzero & D/eps^2 -> blows up : SINGULAR cross-term (eps^1) => box spline.")

print()
print("  CONTROL: synthetic SIMPLE SUM  Ntilde_ctrl = (k24)_+ * P1(omega) + (k25)_+ * P2(omega)")
print("           (P1,P2 generic polys in the 6 oracle legs). Must scale as eps^2.")
def ctrl(s1,s2):
    r=oracle([v,w3,v+s1,v+s2])
    if r is None: return None
    val,omg=r; w=omg
    k24=w[3]**2-w[1]**2; k25=w[4]**2-w[1]**2
    P1=w[0]*w[5]+w[2]**2+F(3)*w[3]      # arbitrary deg-2 poly in legs
    P2=w[1]*w[4]-w[0]**2+F(2)*w[5]*w[2]
    return (max(k24,F(0))*P1 + max(k25,F(0))*P2)
for k in range(1,7):
    eps=F(1,10)/(2**(k-1))
    cc={}
    ok=True
    for s1 in (eps,-eps):
        for s2 in (eps,-eps):
            x=ctrl(s1,s2)
            if x is None: ok=False;break
            cc[(1 if s1>0 else -1,1 if s2>0 else -1)]=x
        if not ok: break
    if not ok: print("   ctrl corner failed"); continue
    D=cc[(1,1)]-cc[(1,-1)]-cc[(-1,1)]+cc[(-1,-1)]
    print(f"   ctrl eps={float(eps):>9.6f} | D/eps^2={float(D/eps**2):>14.6g} | D/eps^1={float(D/eps**1):>14.6g}")
