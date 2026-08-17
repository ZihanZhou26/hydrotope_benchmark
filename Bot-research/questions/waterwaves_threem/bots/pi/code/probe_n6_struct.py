#!/usr/bin/env python3
"""PI structural probe for the n=6 three-minus closed form.

Hypothesis family (S_3 wr Z_2 symmetric):  A_6 = i * c * g^{-3} * J
where J is built symmetrically from the two triples' truncated-power blocks
   P_-(t) = sum_{S subseteq {1,2,3}} (-1)^|S| (t - sum_{j in S} w_j^2)_+^2     (minus triple)
   P_+(t) = sum_{S subseteq {4,5,6}} (-1)^|S| (t - sum_{j in S} w_j^2)_+^2     (plus  triple)
Both supported on [0,Q], Q = sum_minus w^2 = sum_plus w^2 (equal on-shell).

Candidates tested for J (all exact, fractions):
  J0 = int_0^Q P_-(t) P_+(t) dt
  J1 = int_0^Q P_-'(t) P_+(t) dt   (and its swap; antisymmetric combo)
  J2 = int_0^Q P_-(t) P_+(t) dt / (w1^2..)  -- handled by checking ratio polynomiality
We compute A_6 from the oracle (exact) and the J's exactly, then look at A_6/(i*J).
If the ratio is constant (or a clean monomial) across points -> strong lead.
"""
import subprocess, re
from fractions import Fraction as F

BG="./bg"; SIG="-1,-1,-1,1,1,1"

def run_onshell(freeW):
    ws=",".join(str(F(w)) for w in freeW)
    out=subprocess.run([BG,"-n","6","-w",ws,"-s",SIG],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if out.returncode!=0: return None
    m=re.search(r"A_6 = i \* \(([-0-9/]+)\)",out.stdout)
    mo=re.search(r"omega = \{([^}]*)\}",out.stdout)
    om=[F(x.strip()) for x in mo.group(1).split(",")]
    return (F(m.group(1)), om) if m else None

def subset_sums_with_sign(ws):
    """list of (c_S, (-1)^|S|) for S subseteq the 3 weights ws (already squared)."""
    res=[]
    for mask in range(8):
        c=F(0); k=0
        for b in range(3):
            if mask&(1<<b): c+=ws[b]; k+=1
        res.append((c,(-1)**k))
    return res

def Pfun_pieces(ws):
    """Return list of (c_S, sign) so that P(t)=sum sign*(t-c_S)_+^2."""
    return subset_sums_with_sign(ws)

def integrate_product(minus_sq, plus_sq, Q, deriv_minus=False):
    """Exactly integrate over [0,Q] of P_-^(d)(t)*P_+(t) dt.
    P(t)=sum_i s_i (t-c_i)_+^2 ; P'(t)=sum_i s_i*2*(t-c_i)_+.
    On a subinterval, sum only over c_i <= t. Product is polynomial; integrate exactly."""
    Pm=Pfun_pieces(minus_sq); Pp=Pfun_pieces(plus_sq)
    bps=sorted(set([F(0),Q]+[c for c,_ in Pm if 0<=c<=Q]+[c for c,_ in Pp if 0<=c<=Q]))
    total=F(0)
    # integrate piecewise; represent polynomials as dict power->coeff
    def polymul(a,b):
        r={}
        for pa,ca in a.items():
            for pb,cb in b.items():
                r[pa+pb]=r.get(pa+pb,F(0))+ca*cb
        return r
    def polyint(p,lo,hi):
        s=F(0)
        for pw,c in p.items():
            s+=c*(hi**(pw+1)-lo**(pw+1))/(pw+1)
        return s
    for a,b in zip(bps[:-1],bps[1:]):
        mid=(a+b)/2
        # build P_- (or P_-') poly on this interval
        pm={}
        for c,s in Pm:
            if c<=mid:
                if deriv_minus:
                    # 2 s (t-c) = 2s*t - 2s*c
                    pm[1]=pm.get(1,F(0))+2*s; pm[0]=pm.get(0,F(0))-2*s*c
                else:
                    # s (t-c)^2 = s t^2 -2 s c t + s c^2
                    pm[2]=pm.get(2,F(0))+s; pm[1]=pm.get(1,F(0))-2*s*c; pm[0]=pm.get(0,F(0))+s*c*c
        pp={}
        for c,s in Pp:
            if c<=mid:
                pp[2]=pp.get(2,F(0))+s; pp[1]=pp.get(1,F(0))-2*s*c; pp[0]=pp.get(0,F(0))+s*c*c
        prod=polymul(pm,pp)
        total+=polyint(prod,a,b)
    return total

pts=[(F(2),F(3),F(5),F(7)),(F(3),F(5),F(2),F(4)),(F(1),F(4),F(6),F(3)),
     (F(5),F(2),F(7),F(3)),(F(3),F(3),F(4),F(5)),(F(1),F(2),F(3),F(5))]
print(f"{'point(w2,w3,w4,w5)':>22} {'A6/i':>16} {'J0':>16} {'A6/(i J0)':>22} {'A6/(i J1sym)':>22}")
for fw in pts:
    r=run_onshell(fw)
    if r is None:
        print(f"{str(fw):>22}  SIGFPE/skip"); continue
    A,om=r
    w=[x*x for x in om]  # squared, 0-indexed legs1..6
    minus_sq=[w[0],w[1],w[2]]; plus_sq=[w[3],w[4],w[5]]
    Q=sum(minus_sq)
    assert sum(plus_sq)==Q, (sum(plus_sq),Q)
    J0=integrate_product(minus_sq,plus_sq,Q)
    # antisymmetric derivative combo J1sym = int(P-' P+ - P+' P-) -- but that's d/dt(P-P+) -> 0. Use J1=int P-' P+
    J1=integrate_product(minus_sq,plus_sq,Q,deriv_minus=True)
    r0 = A/J0 if J0!=0 else None
    r1 = A/J1 if J1!=0 else None
    print(f"{str(fw):>22} {str(A):>16} {str(J0):>16} {str(r0):>22} {str(r1):>22}")
