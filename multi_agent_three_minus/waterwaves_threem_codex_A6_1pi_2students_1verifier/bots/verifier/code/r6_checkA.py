"""
CHECK A -- global re-confirmation of R_Q = -32 sum (Q_{m;pq})_+^3 w_m w_tbar.

On on-shell polynomial lines crossing an ISOLATED Q-wall (only one Q_T changes
sign in the window; no q-wall crossing nearby), verify:
  * R_spline JUMPS (left-fit poly fails on the right side)  -> genuine wall
  * S = R_spline - R_Q is a SINGLE degree-8 polynomial across the wall
    (holdouts pass on BOTH sides with the same left-fit; continuity at t0)
i.e. subtracting R_Q removes the order-3 Q-jump. Independent of any student code.
"""
from fractions import Fraction as Fr
from itertools import combinations, product
import r6_core as C
from r5_core import line, poly_interp, poly_eval, SingularError
from r6_walls import wall_crossings, sample_poly

M, P = [0,1,2],[3,4,5]
SIG = [-1,-1,-1,1,1,1]

def onshell_pt(P6):
    P6=[Fr(x) for x in P6]
    return sum(P6)==0 and sum(SIG[i]*P6[i]**2 for i in range(6))==0

def null_dirs(P6, rng=3):
    """All small-integer null tangent directions d at base P6:
       sum d = 0, sum sigma P d = 0, sum sigma d^2 = 0."""
    P6=[Fr(x) for x in P6]
    out=[]
    seen=set()
    for c in product(range(-rng,rng+1), repeat=6):
        if all(v==0 for v in c): continue
        d=[Fr(v) for v in c]
        if sum(d)!=0: continue
        if sum(SIG[i]*P6[i]*d[i] for i in range(6))!=0: continue
        if sum(SIG[i]*d[i]**2 for i in range(6))!=0: continue
        # canonical form: divide by gcd of numerators (they're ints here), fix sign
        from math import gcd
        g=0
        for v in c: g=gcd(g,abs(v))
        key=tuple(v//g for v in c)
        if key[0]<0 or (key[0]==0 and next((v for v in key if v!=0),0)<0):
            key=tuple(-v for v in key)
        if key in seen: continue
        seen.add(key)
        out.append([Fr(v) for v in key])
    return out

def test_isolated_Q(Pv, dv, t0, kind_label, half=Fr(1,3)):
    """At an isolated Q-crossing t0, fit deg-8 to R_spline and to S on the LEFT,
    test on the RIGHT. Returns dict of outcomes."""
    span=half
    # left/right windows, avoid the wall by a margin; generic sample points
    def wins(sign):
        base = t0 + sign*Fr(1,50)
        return [base + sign*span*Fr(i,20) for i in range(1,17)]
    resL = _fit_side(Pv,dv,wins(-1))
    resR = _fit_side(Pv,dv,wins(1))
    if resL is None or resR is None:
        return {"ok":False,"reason":"insufficient samples"}
    (rs_cL, s_cL, xsL, rsL, sL) = resL
    (rs_cR, s_cR, xsR, rsR, sR) = resR
    # R_spline: does left poly fail on right? (=> genuine jump)
    rs_jump = max((abs(poly_eval(rs_cL,x)-y) for x,y in zip(xsR,rsR)), default=Fr(0))
    # S: does left poly hold on right? (=> smooth, R_Q removed the jump)
    s_cross = max((abs(poly_eval(s_cL,x)-y) for x,y in zip(xsR,sR)), default=Fr(0))
    # continuity of S at t0 (both extrapolate to same value)
    s_contin = abs(poly_eval(s_cL,t0)-poly_eval(s_cR,t0))
    rs_contin = abs(poly_eval(rs_cL,t0)-poly_eval(rs_cR,t0))
    return {"ok":True,"label":kind_label,"t0":str(t0),
            "R_spline_jumps": rs_jump!=0,
            "S_smooth_across": s_cross==0,
            "S_continuous": s_contin==0,
            "R_spline_continuous": rs_contin==0,
            "rs_jump_resid":str(rs_jump),"s_cross_resid":str(s_cross)}

def _fit_side(Pv,dv,ts):
    xs,rs,ss=[],[],[]
    for t in ts:
        om=line(Pv,dv,t)
        try:
            rsp=C.R_spline(om); sv=rsp - C.R_Q(om)
        except (SingularError,RuntimeError) as e:
            if "SIGFPE" in str(e) or "rc=" in str(e) or isinstance(e,SingularError): continue
            raise
        xs.append(t); rs.append(rsp); ss.append(sv)
    if len(xs)<10: return None
    rs_c=poly_interp(xs[:9],rs[:9]); s_c=poly_interp(xs[:9],ss[:9])
    return (rs_c,s_c,xs[9:],rs[9:],ss[9:])

# ------- diverse on-shell bases spanning energy-sign chambers -------
BASES=[
    [8,2,-3,-5,4,-6],
    [-8,2,3,4,5,-6],
    [10,-7,-6,-5,-4,12],
    [1,-21,-18,3,9,26],
    [-1,-28,-24,4,16,33],
    [-8,-7,-3,4,5,9],
    [-3,-14,-2,8,12,-1],
    [-1,-35,-10,-5,25,26],
]

def esign(om):
    """energy-sign chamber = sign of each frequency."""
    return "".join('+' if om[i]>0 else '-' for i in range(6))

def main():
    import json
    results=[]
    nQ_tested=0; nQ_pass=0
    chambers=set(); channels=set(); esigns=set()
    for base in BASES:
        if not onshell_pt(base):
            print("SKIP non-onshell base", base); continue
        dirs=null_dirs(base, rng=3)
        per_base=0
        for dv in dirs:
            if per_base>=12: break
            # scan a window, find crossings
            t_lo,t_hi=Fr(-1),Fr(1)
            cr=wall_crossings(base,dv,t_lo,t_hi)
            # isolated Q crossing: a 'Q' crossing whose nearest neighbor crossing is far
            for i,(tc,kind,lab) in enumerate(cr):
                if kind!="Q": continue
                left = cr[i-1][0] if i>0 else t_lo
                right= cr[i+1][0] if i+1<len(cr) else t_hi
                gap=min(tc-left, right-tc)
                if gap < Fr(1,4):    # need isolation
                    continue
                half=min(gap*Fr(2,5), Fr(1,3))
                # record chamber signature just left of crossing
                omL=line(base,dv,tc-Fr(1,60))
                sigq=tuple(1 if C.q_wall(m,p,omL)>0 else -1 for m in M for p in P)
                res=test_isolated_Q(base,dv,tc,(base,[str(x) for x in dv],lab),half=half)
                if not res.get("ok"): continue
                nQ_tested+=1; per_base+=1
                good = res["R_spline_jumps"] and res["S_smooth_across"] and res["S_continuous"]
                if good: nQ_pass+=1
                chambers.add(sigq); channels.add(lab); esigns.add(esign(omL))
                res["chamber_qsig"]="".join('+' if s>0 else '-' for s in sigq)
                res["esign"]=esign(omL)
                results.append(res)
    print(f"Isolated Q-wall crossings tested: {nQ_tested}")
    print(f"  R_spline jumps AND S smooth AND S continuous: {nQ_pass}/{nQ_tested}")
    print(f"  distinct q-chambers touched: {len(chambers)}")
    print(f"  distinct triple channels (m;p,q) hit: {sorted(channels)}")
    print(f"  distinct energy-sign chambers: {sorted(esigns)}")
    bad=[r for r in results if not (r['R_spline_jumps'] and r['S_smooth_across'] and r['S_continuous'])]
    print(f"  FAILURES: {len(bad)}")
    for r in bad[:10]:
        print("   ", r)
    # show a few passing examples
    print("Sample passing crossings:")
    for r in results[:6]:
        print("   ", r["label"][2], "chamber",r["chamber_qsig"],
              "| Rspl jumps",r["R_spline_jumps"],"S smooth",r["S_smooth_across"],
              "S cont",r["S_continuous"])
    json.dump({"nQ_tested":nQ_tested,"nQ_pass":nQ_pass,
               "distinct_chambers":len(chambers),"failures":len(bad),
               "results":results},
              open("../data/r6_checkA.json","w"), indent=1)

if __name__=="__main__":
    main()
