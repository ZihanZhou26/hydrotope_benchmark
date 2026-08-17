from fractions import Fraction as Fr
import r6_core as C
from r5_core import line, poly_interp, poly_eval
from r6_walls import wall_crossings
from r6_checkA import null_dirs, onshell_pt
from r6_checkC import H_cand, Rq_cand
M,P=[0,1,2],[3,4,5]

def fit_side(fn,Pv,dv,ts):
    xs,ys=[],[]
    for t in ts:
        om=line(Pv,dv,t); xs.append(t); ys.append(fn(om))
    return poly_interp(xs[:9],ys[:9]), xs, ys

base=[8,2,-3,-5,4,-6]
assert onshell_pt(base)
done=False
for dv in null_dirs(base,3):
    cr=wall_crossings(base,dv,Fr(-1),Fr(1))
    for i,(tc,kind,lab) in enumerate(cr):
        if kind!="q": continue
        left=cr[i-1][0] if i>0 else Fr(-1); right=cr[i+1][0] if i+1<len(cr) else Fr(1)
        gap=min(tc-left,right-tc)
        if gap<Fr(1,4): continue
        m,p=lab
        half=min(gap*Fr(2,5),Fr(1,4))
        tsL=[tc-Fr(1,50)-half*Fr(k,10) for k in range(1,11)]
        tsR=[tc+Fr(1,50)+half*Fr(k,10) for k in range(1,11)]
        Scl,_,_=fit_side(C.S_resid,base,dv,tsL)
        Scr,_,_=fit_side(C.S_resid,base,dv,tsR)
        Rcl,_,_=fit_side(Rq_cand,base,dv,tsL)
        Rcr,_,_=fit_side(Rq_cand,base,dv,tsR)
        # per-brick contribution term_{m',p'}(om)=(q)_+ H_cand
        def term(mm,pp):
            def f(om):
                q=om[pp]**2-om[mm]**2
                return q*H_cand(om,mm,pp) if q>0 else Fr(0)
            return f
        print(f"crossing wall={lab} t0={tc}  dv={[str(x) for x in dv]}")
        # jumps: predict other side with this side's poly at a test point on the other side
        tR=tsR[0]
        print("  S:   left-poly(tR)-S(tR) =", poly_eval(Scl,tR)-C.S_resid(line(base,dv,tR)))
        print("  Rq:  left-poly(tR)-Rq(tR)=", poly_eval(Rcl,tR)-Rq_cand(line(base,dv,tR)))
        # per-brick: does each brick term's left-fit predict the right point?
        for mm in M:
            for pp in P:
                tcl,_,_=fit_side(term(mm,pp),base,dv,tsL)
                jump=poly_eval(tcl,tR)-term(mm,pp)(line(base,dv,tR))
                tag=""
                if (mm,pp)==(m,p): tag=" <-- the crossed wall"
                if jump!=0: print(f"    brick({mm},{pp}) term jump = {jump}{tag}")
        # also compute S jump minus (m,p) term jump
        done=True; break
    if done: break
