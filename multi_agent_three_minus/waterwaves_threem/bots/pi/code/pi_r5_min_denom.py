#!/usr/bin/env python3
"""
PI round-5 INDEPENDENT verification of round-4 load-bearing claims (EXACT rational,
own oracle, no student code).  Uses finite differences on arithmetic-progression
slices (fast + exact).

  s1_011: D9 = prod_{i in M,j in P}(w_i+w_j) = (e3m+e3p)^3 on the manifold.
  s1_012: MINIMAL denominator of A_6 = (e3m+e3p)^1 (single cubic, simple pole);
          A_6 = i 2^5 g^-3 N/(e3m+e3p), N a degree-11 spline.
  s1_013 / s2_004: smoothness across walls: (1=1) -> C^0 kink, (1=2) -> C^2 (cubic) kink.
"""
import subprocess, re, sys
from fractions import Fraction as F
import sympy as sp

BG = "./bg"

def oracle_onshell(n, freeW, signs, g=1):
    ws = ",".join(str(x) for x in freeW); ss = ",".join(str(s) for s in signs)
    out = subprocess.run([BG,"-n",str(n),"-w",ws,"-s",ss,"-g",str(g)],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if out.returncode != 0:
        raise RuntimeError("oracle fail (wall?)")
    txt = out.stdout
    m = re.search(r"omega = \{([^}]*)\}", txt)
    omg = [F(s.strip()) for s in m.group(1).split(",")]
    m = re.search(r"A_%d = i \* \(([^)]*)\)"%n, txt)
    if not m:
        m2 = re.search(r"A_%d = \(([^)]*)\) \+ i \* \(([^)]*)\)"%n, txt)
        if m2 and F(m2.group(1))==0: return F(m2.group(2)), omg
        raise RuntimeError("parse fail: "+txt)
    return F(m.group(1)), omg

def e3(a,b,c): return a*b*c

def poly_degree_fd(vals, maxdeg=30):
    """minimal degree d s.t. finite-difference Delta^{d+1}=0 (exact), else None."""
    cur = list(vals)
    for m in range(0, maxdeg+2):
        if len(cur)==0: return None
        if all(x==0 for x in cur):
            return m-1
        if len(cur) < 2: return None
        cur = [cur[i+1]-cur[i] for i in range(len(cur)-1)]
    return None

# ============================================================
print("="*70); print("CHECK 1 (s1_011): D9 = (e3m+e3p)^3 on the manifold"); print("="*70)
# symbolic
w1,w2,w3,w4,w5,w6 = sp.symbols('w1 w2 w3 w4 w5 w6'); x=sp.symbols('x')
Q=(x+w4)*(x+w5)*(x+w6); pm=(x-w1)*(x-w2)*(x-w3)
w1sol=-(w2+w3+w4+w5+w6)
cons2=(-w1sol**2-w2**2-w3**2+w4**2+w5**2+w6**2)
w6sol=sp.solve(cons2.subs(w1,w1sol),w6)[0]
d_on=sp.simplify((Q-pm).subs(w1,w1sol).subs(w6,w6sol))
const = sp.simplify(sp.diff(d_on,x))==0
target=sp.simplify((w1*w2*w3+w4*w5*w6).subs(w1,w1sol).subs(w6,w6sol))
eq=sp.simplify(d_on-target)==0
print("  symbolic: Q-p_- is x-independent on manifold:",const,"; equals e3m+e3p:",eq)
# numeric exact vs oracle kinematics
pts=[[F(2),F(3),F(5),F(7)],[F(2),F(3),F(5,2),F(11,3)],[F(-3),F(4),F(5),F(-2)],
     [F(7),F(-1),F(13,5),F(-9,4)],[F(10),F(1),F(2),F(3)],[F(-5),F(-7,2),F(8),F(13,2)]]
ok=tot=0
for fw in pts:
    try: A,omg=oracle_onshell(6,fw,[-1,-1,-1,1,1,1])
    except RuntimeError: continue
    tot+=1; W1,W2,W3,W4,W5,W6=omg
    D9=1
    for i in (W1,W2,W3):
        for j in (W4,W5,W6): D9*=(i+j)
    cube=(e3(W1,W2,W3)+e3(W4,W5,W6))**3
    ok+= (D9==cube)
print("  numeric exact (oracle legs): D9==(e3m+e3p)^3 at %d/%d points"%(ok,tot))

# ============================================================
print(); print("="*70)
print("CHECK 2 (s1_012): minimal denominator (e3m+e3p)^1, N deg 11"); print("="*70)
# F-const slice, ONE chamber: legs2,3 fixed; w4=a+t, w5=b-t (sumFree const)
fixed=[F(3),F(5,2)]; a=F(5); b=F(7)
ts=[F(k,24) for k in range(-12,13)]   # 25 pts, |t|<=0.5, one chamber
sl=[]
for t in ts:
    try: A,omg=oracle_onshell(6,fixed+[a+t,b-t],[-1,-1,-1,1,1,1]); sl.append((t,A,omg))
    except RuntimeError: pass
print("  slice points (one chamber):",len(sl))
A6=[A for (_,A,_) in sl]
D=[e3(*omg[:3])+e3(*omg[3:]) for (_,_,omg) in sl]
sumF=[sum(omg[1:5]) for (_,_,omg) in sl]
dA6=poly_degree_fd(A6,28)
dN =poly_degree_fd([A*d for A,d in zip(A6,D)],28)
dN3=poly_degree_fd([A*d**3 for A,d in zip(A6,D)],28)
dD =poly_degree_fd(D,6)
dSF=poly_degree_fd(sumF,4)
print("  A_6(t) polynomial?              ->", "deg %d"%dA6 if dA6 is not None else "NO (rational) <-- expected")
print("  A_6(t)*(e3m+e3p)(t) polynomial? ->", "deg %d"%dN if dN is not None else "NO", "  <-- expect YES")
print("  A_6(t)*(e3m+e3p)^3 polynomial?  ->", "deg %d"%dN3 if dN3 is not None else "NO", "  (D9 over-clears)")
print("  (e3m+e3p)(t) degree in t:",dD,"   sumFree(t) degree:",dSF,"(0 => F-const slice OK)")
verdict = (dA6 is None) and (dN is not None)
print("  => pole order exactly 1 (A_6 not poly, one factor (e3m+e3p) clears it):",verdict)

# homogeneity: A_6 degree 8 => N = A_6*(e3m+e3p) degree 8+3 = 11
A_1,_=oracle_onshell(6,[F(2),F(3),F(5),F(7)],[-1,-1,-1,1,1,1])
A_2,_=oracle_onshell(6,[F(4),F(6),F(10),F(14)],[-1,-1,-1,1,1,1])
print("  homogeneity: A_6(2*w)/A_6(w) =",A_2/A_1,"(expect 2^8=256) => deg A_6=8, deg N=8+3=11:",A_2/A_1==256)

# ============================================================
print(); print("="*70)
print("CHECK 3 control: n=5 (known polynomial) returns POLYNOMIAL"); print("="*70)
# n=5: minus 1,2,3 ; plus 4,5. free legs 2,3,4. slice: leg2 fixed; w3=a+t,w4=b-t
f2=[F(2)]; a3=F(3); b4=F(11,2)
sl5=[]
for t in [F(k,24) for k in range(-12,13)]:
    try: A,omg=oracle_onshell(5,[F(2),a3+t,b4-t],[-1,-1,-1,1,1]); sl5.append(A)
    except RuntimeError: pass
d5=poly_degree_fd(sl5,12)
print("  n=5 A_5(t) polynomial? ->", "deg %d"%d5 if d5 is not None else "NO","(expect YES ~deg 6)")

# ============================================================
print(); print("="*70)
print("CHECK 4 (s1_013/s2_004): cross-wall smoothness orders"); print("="*70)
def kink_order(center_t, half, fixed, a, b, wallname):
    """N=A_6*(e3m+e3p) is a genuine degree-6 polynomial in t per chamber. Fit the
       exact degree-6 polynomial in s=t-center on each side of the wall, compare
       Taylor coefficients. Lowest differing order k = jump exponent p of N.
       A_6 = N/(e3m+e3p) has the same kink order since (e3m+e3p)!=0 at these walls."""
    deg=6; npts=deg+1
    h=half/F(npts)
    def side_fit(sgn):
        rows=[]
        for k in range(1,npts+1):
            t=center_t+sgn*k*h; s=sgn*k*h
            A,omg=oracle_onshell(6,fixed+[a+t,b-t],[-1,-1,-1,1,1,1])
            N=A*(e3(*omg[:3])+e3(*omg[3:]))
            rows.append((s,N))
        S=sp.Matrix([[sp.Rational((s**j).numerator,(s**j).denominator) for j in range(deg+1)] for (s,_) in rows])
        v=sp.Matrix([sp.Rational(N.numerator,N.denominator) for (_,N) in rows])
        return list(S.solve(v))
    cl=side_fit(-1); cr=side_fit(1)
    order=None
    for k in range(deg+1):
        if sp.simplify(cl[k]-cr[k])!=0: order=k; break
    diffs=[sp.simplify(cl[k]-cr[k]) for k in range(deg+1)]
    print("  %-8s  Taylor-coeff differences L-R (k=0..6): %s"%(wallname,[0 if d==0 else 'NONZERO' for d in diffs]))
    print("  -> lowest differing order k=%s  (k=1 => C^0/first-deriv kink; k=3 => C^2 cubic kink)"%order)
    return order

# (1=1) wall: w4 = w2 (mixed, minus leg2 vs plus leg4). fixed legs (2,3)=(3, 5/2): w4 hits 3 at t=-2 from a=5 -> too far. Use anchor with a near 3.
# choose fixed=(w2,w3)=(3, 5/2), a=5/2,b=7 so w4=5/2+t crosses w2=3 at t=1/2 inside.
print(" (1=1) wall  w4=w2=3  (D9 != 0 there):")
o11=kink_order(F(1,2), F(3,10), [F(3),F(5,2)], F(5,2), F(7), "(1=1)")
# (1=2) wall: w4^2 = w2^2+w3^2.  with (w2,w3)=(3,5/2): w4^2=9+25/4=61/4 -> w4=sqrt(61)/2~3.905.
# pick a,b so w4=a+t hits ~3.905 near t=0.  a=39/10,b=7 -> w4=3.9+t, crosses at t=sqrt(61)/2-3.9 ~ .005 -> too close; use rational wall instead:
# choose (w2,w3)=(4,3): w4^2=16+9=25 -> w4=5 exactly (rational wall). a=5? then t=0 on wall (SIGFPE). use a=24/5,b=7: w4=24/5+t crosses 5 at t=1/5.
print(" (1=2) wall  w4^2=w2^2+w3^2 (w2,w3)=(4,3)->w4=5  (D9 != 0 there):")
o12=kink_order(F(1,5), F(1,12), [F(4),F(3)], F(24,5), F(7), "(1=2)")
print("  => numerator jump exponents: (1=1) p = k = %s ; (1=2) p = k = %s  (since denom != 0 at wall)"%(o11,o12))

print(); print("ALL CHECKS DONE.")
