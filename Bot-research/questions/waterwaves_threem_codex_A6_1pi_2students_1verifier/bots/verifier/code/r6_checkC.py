"""
CHECK C -- run the BLOCKED cure test on student-2's active two-block candidate
R_q^cand (s2_011), independently, at the brick level.

Logic: if the candidate brick H_mp is the correct q-wall jump, then
  T = S - R_q^cand
must be SMOOTH across every isolated q_{mp}=0 wall (all q-jumps removed, leaving
the global smooth R_0). If T still JUMPS across even one q-wall, the candidate is
wrong there -> reproduces student-1's obstruction for the active candidate.
This is a LOCAL test (per wall) and needs no R_0 fit: R_0 is smooth and cancels
from any jump.

Transcribed verbatim from bots/student-2/derivations/s2_011 (the WRITTEN blocks),
guarded against the round-3-verified same-energy brick F11 and against the
BG-extracted on-wall jump.
"""
from fractions import Fraction as Fr
from itertools import combinations
import r6_core as C
from r5_core import line, poly_interp, poly_eval, poly_divmod, SingularError
from r6_walls import wall_crossings
from r6_checkA import null_dirs, onshell_pt

M,P=[0,1,2],[3,4,5]

def H_cand(om, m, p):
    """student-2 s2_011 two-block brick for pair (m,p)."""
    a=om[m]; b=om[p]; q=b*b-a*a
    other_minus=[i for i in M if i!=m]
    other_plus =[i for i in P if i!=p]
    xm0,xm1=other_minus
    # s,v are symmetric functions of the two OTHER MINUS legs
    s=om[xm0]+om[xm1]; v=om[xm0]*om[xm1]
    F=a*s**3+v*(s*s-2*v)
    D=2*a**3+3*a*a*s+a*(s*s+v)-s*v
    core=F+(a+b)*D
    # four-leg beta selector
    four=other_minus+other_plus
    jmin=min(four, key=lambda i:abs(om[i]))
    if jmin in other_minus:
        y=om[jmin]; xother=[i for i in other_minus if i!=jmin][0]; x=om[xother]
        L=3*a*a+2*a*(s+b)-v+b*(2*x+y)
        return -32*y*y*core - 32*q*y*y*L + 32*x*b*q*q
    else:
        z=om[jmin]
        A0=a**4+4*a**3*b+4*a**3*z+4*a*a*b*b+6*a*a*b*z+a*b**3+2*a*b*b*z
        A1=4*a**3+8*a*a*b+7*a*a*z+5*a*b*b+7*a*b*z+b**3+b*b*z
        A2=3*a*a+4*a*b+3*a*z+b*b+b*z
        B0=3*a*a+2*a*b+a*z
        B1=3*a+b
        K=A0+s*A1+s*s*A2+v*B0+s*v*B1
        return -32*z*z*core + 32*q*K

def Rq_cand(om):
    tot=Fr(0)
    for m in M:
        for p in P:
            q=om[p]**2-om[m]**2
            if q>0:
                tot+=q*H_cand(om,m,p)
    return tot

def T_val(om):
    return C.S_resid(om) - Rq_cand(om)

# ---------- guard: on-wall trace ----------
def guard_same_energy():
    """At a same-energy point (b=a), core should equal the F11 poly, verified
    numerically at random kinematics."""
    import random
    rng=random.Random(11)
    ok=True
    for _ in range(20):
        a=Fr(rng.randint(-9,9),rng.randint(1,4));
        if a==0: continue
        s=Fr(rng.randint(-9,9)); v=Fr(rng.randint(-9,9))
        F=a*s**3+v*(s*s-2*v); D=2*a**3+3*a*a*s+a*(s*s+v)-s*v
        core=F+2*a*D
        f11=4*a**4+6*a**3*s+2*a*a*(s*s+v)+(a*s+v)*(s*s-2*v)
        if core!=f11: ok=False
    return ok

def _fit_side(fn,Pv,dv,ts):
    xs,ys=[],[]
    for t in ts:
        om=line(Pv,dv,t)
        try: y=fn(om)
        except (SingularError,RuntimeError) as e:
            if "SIGFPE" in str(e) or "rc=" in str(e) or isinstance(e,SingularError): continue
            raise
        xs.append(t); ys.append(y)
    if len(xs)<10: return None
    return poly_interp(xs[:9],ys[:9]), xs[9:], ys[9:]

def smooth_across(fn,Pv,dv,t0,half):
    L=_fit_side(fn,Pv,dv,[t0-Fr(1,50)-half*Fr(i,12) for i in range(1,12)])
    R=_fit_side(fn,Pv,dv,[t0+Fr(1,50)+half*Fr(i,12) for i in range(1,12)])
    if L is None or R is None: return None
    cL,xR,yR=R[0],R[1],R[2]  # note: use left-fit to predict right
    cLL,xLh,yLh=L
    # does the LEFT poly predict the RIGHT points?
    cross=max((abs(poly_eval(cLL,x)-y) for x,y in zip(xR,yR)),default=Fr(0))
    contin=abs(poly_eval(cLL,t0)-poly_eval(R[0],t0))
    return cross, contin

def main():
    import json,random
    print("Guard: core==F11 at same-energy:", guard_same_energy())
    # anchor sanity: Rq_cand at anchor, and T
    anchor=[Fr(-8),Fr(2),Fr(3),Fr(4),Fr(5),Fr(-6)]
    print("anchor: S =",C.S_resid(anchor)," Rq_cand =",Rq_cand(anchor)," T =",T_val(anchor))

    BASES=[[8,2,-3,-5,4,-6],[-8,2,3,4,5,-6],[10,-7,-6,-5,-4,12],
           [1,-21,-18,3,9,26],[-1,-28,-24,4,16,33],[-8,-7,-3,4,5,9],
           [-3,-14,-2,8,12,-1],[-1,-35,-10,-5,25,26]]
    results=[]
    n=0; S_jumps=0; T_smooth=0; T_jumps=0
    envs=set()
    for base in BASES:
        if not onshell_pt(base): continue
        for dv in null_dirs(base,3):
            cr=wall_crossings(base,dv,Fr(-1),Fr(1))
            for i,(tc,kind,lab) in enumerate(cr):
                if kind!="q": continue
                left=cr[i-1][0] if i>0 else Fr(-1)
                right=cr[i+1][0] if i+1<len(cr) else Fr(1)
                gap=min(tc-left,right-tc)
                if gap<Fr(1,4): continue
                half=min(gap*Fr(2,5),Fr(1,3))
                # environment: which q-block does the (m,p) brick use just left of wall?
                omw=line(base,dv,tc-Fr(1,80))
                m,p=lab
                other_minus=[i2 for i2 in M if i2!=m]; other_plus=[i2 for i2 in P if i2!=p]
                four=other_minus+other_plus
                jmin=min(four,key=lambda i2:abs(omw[i2]))
                block='minus' if jmin in other_minus else 'plus'
                sres=smooth_across(C.S_resid,base,dv,tc,half)
                tres=smooth_across(T_val,base,dv,tc,half)
                if sres is None or tres is None: continue
                n+=1
                sj = sres[0]!=0
                ts_smooth = (tres[0]==0 and tres[1]==0)
                if sj: S_jumps+=1
                if ts_smooth: T_smooth+=1
                else: T_jumps+=1
                envs.add((block,))
                results.append({"wall":lab,"t0":str(tc),"block":block,
                                "S_jumps":sj,"T_smooth":ts_smooth,
                                "T_cross_resid":str(tres[0]),"T_contin":str(tres[1])})
                if n>=18: break
            if n>=18: break
        if n>=18: break
    print(f"\nIsolated q-wall crossings tested: {n}")
    print(f"  S jumps across the q-wall (control):        {S_jumps}/{n}")
    print(f"  T = S - Rq_cand SMOOTH across the q-wall:    {T_smooth}/{n}")
    print(f"  T = S - Rq_cand still JUMPS (candidate WRONG):{T_jumps}/{n}")
    # split by block type
    for blk in ('minus','plus'):
        sub=[r for r in results if r['block']==blk]
        sm=sum(1 for r in sub if r['T_smooth'])
        print(f"    block={blk}: T smooth {sm}/{len(sub)}")
    print("\nExamples where T still jumps (candidate brick wrong):")
    for r in results:
        if not r['T_smooth']:
            print("   wall",r['wall'],"block",r['block'],"t0",r['t0'],
                  "T_cross_resid",r['T_cross_resid'])
    json.dump({"n":n,"S_jumps":S_jumps,"T_smooth":T_smooth,"T_jumps":T_jumps,
               "results":results}, open("../data/r6_checkC.json","w"),indent=1)

if __name__=="__main__":
    main()
