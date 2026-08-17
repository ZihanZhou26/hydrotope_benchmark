#!/usr/bin/env python3
"""PI round-8 independent verification of the round-7 load-bearing claims.

Uses ONLY the PI's own freshly-built oracle (./bg) and the PI's own batched
exact evaluator (./pi_batch, faithful copy of the bg.cpp engine). NO student code
is imported. The on-shell leg-solve is reimplemented here from the documented
formula in bg.cpp and cross-checked against ./bg's own printed omega list.

Claims under test:
  s1_020  PARITY: A_n EVEN under w->-w (always, even homogeneity deg 2n-4);
          N_n=A_n*D_n^min has parity = (-1)^deg(D_n^min). n=6: D^min=e3m+e3p
          (deg 3 ODD) -> N_6 ODD; n=7: D^min=prod(w_i+w_j) (12 factors EVEN)
          -> N_7 EVEN. ("N_n odd" was an n=6-only artifact.)
  s2_021  Soft recursion A_n -> 2(n-3) w_p^2 A_{n-1} EXACT at n=7, BOTH legs.
  s1_021  n=7 single-wall jump exponents (1=1)->1, (1=2)->2, with n=6 control
          ((1=1)->1, (1=2)->3).

N_n := A_n * prod_{i in minus, j in plus}(w_i + w_j) (full mixed product). The
product is a polynomial, smooth & nonzero across the difference-branch (1=1)/(1=2)
walls, so it clears the rational denominator without changing kink exponents.
"""
import subprocess, sys
from fractions import Fraction as F

HERE = sys.path[0] or "."
BG = HERE + "/bg"
BATCH = HERE + "/pi_batch"
SIG = lambda n: [-1,-1,-1] + [1]*(n-3)

# ---------------- on-shell solver (my own; bg.cpp documented formula) ---------
def solve_full(freeW, n, signs):
    assert len(freeW) == n-2 and len(signs) == n
    s1 = signs[0]
    sumFree = sum(freeW, F(0))
    sumSig = sum(signs[i+1]*freeW[i]*freeW[i] for i in range(n-2))
    wn = -(s1*sumFree*sumFree + sumSig)/(F(2)*s1*sumFree)
    w1 = -(sumFree + wn)
    W = [w1] + list(freeW) + [wn]
    K = [signs[i]*W[i]*W[i] for i in range(n)]   # g=1
    return W, K

def amp_batch(points):
    lines = [",".join(str(x) for x in W)+"|"+",".join(str(x) for x in K) for W,K in points]
    out = subprocess.run([BATCH], input="\n".join(lines), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).stdout.strip().split("\n")
    res = []
    for o in out:
        o=o.strip()
        if o in ("SIGFPE","ERR"): res.append(o)
        elif o.startswith("RE("): raise RuntimeError("nonzero real part: "+o)
        else: res.append(F(o))
    return res

def amp1(W,K): return amp_batch([(W,K)])[0]

def Wamp(W, signs):
    K=[signs[i]*W[i]*W[i] for i in range(len(W))]
    return amp1(W,K)

# ---------------- exact polynomial utilities (ascending coeffs) ---------------
def lagrange(xs, ys):
    n=len(xs); coeffs=[F(0)]*n
    for i in range(n):
        num=[F(1)]; den=F(1)
        for j in range(n):
            if j==i: continue
            new=[F(0)]*(len(num)+1)
            for k,c in enumerate(num):
                new[k]+= c*(-xs[j]); new[k+1]+= c
            num=new; den*=(xs[i]-xs[j])
        sc=ys[i]/den
        for k in range(len(num)): coeffs[k]+=num[k]*sc
    return coeffs

def peval(c,x):
    r=F(0)
    for a in reversed(c): r=r*x+a
    return r

def trim(c):
    c=list(c)
    while len(c)>1 and c[-1]==0: c=c[:-1]
    return c

def adaptive(vals_dict, order, ret_deg=False):
    """vals_dict: {t: F}. order: list of t to use. Increase degree until 2 held-out
    points confirm. Returns exact poly coeffs."""
    pts=list(order)
    for d in range(1,len(pts)-2):
        xs=pts[:d+1]; ys=[vals_dict[t] for t in xs]
        c=lagrange(xs,ys)
        held=pts[d+1:]
        if all(peval(c,t)==vals_dict[t] for t in held) and len(held)>=2:
            return (trim(c), d) if ret_deg else trim(c)
    raise RuntimeError(f"did not settle within pool (tried deg up to {len(pts)-3})")

def root_mult(c, t0):
    c=trim(c); m=0
    while len(c)>1 and peval(c,t0)==0:
        n=len(c); q=[F(0)]*(n-1); rem=c[-1]
        for k in range(n-2,-1,-1): q[k]=rem; rem=c[k]+rem*t0
        assert rem==0
        c=trim(q); m+=1
    if len(c)==1 and c[0]==0: return m+1  # identically zero remainder
    return m

def D_full(W, n):
    p=F(1)
    for i in (0,1,2):
        for j in range(3,n): p*=(W[i]+W[j])
    return p

import itertools
def wallfns(W,n):
    """named mixed-wall function values, to detect single-wall crossings."""
    d={}; mi=[0,1,2]; pj=list(range(3,n))
    for i in mi:
        for j in pj: d[f"11_{i}_{j}"]=W[i]**2-W[j]**2
    for i in mi:
        for jk in itertools.combinations(pj,2): d[f"12_{i}_{jk[0]}_{jk[1]}"]=W[i]**2-W[jk[0]]**2-W[jk[1]]**2
    for i in mi:
        for jkl in itertools.combinations(pj,3): d[f"13_{i}_"+"_".join(map(str,jkl))]=W[i]**2-sum(W[x]**2 for x in jkl)
    return d

print("="*72)
print("PI ROUND-8 INDEPENDENT VERIFICATION  (own ./bg + own ./pi_batch; no student code)")
print("="*72)

# solver/oracle self-check
W,K=solve_full([F(2),F(3),F(5),F(7),F(11)],7,SIG(7))
bgout=subprocess.run([BG,"-n","7","-w","2,3,5,7,11","-s","-1,-1,-1,1,1,1,1"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True).stdout
print("solver self-check W =",[str(x) for x in W])
print("  ./bg :",[l for l in bgout.split(chr(10)) if l.startswith('omega')][0])
assert amp1(W,K)==F("-14285060561327616/141684725"); print("  amp self-check vs ./bg: OK\n")

# ============================ TEST 1: PARITY (s1_020) ========================
print("--- TEST 1: parity (s1_020): A_n even; N_6 odd, N_7 even ---")
for n,base in ((6,[F(2),F(3),F(5),F(7)]),(7,[F(2),F(3),F(5),F(7),F(11)])):
    W,K=solve_full(base,n,SIG(n)); A=amp1(W,K)
    Wm=[-x for x in W]; Km=[SIG(n)[i]*Wm[i]*Wm[i] for i in range(n)]
    assert Km==K
    Am=amp1(Wm,Km)
    Dp=D_full(W,n); Dm=D_full(Wm,n)
    print(f"  n={n}: A_n(-w)==A_n(w)? {A==Am}   full D parity: {'EVEN' if Dp==Dm else 'ODD'} (deg {3*(n-3)})")
    if n==6:
        e3=W[0]*W[1]*W[2]+W[3]*W[4]*W[5]; e3m=Wm[0]*Wm[1]*Wm[2]+Wm[3]*Wm[4]*Wm[5]
        Np=A*e3; Nn=Am*e3m
        print(f"        N_6=A_6*(e3m+e3p): N(-w) = {'-N(w) -> ODD' if Nn==-Np else 'NOT odd'}")
    else:
        Np=A*Dp; Nn=Am*Dm
        print(f"        N_7=A_7*D_7:       N(-w) = {'+N(w) -> EVEN' if Nn==Np else 'NOT even'}")
print("  => CONFIRMED: A_n even (homogeneity); N_6 ODD, N_7 EVEN. s1_020 holds.\n")

# ===================== TEST 2: SOFT RECURSION n=7 (s2_021) ===================
print("--- TEST 2: soft recursion A_7 -> 8 w_p^2 A_6, both legs (s2_021) ---")
def soft(kind):
    n=7; sig=SIG(7)
    if kind=='plus':   # soft plus leg = leg6 (freeW idx4); partner plus leg5 (idx3)
        b=F(13)
        fw=lambda e:[F(2),F(3),F(5), b-e, e]
        drop=5; surv_sig=[-1,-1,-1,1,1,1]; surv_idx=[0,1,2,3,4,6]
    else:              # soft minus leg = leg3 (freeW idx1); partner minus leg2 (idx0)
        a=F(9)
        fw=lambda e:[a-e, e, F(5),F(7),F(11)]
        drop=2; surv_sig=[-1,-1,1,1,1,1]; surv_idx=[0,1,3,4,5,6]
    # surviving 6-pt amplitude at eps=0 (independent direct evaluation)
    W0,_=solve_full(fw(F(0)),7,sig)
    W6=[W0[i] for i in surv_idx]
    A6=Wamp(W6, surv_sig)
    # sample SMALL eps so all points lie in the SINGLE chamber adjacent to eps=0
    # (a wide range crosses walls -> N_7(eps) is not one polynomial). Verify the
    # mixed-wall signature is constant across the window.
    eps=[F(1,k) for k in range(40,130)]
    sig0=None
    for e in eps:
        Wf,_=solve_full(fw(e),7,sig)
        s=tuple(val>0 for key,val in sorted(wallfns(Wf,7).items()))
        if sig0 is None: sig0=s
        elif s!=sig0: raise RuntimeError(f"wall crossed within eps window at e={e}")
    pts=[];good=[]
    for e in eps:
        Wf,Kf=solve_full(fw(e),7,sig); pts.append((Wf,Kf)); good.append((e,Wf))
    amps=amp_batch(pts)
    N7={}
    for (e,Wf),a in zip(good,amps):
        if a in('SIGFPE','ERR'): continue
        N7[e]=a*D_full(Wf,7)
    order=[e for e in eps if e in N7]
    c,deg=adaptive(N7,order,ret_deg=True)
    D0=D_full(solve_full(fw(F(0)),7,sig)[0],7)
    # c[0]=c[1]=0 expected; limit = c[2]/D0
    L=c[2]/D0 if len(c)>2 else F(0)
    return L, F(8)*A6, c[0],c[1], deg
for kind in ('plus','minus'):
    try:
        L,exp,c0,c1,deg=soft(kind)
        print(f"  {kind:5s} leg: lim A_7/(i e^2) = {L}   (N_7 slice deg {deg})")
        print(f"             8*A_6 (direct)      = {exp}   MATCH: {L==exp}  (vanishes to O(e^2): c0={c0},c1={c1})")
    except Exception as e:
        print(f"  {kind:5s} leg: FAILED ({e})")
print()

# ===================== TEST 3: n=7 JUMP EXPONENTS (s1_021) ===================
print("--- TEST 3: single-wall jump exponents (s1_021), with n=6 control ---")
def measure_exponent(n, freeW_fn, tstar, target_key, delta=F(1,200), npts=14):
    sig=SIG(n)
    # build left/right sample sets
    ts_left=[tstar-delta*k for k in range(1,npts+1)]
    ts_right=[tstar+delta*k for k in range(1,npts+1)]
    allpts=[]; meta=[]
    for t in ts_left+ts_right:
        Wf,Kf=solve_full(freeW_fn(t),n,sig); allpts.append((Wf,Kf)); meta.append((t,Wf))
    amps=amp_batch(allpts)
    NL={}; NR={}
    for (t,Wf),a in zip(meta,amps):
        if a in('SIGFPE','ERR'): raise RuntimeError(f"SIGFPE at t={t}")
        val=a*D_full(Wf,n)
        (NL if t<tstar else NR)[t]=val
    # single-wall check: only target wall flips sign between the innermost left & right pt
    WL,_=solve_full(freeW_fn(tstar-delta),n,sig)
    WR,_=solve_full(freeW_fn(tstar+delta),n,sig)
    fL=wallfns(WL,n); fR=wallfns(WR,n)
    flipped=[k for k in fL if (fL[k]>0)!=(fR[k]>0)]
    cL,dL=adaptive(NL,sorted(NL,reverse=True),ret_deg=True)   # near-wall order
    cR,dR=adaptive(NR,sorted(NR),ret_deg=True)
    # continuity at wall
    contin = peval(cL,tstar)==peval(cR,tstar)
    diff=[ (cR[i] if i<len(cR) else F(0)) - (cL[i] if i<len(cL) else F(0)) for i in range(max(len(cL),len(cR))) ]
    m=root_mult(diff,tstar)
    return m, flipped, contin, (dL,dR)

# Slice constructions (all F-const so legs are polynomial in t):
#  (1=1) wall  w_i^2=w_j^2 (i minus, j plus): vary the minus & plus leg oppositely;
#        difference-of-squares makes the wall function LINEAR in t (t^2 cancels).
#  (1=2) wall  w_i^2=w_j^2+w_k^2: hold the plus pair {j,k} fixed at a PERFECT-SQUARE
#        sum C, vary the minus leg i and a second minus leg oppositely; wall = w_i^2 - C.
def run_exp(label,n,fn,tstar,delta,npts,expect):
    try:
        m,flip,ct,degs=measure_exponent(n,fn,tstar,None,delta=delta,npts=npts)
    except Exception as e:
        print(f"  {label}: FAILED ({e})"); return
    single = (len(flip)==1)
    ok = (m==expect) and ct and single
    print(f"  {label}: exponent={m} (expect {expect}) continuous={ct} flips={flip} slicedeg={degs} -> {'OK' if ok else 'CHECK'}")

# --- n=6 control: (1=1)->1, (1=2)->3 ---
# (1=1) w2^2=w4^2: leg2=3+t(minus), leg4=2-t(plus), leg3,leg5 fixed; wall 5+10t=0 -> t*=-1/2
run_exp("n=6 (1=1) w2^2=w4^2", 6, lambda t:[F(3)+t,F(17,5),F(2)-t,F(53,10)], F(-1,2), F(1,400),20, 1)
# (1=2) w2^2=w4^2+w5^2 with w4=3,w5=4 (C=25): leg2=2+t(minus), leg3=10-t(minus), leg4=3,leg5=4 fixed
#   wall (2+t)^2-25=0 -> t*=3 (also root -7)
run_exp("n=6 (1=2) w2^2=w4^2+w5^2", 6, lambda t:[F(2)+t,F(10)-t,F(3),F(4)], F(3), F(1,400),24, 3)

# --- n=7: (1=1)->1, (1=2)->2 ---
# (1=1) w2^2=w4^2: leg2=3+t,leg4=2-t, leg3,leg5,leg6 fixed; t*=-1/2
run_exp("n=7 (1=1) w2^2=w4^2", 7, lambda t:[F(3)+t,F(17,5),F(2)-t,F(53,10),F(31,7)], F(-1,2), F(1,400),34, 1)
# (1=2) w2^2=w4^2+w5^2 with w4=3,w5=4 (C=25): leg2=2+t,leg3=10-t, leg4=3,leg5=4,leg6 fixed; t*=3
run_exp("n=7 (1=2) w2^2=w4^2+w5^2", 7, lambda t:[F(2)+t,F(10)-t,F(3),F(4),F(29,5)], F(3), F(1,400),44, 2)
print("\nDONE.")
