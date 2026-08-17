"""
CHECK C3 -- reconcile C (T jumps) with C2 (brick matches): test student-2's
R_q^cand at SAME-SECTOR magnitude ties |w_i|=|w_j| (i,j both minus or both plus).
These are NOT walls of S (S stays smooth), but the four-leg beta selector inside
H_cand flips its argmin there, so R_q^cand can jump spuriously.

Expect: S SMOOTH across an isolated same-sector tie, but R_q^cand JUMPS ->
the candidate injects a discontinuity where none exists -> S - R_q^cand not a
smooth global R_0 -> confirms student-1's obstruction.
"""
from fractions import Fraction as Fr
from itertools import combinations
import r6_core as C
from r5_core import line, poly_interp, poly_eval, SingularError
from r6_walls import wall_crossings
from r6_checkA import null_dirs, onshell_pt
from r6_checkC import Rq_cand
M,P=[0,1,2],[3,4,5]

def samesector_ties(Pv,dv,t_lo,t_hi):
    """crossings of w_i^2 - w_j^2 = 0 for SAME-sector pairs (i,j)."""
    import math
    out=[]
    def roots(coeffs):
        c=[Fr(x) for x in coeffs]
        while len(c)>1 and c[-1]==0: c.pop()
        if len(c)==2: return [-c[0]/c[1]]
        if len(c)==3:
            a,b,cc=c[2],c[1],c[0]; disc=b*b-4*a*cc
            if disc<0: return []
            dn,dd=disc.numerator,disc.denominator
            rn=math.isqrt(dn); rd=math.isqrt(dd)
            if rn*rn==dn and rd*rd==dd:
                sq=Fr(rn,rd); return [(-b+sq)/(2*a),(-b-sq)/(2*a)]
            return []
        return []
    for sector in (M,P):
        for i,j in combinations(sector,2):
            Pi,di=Fr(Pv[i]),Fr(dv[i]); Pj,dj=Fr(Pv[j]),Fr(dv[j])
            coeffs=[Pi*Pi-Pj*Pj, 2*(Pi*di-Pj*dj), di*di-dj*dj]
            for r in roots(coeffs):
                if t_lo<r<t_hi: out.append((r,(i,j)))
    return out

def side_fit(fn,Pv,dv,ts):
    xs,ys=[],[]
    for t in ts:
        om=line(Pv,dv,t)
        try: y=fn(om)
        except (SingularError,RuntimeError) as e:
            if "SIGFPE" in str(e) or "rc=" in str(e) or isinstance(e,SingularError): continue
            raise
        xs.append(t); ys.append(y)
    if len(xs)<9: return None
    return poly_interp(xs[:9],ys[:9]), xs[9:], ys[9:]

def jump_across(fn,Pv,dv,t0,half):
    L=side_fit(fn,Pv,dv,[t0-Fr(1,50)-half*Fr(i,10) for i in range(1,11)])
    R=side_fit(fn,Pv,dv,[t0+Fr(1,50)+half*Fr(i,10) for i in range(1,11)])
    if L is None or R is None: return None
    cross=max((abs(poly_eval(L[0],x)-y) for x,y in zip(R[1],R[2])),default=Fr(0))
    return cross

def allwall_ts(Pv,dv):
    return [tc for tc,_,_ in wall_crossings(Pv,dv,Fr(-1),Fr(1))]

def main():
    BASES=[[8,2,-3,-5,4,-6],[-8,2,3,4,5,-6],[10,-7,-6,-5,-4,12],
           [1,-21,-18,3,9,26],[-1,-28,-24,4,16,33],[-8,-7,-3,4,5,9],
           [-3,-14,-2,8,12,-1],[-1,-35,-10,-5,25,26]]
    tested=0; S_smooth=0; Rq_jumps=0
    ex=[]
    for base in BASES:
        if not onshell_pt(base): continue
        for dv in null_dirs(base,3):
            qQ=allwall_ts(base,dv)
            for tc,pair in samesector_ties(base,dv,Fr(-1),Fr(1)):
                # isolation from q/Q walls AND other ties
                near=min([abs(tc-x) for x in qQ]+[Fr(10)])
                if near<Fr(1,4): continue
                half=min(near*Fr(2,5),Fr(1,4))
                # confirm w_i,w_j opposite sign at tie (the x=-y case) -> the interesting one
                om=line(base,dv,tc); i,j=pair
                opp = (om[i]*om[j]<0)
                ss=jump_across(C.S_resid,base,dv,tc,half)
                rq=jump_across(Rq_cand,base,dv,tc,half)
                if ss is None or rq is None: continue
                tested+=1
                if ss==0: S_smooth+=1
                if rq!=0: Rq_jumps+=1
                if len(ex)<10:
                    ex.append((pair,('minus' if i in M else 'plus'),str(tc),opp,
                               'Ssmooth' if ss==0 else 'SJUMP',
                               'RqJUMP' if rq!=0 else 'Rqsmooth'))
                if tested>=20: break
            if tested>=20: break
        if tested>=20: break
    print(f"Isolated SAME-SECTOR magnitude ties tested: {tested}")
    print(f"  S smooth across the tie (not a wall of S): {S_smooth}/{tested}")
    print(f"  R_q^cand JUMPS across the tie (spurious): {Rq_jumps}/{tested}")
    print("  examples (pair, sector, t0, opposite-sign, S, Rq):")
    for e in ex: print("   ",e)

if __name__=="__main__":
    main()
