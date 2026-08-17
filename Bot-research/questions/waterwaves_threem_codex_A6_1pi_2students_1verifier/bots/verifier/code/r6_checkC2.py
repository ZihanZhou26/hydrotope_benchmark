"""
CHECK C2 -- diagnostic: extract the true q-brick from BG and localize where
student-2's candidate fails.

At an isolated q_{mp}=0 crossing, both sides of S are degree-8 polynomials in t.
The jump  J(t) = S_{q>0}(t) - S_{q<0}(t)  must be divisible by q_{mp}(t); the
quotient  H_extract(t) = J(t)/q_{mp}(t)  is the TRUE brick along the line.
Compare:
  * H_extract(t0) vs the block-independent on-wall trace -32 beta^2 [F+(a+b)D]
    (GUARD: this generalizes the round-3-verified F11 same-energy brick),
  * H_extract(t) vs student-2 H_cand(omega(t)) OFF the wall (tests the L/K blocks).
"""
from fractions import Fraction as Fr
import r6_core as C
from r5_core import line, poly_interp, poly_eval, poly_divmod, SingularError
from r6_walls import wall_crossings
from r6_checkA import null_dirs, onshell_pt
from r6_checkC import H_cand
M,P=[0,1,2],[3,4,5]

def onwall_trace(om,m,p):
    a=om[m]; b=om[p]
    om_=om
    other_minus=[i for i in M if i!=m]
    s=om_[other_minus[0]]+om_[other_minus[1]]; v=om_[other_minus[0]]*om_[other_minus[1]]
    F=a*s**3+v*(s*s-2*v); D=2*a**3+3*a*a*s+a*(s*s+v)-s*v
    beta2=min(min(om_[i]**2 for i in other_minus), min(om_[i]**2 for i in [j for j in P if j!=p]))
    return -32*beta2*(F+(a+b)*D)

def q_poly(Pv,dv,m,p):
    # q_{mp}(t)=w_p(t)^2-w_m(t)^2, coeffs low->high
    Pp,dp=Fr(Pv[p]),Fr(dv[p]); Pm,dm=Fr(Pv[m]),Fr(dv[m])
    return [Pp*Pp-Pm*Pm, 2*(Pp*dp-Pm*dm), dp*dp-dm*dm]

def side_fit(Pv,dv,ts):
    xs,ys=[],[]
    for t in ts:
        om=line(Pv,dv,t)
        try: y=C.S_resid(om)
        except (SingularError,RuntimeError) as e:
            if "SIGFPE" in str(e) or "rc=" in str(e) or isinstance(e,SingularError): continue
            raise
        xs.append(t); ys.append(y)
    if len(xs)<9: return None
    return poly_interp(xs[:9],ys[:9])

def extract(Pv,dv,t0,m,p,half):
    # which side has q>0?
    qL = (line(Pv,dv,t0-Fr(1,60))[p]**2 - line(Pv,dv,t0-Fr(1,60))[m]**2)
    cLeft = side_fit(Pv,dv,[t0-Fr(1,50)-half*Fr(i,10) for i in range(1,11)])
    cRight= side_fit(Pv,dv,[t0+Fr(1,50)+half*Fr(i,10) for i in range(1,11)])
    if cLeft is None or cRight is None: return None
    # jump = S_{q>0} - S_{q<0}
    if qL>0:  # left side is q>0
        J=[a-b for a,b in zip(_pad(cLeft,9),_pad(cRight,9))]
    else:
        J=[a-b for a,b in zip(_pad(cRight,9),_pad(cLeft,9))]
    qp=q_poly(Pv,dv,m,p)
    quot,rem=poly_divmod(J,qp)
    rem=[c for c in rem if c!=0]
    return quot, (len(rem)==0), cLeft, cRight

def _pad(c,n):
    return c+[Fr(0)]*(n-len(c))

def main():
    BASES=[[8,2,-3,-5,4,-6],[-8,2,3,4,5,-6],[10,-7,-6,-5,-4,12],
           [1,-21,-18,3,9,26],[-1,-28,-24,4,16,33],[-8,-7,-3,4,5,9],
           [-3,-14,-2,8,12,-1],[-1,-35,-10,-5,25,26]]
    tested=0; onwall_ok=0; offwall_match=0; div_ok=0
    minus_blk=0; plus_blk=0
    examples=[]
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
                half=min(gap*Fr(2,5),Fr(1,4))
                m,p=lab
                res=extract(base,dv,tc,m,p,half)
                if res is None: continue
                quot,divok,cL,cR=res
                # on-wall value of H_extract at t0
                Hx_t0=poly_eval(quot,tc)
                omw=line(base,dv,tc)
                trace=onwall_trace(omw,m,p)
                on_ok=(Hx_t0==trace)
                # off-wall comparison at a generic t in the q>0 window
                toff=tc+ (half*Fr(1,2) if (line(base,dv,tc+Fr(1,60))[p]**2-line(base,dv,tc+Fr(1,60))[m]**2)>0 else -half*Fr(1,2))
                omoff=line(base,dv,toff)
                Hx_off=poly_eval(quot,toff); Hc_off=H_cand(omoff,m,p)
                off_ok=(Hx_off==Hc_off)
                # block type at wall
                other_minus=[i2 for i2 in M if i2!=m]; other_plus=[i2 for i2 in P if i2!=p]
                jmin=min(other_minus+other_plus,key=lambda i2:abs(omw[i2]))
                blk='minus' if jmin in other_minus else 'plus'
                tested+=1
                if divok: div_ok+=1
                if on_ok: onwall_ok+=1
                if off_ok: offwall_match+=1
                if blk=='minus': minus_blk+=1
                else: plus_blk+=1
                if len(examples)<6:
                    examples.append((lab,blk,str(tc),on_ok,off_ok,divok))
                if tested>=24: break
            if tested>=24: break
        if tested>=24: break
    print(f"Isolated q-wall crossings analyzed: {tested}  (minus-block {minus_blk}, plus-block {plus_blk})")
    print(f"  jump divisible by q_mp (order-1 jump): {div_ok}/{tested}")
    print(f"  H_extract(t0) == on-wall trace -32 b^2[F+(a+b)D] (GUARD/F11 general): {onwall_ok}/{tested}")
    print(f"  H_extract == student-2 H_cand OFF the wall (candidate correct): {offwall_match}/{tested}")
    print("  examples (wall, block, t0, onwall_ok, offwall_ok, divisible):")
    for e in examples: print("   ",e)

if __name__=="__main__":
    main()
