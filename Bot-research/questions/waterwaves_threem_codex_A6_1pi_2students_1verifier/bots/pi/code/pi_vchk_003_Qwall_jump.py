#!/usr/bin/env python3
"""
pi_vchk_003 : independent PI confirmation that A_6 itself jumps across the
3-leg factorization / subset-momentum wall  Q_{1;46} = k_{{1,4,6}} = 0.

Method (fully independent of the students' and verifier's P_pole evaluators):
  * On-shell polynomial line w(t) = P + t d, P=(8,2,-3,-5,4,-6), d=(-2,1,0,2,-1,0).
    (verifier's line; re-checked on-shell here.)
  * momenta k_i = sigma_i w_i^2, sigma=(-,-,-,+,+,+), g=1.
  * A_6/i from a FRESH md5-matched bg  (--amp, exact rational).
  * C(t)=w1 w2 w3 + w4 w5 w6  (smooth deg-3, C!=0 on window).
  * N(t) = (A_6/i)*C(t) is a fixed polynomial (deg<=11) on ONE analytic cell.
  * Fit exact interpolating poly on 12 LEFT nodes; test 3 LEFT holdouts (control)
    and 3 RIGHT nodes (jump test). Cell-constancy of the magnitude order and all
    q_{mp}, Q_{m;pq} signs is certified on each side (only Q_{1;46} crosses).
Everything is exact (fractions). No numpy, no student code.
"""
import subprocess, sys
from fractions import Fraction as F
from itertools import combinations

BG = "bots/pi/code/bg"
P  = [F(8), F(2), F(-3), F(-5), F(4), F(-6)]
D  = [F(-2), F(1), F(0), F(2), F(-1), F(0)]
SIG= [-1,-1,-1,1,1,1]            # sector: legs 1,2,3 minus ; 4,5,6 plus
MIN= [0,1,2]; PLU=[3,4,5]        # 0-based leg indices

def w_of(t):  return [P[i] + t*D[i] for i in range(6)]

def onshell_line_ok():
    s0 = sum(D)
    s1 = sum(SIG[i]*P[i]*D[i] for i in range(6))
    s2 = sum(SIG[i]*D[i]*D[i] for i in range(6))
    e  = sum(P); em = sum(SIG[i]*P[i]*P[i] for i in range(6))
    return dict(sumP=e, energyP=em, sumd=s0, mixed=s1, quad=s2)

def C_of(w):  return w[0]*w[1]*w[2] + w[3]*w[4]*w[5]

def frac_arg(x):  # print a Fraction as an exact "p/q" string bg accepts
    return f"{x.numerator}/{x.denominator}" if x.denominator!=1 else str(x.numerator)

def bg_amp(w):
    k = [F(SIG[i])*w[i]*w[i] for i in range(6)]
    Ks=",".join(frac_arg(x) for x in k)
    Ws=",".join(frac_arg(x) for x in w)
    out=subprocess.run([BG,"--amp","-K",Ks,"-W",Ws,"-g","1"],
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                       universal_newlines=True)
    txt=out.stdout+out.stderr
    for ln in txt.splitlines():
        if ln.strip().startswith("A_6 = i *"):
            body=ln.split("i *",1)[1].strip().strip("()")
            if "/" in body:
                n,dn=body.split("/"); return F(int(n),int(dn))
            return F(int(body))
    raise RuntimeError("no A_6 parsed:\n"+txt)

def cell_signature(w):
    """magnitude sort order + signs of all q_mp and Q_{m;pq}."""
    order = tuple(sorted(range(6), key=lambda i: (abs(w[i]), i)))
    qsig={}
    for m in MIN:
        for p in PLU:
            v=w[p]*w[p]-w[m]*w[m]            # q_{mp}
            qsig[(m,p)] = (v>0)-(v<0)
    Qsig={}
    for m in MIN:
        for (p,q) in combinations(PLU,2):
            v=w[p]*w[p]+w[q]*w[q]-w[m]*w[m]  # Q_{m;pq}
            Qsig[(m,p,q)] = (v>0)-(v<0)
    return order,qsig,Qsig

# ---- exact polynomial interpolation (Lagrange, rational) ----
def interp_eval(nodes, vals, x):
    """value at x of the unique poly through (nodes,vals), exact."""
    tot=F(0)
    for i,(xi,yi) in enumerate(zip(nodes,vals)):
        term=yi
        for j,xj in enumerate(nodes):
            if i!=j: term*= (x-xj)/(xi-xj)
        tot+=term
    return tot

def main():
    print("=== on-shell line check ===")
    osk=onshell_line_ok()
    for k,v in osk.items(): print(f"  {k} = {v}")
    assert osk['sumP']==0 and osk['energyP']==0 and osk['sumd']==0 \
           and osk['mixed']==0 and osk['quad']==0, "line not on-shell"
    print("  -> w(t) exactly on-shell for all t.  Q_{1;46}(t)=", end="")
    # Q_{1;46} = w4^2+w6^2-w1^2 ; print as linear in t
    t=F(0); w=w_of(t); Q0=w[3]**2+w[5]**2-w[0]**2
    t=F(1); w=w_of(t); Q1=w[3]**2+w[5]**2-w[0]**2
    print(f"{Q0} + {Q1-Q0}*t  -> zero at t0={-Q0/(Q1-Q0)}")

    t0=F(1,4)
    fit_nodes  =[F(25-j,100) for j in range(1,13)]        # 0.24..0.13  (12, left)
    left_hold  =[F(235,1000),F(225,1000),F(215,1000)]     # left controls
    right_nodes=[F(26,100),F(27,100),F(28,100)]           # right jump test
    assert all(n<t0 for n in fit_nodes+left_hold) and all(n>t0 for n in right_nodes)

    # cell-constancy certification
    print("\n=== cell signature constancy ===")
    ref_left=cell_signature(w_of(fit_nodes[0]))
    for n in fit_nodes+left_hold:
        assert cell_signature(w_of(n))==ref_left, f"left cell breaks at t={n}"
    print(f"  LEFT  cell constant over {len(fit_nodes)+len(left_hold)} nodes; "
          f"mag order={ref_left[0]}")
    ref_right=cell_signature(w_of(right_nodes[0]))
    for n in right_nodes:
        assert cell_signature(w_of(n))==ref_right, f"right cell breaks at t={n}"
    print(f"  RIGHT cell constant over {len(right_nodes)} nodes; "
          f"mag order={ref_right[0]}")
    # which invariant flips across t0?
    dq=[k for k in ref_left[1] if ref_left[1][k]!=ref_right[1][k]]
    dQ=[k for k in ref_left[2] if ref_left[2][k]!=ref_right[2][k]]
    print(f"  q_mp sign flips L->R: {dq}")
    print(f"  Q_{{m;pq}} sign flips L->R: {dQ}   (expect only (0,3,5)=Q_1;46)")

    def N_of(t):
        w=w_of(t); return bg_amp(w)*C_of(w)

    print("\n=== fit N(t)=(A6/i)*C on 12 left nodes ===")
    fit_vals=[N_of(n) for n in fit_nodes]

    print("--- LEFT holdouts (control: must match) ---")
    ok_ctrl=True
    for n in left_hold:
        pred=interp_eval(fit_nodes,fit_vals,n); act=N_of(n)
        good=(pred==act); ok_ctrl&=good
        print(f"  t={float(n):+.3f}  match={good}  resid={act-pred}")

    print("--- RIGHT nodes (jump test: must FAIL if A6 jumps) ---")
    any_fail=False
    for n in right_nodes:
        pred=interp_eval(fit_nodes,fit_vals,n); act=N_of(n)
        good=(pred==act); any_fail|=(not good)
        print(f"  t={float(n):+.3f}  match={good}  resid={act-pred}")

    print("\n=== VERDICT ===")
    print(f"  left-holdout control passes : {ok_ctrl}")
    print(f"  right side breaks the fit   : {any_fail}")
    if ok_ctrl and any_fail:
        print("  => A_6 itself is a polynomial on the LEFT cell and JUMPS across")
        print("     Q_{1;46}=k_{1,4,6}=0.  Verifier finding V3 CONFIRMED independently.")
    else:
        print("  => inconclusive / verifier finding NOT reproduced -- investigate.")

if __name__=="__main__":
    main()
