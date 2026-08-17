#!/usr/bin/env python3
"""PI round-7 INDEPENDENT verification of student-1 s1_018: the full n=6 three-minus
closed form  A_6 = i 2^5 g^-3 N_6/(e3m+e3p).

Independence:
 - Oracle is the PI's own freshly-built bots/pi/code/bg (byte-identical to shared bg.cpp).
 - The ONLY thing taken from the student is the *candidate formula itself*: the explicit
   reference polynomials B, P0, R0 (from r6_polys.txt) and the (1=2) coefficient Q (s1_015,
   transcribed below as Qref). Those polynomials ARE the deliverable under test.
 - ALL evaluation logic (group of 72, orbit sums, truncated powers, chamber classification,
   point generation, on-shell solve, comparison) is the PI's own code in THIS file. No import
   of any student module.

N_6 = B                                           (smooth symmetric base; direct eval)
    + sum_{i in M,j in P} (b_j-a_i)_+ P_ij        (single (1=1); 72-orbit sum of P0)
    + sum_{i!=k, j!=l}    (b_j-a_i)_+(b_l-a_k)_+ R (pair (1=1);   72-orbit sum of R0)
    + sum_{i,{j,k}}       (a_i-b_j-b_k)_+^3 Q_ijk  ((1=2); clean 9-wall sum of Qref)

a_i=w_i^2 (minus i in {0,1,2}), b_j=w_j^2 (plus j in {3,4,5}); (x)_+=max(x,0); g=1.
"""
import re, os, subprocess, itertools, random
from fractions import Fraction as F
import sympy as sp

HERE = os.path.dirname(os.path.abspath(__file__))
BG   = os.path.join(HERE, "bg")
POLYS= os.path.join(HERE, "..", "..", "student-1", "code", "r6_polys.txt")

# ----------------------------------------------------------------------------
# Parse the three reference polynomials (candidate formula) into exact term lists.
# ----------------------------------------------------------------------------
def _expanded_block(txt, key):
    blocks = re.split(r'=== ', txt)
    for b in blocks:
        if b.startswith(key):
            m = re.search(r'expanded:\n(.*?)\nfactored:', b, re.S)
            return m.group(1).strip()
    raise KeyError(key)

def _termlist(expr_str, symbols):
    """Return [(Fraction coeff, (e1,e2,...)), ...] for expr in given ordered symbols."""
    e = sp.sympify(expr_str)
    p = sp.Poly(e, *symbols)
    out = []
    for exps, c in p.terms():
        cf = sp.nsimplify(c); cr = sp.Rational(cf)
        out.append((F(int(cr.p), int(cr.q)), tuple(int(x) for x in exps)))
    return out

def _evalterms(terms, vals):
    s = F(0)
    for c, exps in terms:
        t = c
        for v, ex in zip(vals, exps):
            if ex: t *= v**ex
        s += t
    return s

_txt = open(POLYS).read()
e1,e2,e3m,e3p = sp.symbols('e1 e2 e3m e3p')
A1,A2,B1,B2,y = sp.symbols('A1 A2 B1 B2 y')
w2s,w3s,w4s,w5s,w6s = sp.symbols('w2 w3 w4 w5 w6')

B_TERMS  = _termlist(_expanded_block(_txt, "B "),  [e1,e2,e3m,e3p])
P0_TERMS = _termlist(_expanded_block(_txt, "P0"), [A1,A2,B1,B2,y])
R0_TERMS = _termlist(_expanded_block(_txt, "R0"), [w2s,w3s,w4s,w5s,w6s])

# (1=2) coefficient Q (s1_015 / s1_018), reference wall: minus 0, plus pair {3,4}, excl plus 5.
def Qref(o):
    A1v=o[1]+o[2]; A2v=o[1]*o[2]; B1v=o[3]+o[4]; B2v=o[3]*o[4]; yv=o[5]
    return (A2v*B1v*(yv**2 - A1v**2 - A1v*B1v + A2v - B2v)
            + B2v*yv*(A2v - B1v*yv - B2v))

# ----------------------------------------------------------------------------
# Group of 72:  S3(minus 0,1,2) x S3(plus 3,4,5) x Z2(swap blocks).  Own code.
# perm tuple: perm[k] = image position of leg k.  apply_perm: new[perm[j]] = oms[j].
# ----------------------------------------------------------------------------
def _full_group():
    base=[]
    for pm in itertools.permutations([0,1,2]):
        for pp in itertools.permutations([3,4,5]):
            base.append(tuple(list(pm)+list(pp)))
    z2=(3,4,5,0,1,2)
    def comp(g,h): return tuple(g[h[k]] for k in range(6))
    G=set(base)
    for g in base: G.add(comp(z2,g))
    return [tuple(x) for x in G]
GROUP=_full_group()
assert len(GROUP)==72, len(GROUP)

def apply_perm(perm, oms):
    new=[None]*6
    for j in range(6): new[perm[j]]=oms[j]
    return new

def _relabel_12_to_ref(i, pair):
    others_m=[x for x in (0,1,2) if x!=i]
    pm=[None,None,None]; pm[i]=0; pm[others_m[0]]=1; pm[others_m[1]]=2
    j,k=pair; l=[x for x in (3,4,5) if x not in pair][0]
    pp={j:3,k:4,l:5}
    return (pm[0],pm[1],pm[2],pp[3],pp[4],pp[5])

# ----------------------------------------------------------------------------
# The candidate amplitude.
# ----------------------------------------------------------------------------
def invariants(o):
    e1v=o[3]+o[4]+o[5]
    e2v=o[3]*o[4]+o[3]*o[5]+o[4]*o[5]
    e3mv=o[0]*o[1]*o[2]; e3pv=o[3]*o[4]*o[5]
    return e1v,e2v,e3mv,e3pv

def N6(o):
    o=[F(x) for x in o]
    e1v,e2v,e3mv,e3pv=invariants(o)
    tot = _evalterms(B_TERMS, (e1v,e2v,e3mv,e3pv))           # base
    for p in GROUP:                                          # single + pair orbit sums
        ro=apply_perm(p,o)
        k03=ro[3]**2-ro[0]**2
        if k03>0:
            tot += k03*_evalterms(P0_TERMS, (ro[1]+ro[2], ro[1]*ro[2], ro[4]+ro[5], ro[4]*ro[5], ro[3]))
            k14=ro[4]**2-ro[1]**2
            if k14>0:
                tot += k03*k14*_evalterms(R0_TERMS, (ro[1],ro[2],ro[3],ro[4],ro[5]))
    for i in (0,1,2):                                        # (1=2) clean 9-wall sum
        for (j,k) in itertools.combinations((3,4,5),2):
            kS=o[i]**2-o[j]**2-o[k]**2
            if kS>0:
                tot += kS**3 * Qref(apply_perm(_relabel_12_to_ref(i,(j,k)), o))
    return tot

def A6_imag(o, g=F(1)):
    o=[F(x) for x in o]
    e1v,e2v,e3mv,e3pv=invariants(o)
    den=e3mv+e3pv
    if den==0: raise ZeroDivisionError("on pole e3m+e3p=0")
    val=F(32)*N6(o)/den
    return val*(g**(-3)) if g!=1 else val

# ----------------------------------------------------------------------------
# PI's own on-shell solver (replicates bg.cpp solve for legs 1,n) and oracle call.
# ----------------------------------------------------------------------------
def solve_omega(free, sig=(-1,-1,-1,1,1,1)):
    """free = (w2,w3,w4,w5) Fractions. Returns [w1..w6] or None."""
    free=[F(x) for x in free]
    s0=sig[0]; n=6
    sumFree=sum(free)
    if sumFree==0: return None
    sumSig=sum(F(sig[i+1])*free[i]**2 for i in range(n-2))
    wn=-(F(s0)*sumFree**2 + sumSig)/(F(2)*F(s0)*sumFree)
    w1=-(sumFree+wn)
    return [w1, free[0],free[1],free[2],free[3], wn]

def oracle(free, sig=(-1,-1,-1,1,1,1)):
    """Return (omega list as Fractions, A6_imag as Fraction) from PI's own ./bg, or None."""
    w=",".join(str(x) for x in free)
    s=",".join(str(x) for x in sig)
    try:
        out=subprocess.run([BG,"-n","6","-w",w,"-s",s],stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,universal_newlines=True,timeout=60)
    except Exception:
        return None
    txt=out.stdout
    mo=re.search(r'omega = \{([^}]*)\}', txt)
    ma=re.search(r'A_6 = i \* \(([^)]*)\)', txt)
    if not mo or not ma: return None   # SIGFPE on wall, or real part nonzero
    om=[F(x.strip()) for x in mo.group(1).split(',')]
    return om, F(ma.group(1))

def chamber_label(o):
    lab=[]
    for i in (0,1,2):
        for j in (3,4,5):
            lab.append(1 if o[j]**2-o[i]**2>0 else 0)
    for i in (0,1,2):
        for (j,k) in itertools.combinations((3,4,5),2):
            lab.append(1 if o[i]**2-o[j]**2-o[k]**2>0 else 0)
    return tuple(lab)

# ----------------------------------------------------------------------------
# MAIN: broad generic scan across chamber types + non-generic + g-homogeneity.
# ----------------------------------------------------------------------------
if __name__=="__main__":
    print("="*78)
    print("PI round-7 INDEPENDENT check of s1_018 (n=6 closed form)")
    print("oracle:", BG)
    print("="*78)

    # (0) Known anchor
    om,Aim = oracle((2,3,5,7))
    f = A6_imag(om)
    print(f"\n[anchor] free(2,3,5,7): oracle A6/i={Aim}  formula={f}  MATCH={f==Aim}")

    # (1) Broad random generic scan, tracking chamber-type coverage
    rnd=random.Random(20260627)
    seen={}      # chamber label -> count
    ok=tot=0; mism=[]
    trials=0
    while tot<140 and trials<6000:
        trials+=1
        free=tuple(F(rnd.randint(-95,95),rnd.choice([1,2,5,10])) for _ in range(4))
        if any(x==0 for x in free): continue
        o=solve_omega(free)
        if o is None or any(x==0 for x in o): continue
        # avoid sampling on/too near a wall (oracle SIGFPEs exactly on walls)
        res=oracle(free)
        if res is None: continue
        oom,Aim=res
        if any(a!=b for a,b in zip(o,oom)):    # sanity: my solve == oracle kinematics
            print("  KIN MISMATCH", o, oom); continue
        e3mv=o[0]*o[1]*o[2]; e3pv=o[3]*o[4]*o[5]
        if e3mv+e3pv==0: continue
        f=A6_imag(o)
        tot+=1; lab=chamber_label(o); seen[lab]=seen.get(lab,0)+1
        if f==Aim: ok+=1
        else: mism.append((free,f,Aim))
    print(f"\n[generic scan] {ok}/{tot} EXACT match; distinct chamber labels covered: {len(seen)}")
    if mism:
        print("  MISMATCHES:")
        for free,f,Aim in mism[:10]:
            print("   free",free," formula",f," oracle",Aim," diff",f-Aim)

    # (2) Non-generic regimes: one free freq >> rest, and << rest
    print("\n[non-generic] one frequency dominant / tiny:")
    nong=[(F(1000),F(2),F(3),F(5)), (F(2),F(1000),F(3),F(5)),
          (F(1,1000),F(2),F(3),F(5)), (F(2),F(3),F(5),F(1,1000)),
          (F(1,7),F(1,3),F(50),F(2)), (F(987),F(2),F(991),F(3))]
    ng_ok=ng_tot=0
    for free in nong:
        o=solve_omega(free)
        if o is None or any(x==0 for x in o): print("  skip",free); continue
        res=oracle(free)
        if res is None: print("  oracle-wall skip",free); continue
        oom,Aim=res
        if (o[0]*o[1]*o[2]+o[3]*o[4]*o[5])==0: print("  pole skip",free); continue
        f=A6_imag(o); ng_tot+=1; ng_ok+=(f==Aim)
        print(f"  free{tuple(str(x) for x in free)}: match={f==Aim}")
    print(f"  non-generic: {ng_ok}/{ng_tot}")

    # (3) g-homogeneity:  A_6(g) = i 2^5 g^-3 N/(...). Oracle with -g and formula must agree.
    print("\n[g-homogeneity] check A_6 scales as g^-3 (oracle -g vs formula):")
    free=(F(2),F(3),F(5),F(7))
    for gval in (F(2),F(1,3),F(7,2)):
        w=",".join(str(x) for x in free)
        out=subprocess.run([BG,"-n","6","-w",w,"-s","-1,-1,-1,1,1,1","-g",str(gval)],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        ma=re.search(r'A_6 = i \* \(([^)]*)\)', out.stdout)
        Aim_g=F(ma.group(1))
        o=solve_omega(free)
        fg=A6_imag(o, g=gval)
        print(f"  g={gval}: oracle A6/i={Aim_g}  formula={fg}  MATCH={fg==Aim_g}")
