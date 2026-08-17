#!/usr/bin/env python3
"""
pi_vchk_004 : independent PI resolution of the round-5 student<->verifier CONFLICT
on the ORDER-3 triple-wall brick G_{m;pq}.

  * student-2 (s2_010, post_020): G_{m;pq} = -16 max(w_m^2, w_t^2)  (t = omitted plus leg)
  * verifier  (V3, post_021):     G_{m;pq} = -32 w_m w_t           [REFUTES student-2]

Both agree ONLY where |w_m| = 2|w_t| (the canonical-line coincidence).  This check
extracts G on DISCRIMINATING crossings where w_m != 2 w_t, so the two candidate
formulas give different numbers, and reads off which one BG actually realizes.

Method (fully independent of both students' AND the verifier's evaluators):
  * Fresh md5-matched bg (--amp, exact rational).
  * P_pole implemented from the WRITTEN formula F9 (my own code).
  * R_spline(t) = A_6(t)/i - P_pole(t).
  * On an on-shell polynomial line w(t)=P+t d crossing exactly ONE Q_{m;pq}=0 wall
    inside a single 18-wall chamber (all nine q_mp signs and the other eight Q
    signs constant; only the target Q flips), interpolate the two degree-8 branch
    polynomials of R_spline, form the exact jump dR(t)=R_L(t)-R_R(t), and compare
    it to Q(t)^3 * G_cand(t) for each candidate G, exactly.
Everything exact (fractions).  No numpy, no student/verifier code imported.
"""
import subprocess, hashlib
from fractions import Fraction as F
from itertools import combinations

BG      = "bots/pi/code/bg"
BG_SRC  = "bots/pi/code/bg.cpp"
SIG     = [-1,-1,-1,1,1,1]          # legs 1,2,3 minus ; 4,5,6 plus (0-based)
MIN     = [0,1,2]; PLU=[3,4,5]

def md5(path):
    with open(path,"rb") as f: return hashlib.md5(f.read()).hexdigest()

def frac_arg(x):
    return f"{x.numerator}/{x.denominator}" if x.denominator!=1 else str(x.numerator)

def bg_amp_over_i(w):
    k=[F(SIG[i])*w[i]*w[i] for i in range(6)]
    out=subprocess.run([BG,"--amp","-K",",".join(frac_arg(x) for x in k),
                        "-W",",".join(frac_arg(x) for x in w),"-g","1"],
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    txt=out.stdout+out.stderr
    for ln in txt.splitlines():
        if ln.strip().startswith("A_6 = i *"):
            body=ln.split("i *",1)[1].strip().strip("()")
            if "/" in body:
                n,dn=body.split("/"); return F(int(n),int(dn))
            return F(int(body))
    raise RuntimeError("no A_6 parsed:\n"+txt)

# ---------- P_pole from the written formula F9 (my own implementation) ----------
def pos(x):  return x if x>0 else F(0)

def Hblock(b, c, d, w):
    wc2=w[c]*w[c]; wd2=w[d]*w[d]
    return pos(b) - pos(b-wc2) - pos(b-wd2) + pos(b-wc2-wd2)

def P_pole(w):
    tot=F(0)
    for m in MIN:
        mm=[x for x in MIN if x!=m]
        for (p,q) in combinations(PLU,2):
            pbar=[x for x in PLU if x not in (p,q)][0]
            QT=w[p]*w[p]+w[q]*w[q]-w[m]*w[m]
            if QT<=0: continue
            dT=2*(w[m]+w[p])*(w[m]+w[q])
            Hpq=Hblock(min(w[m]*w[m],QT), p, q, w)
            Hmm=Hblock(min(w[pbar]*w[pbar],QT), mm[0], mm[1], w)
            tot+=w[m]*w[pbar]*QT*QT/dT*Hpq*Hmm
    return -64*tot

def R_spline(w):  return bg_amp_over_i(w)-P_pole(w)

# ---------- exact cell signature (18-wall chamber) ----------
def cell_sig(w):
    order=tuple(sorted(range(6), key=lambda i:(abs(w[i]),i)))
    qs={}
    for m in MIN:
        for p in PLU:
            v=w[p]*w[p]-w[m]*w[m]; qs[(m,p)]=(v>0)-(v<0)
    Qs={}
    for m in MIN:
        for (p,q) in combinations(PLU,2):
            v=w[p]*w[p]+w[q]*w[q]-w[m]*w[m]; Qs[(m,p,q)]=(v>0)-(v<0)
    return order,qs,Qs

def lagrange(nodes, vals, x):
    tot=F(0)
    for i,(xi,yi) in enumerate(zip(nodes,vals)):
        term=yi
        for j,xj in enumerate(nodes):
            if i!=j: term*=(x-xj)/(xi-xj)
        tot+=term
    return tot

def analyze_line(P, D, chan, name, t_approx):
    """chan=(m,(p,q)); extract G across the single Q_chan=0 wall nearest t_approx."""
    m,(p,q)=chan
    pbar=[x for x in PLU if x not in (p,q)][0]
    def w_of(t): return [P[i]+t*D[i] for i in range(6)]
    def Qc(t):   w=w_of(t); return w[p]*w[p]+w[q]*w[q]-w[m]*w[m]

    osk=dict(sumP=sum(P), enP=sum(SIG[i]*P[i]*P[i] for i in range(6)),
             sumd=sum(D), mix=sum(SIG[i]*P[i]*D[i] for i in range(6)),
             quad=sum(SIG[i]*D[i]*D[i] for i in range(6)))
    on_shell=all(v==0 for v in osk.values())
    print(f"\n=== line {name}: P={[str(x) for x in P]} d={[str(x) for x in D]}")
    print(f"    channel Q_{{{m+1};{p+1}{q+1}}}  (omitted plus leg t=leg{pbar+1});  on-shell={on_shell} {osk}")
    assert on_shell

    # signature of everything EXCEPT the target Q
    def key_of(t):
        w=w_of(t)
        if any(w[i]==0 for i in range(6)): return None
        s=cell_sig(w)
        return (s[0], tuple(sorted(s[1].items())),
                tuple(sorted((k,v) for k,v in s[2].items() if k!=(m,p,q))))
    base=key_of(t_approx)
    assert base is not None
    # grow outward in small steps until the non-target signature changes; keep clean span
    step=F(1,200)
    t_lo=t_approx
    while key_of(t_lo-step)==base and Qc(t_lo-step)!=0: t_lo-=step
    t_hi=t_approx
    while key_of(t_hi+step)==base and Qc(t_hi+step)!=0: t_hi+=step
    # locate the single target-Q root inside (t_lo,t_hi) by bisection on sign
    a,b=t_lo,t_hi
    assert Qc(a)*Qc(b)<0, "target Q does not change sign on the clean span"
    for _ in range(60):
        mid=(a+b)/2
        if Qc(a)*Qc(mid)<=0: b=mid
        else: a=mid
    root=(a+b)/2
    print(f"    clean span t in ({float(t_lo):.4f},{float(t_hi):.4f}); target-Q root ~ {float(root):.6f}")

    # place 11 nodes strictly inside each sub-interval, away from the root
    def nodes(lo,hi):
        lo=lo+(hi-lo)/F(20); hi=hi-(hi-lo)/F(20)
        return [lo+(hi-lo)*F(j,10) for j in range(11)]
    Lnodes=nodes(t_lo, root-(root-t_lo)/F(20))
    Rnodes=nodes(root+(t_hi-root)/F(20), t_hi)
    # certify: each side one chamber; target Q opposite & nonzero; nothing else flips
    sigL=cell_sig(w_of(Lnodes[0])); sigR=cell_sig(w_of(Rnodes[0]))
    for t in Lnodes: assert cell_sig(w_of(t))==sigL and Qc(t)!=0, f"L breaks {t}"
    for t in Rnodes: assert cell_sig(w_of(t))==sigR and Qc(t)!=0, f"R breaks {t}"
    qfl=[k for k in sigL[1] if sigL[1][k]!=sigR[1][k]]
    Qfl=[k for k in sigL[2] if sigL[2][k]!=sigR[2][k]]
    print(f"    q flips L->R: {qfl}   Q flips L->R: {Qfl}   (expect only {(m,p,q)})")
    assert qfl==[] and Qfl==[(m,p,q)], "not a clean single-Q crossing"
    # discriminating? need |w_m| != 2|w_t| somewhere on the span
    wr=w_of(root)
    print(f"    at wall: w_m={float(wr[m]):.4f}, w_t={float(wr[pbar]):.4f}, "
          f"2 w_t={float(2*wr[pbar]):.4f}  -> discriminating: {wr[m]!=2*wr[pbar]}")

    def fit_branch(nds):
        vals=[R_spline(w_of(t)) for t in nds]
        fn,fv=nds[:9],vals[:9]
        for t,v in zip(nds[9:],vals[9:]):
            assert lagrange(fn,fv,t)==v, f"branch not deg<=8 at holdout {t}"
        return fn,fv
    Lf=fit_branch(Lnodes); Rf=fit_branch(Rnodes)

    def G_verifier(t):  w=w_of(t); return -32*w[m]*w[pbar]
    def G_student2(t):  w=w_of(t); return -16*max(w[m]*w[m], w[pbar]*w[pbar])
    def G_neg16m2(t):   w=w_of(t); return -16*w[m]*w[m]

    # Orientation: the brick is defined dR = R|_{Q>0} - R|_{Q<0}.  Identify which
    # node-set is the Q>0 branch and orient the extracted quotient accordingly.
    Rpos_fit = Rf if Qc(Rnodes[0])>0 else Lf
    Rneg_fit = Lf if Qc(Rnodes[0])>0 else Rf
    print(f"    orientation: Q>0 branch = {'right(t>root)' if Qc(Rnodes[0])>0 else 'left(t<root)'}")

    checks=[t_lo+(t_hi-t_lo)*F(k,17) for k in (2,5,9,13,15)]
    v={"verifier":True,"student2":True,"neg16m2":True}
    print("    --- extracted G = (R_{Q>0}-R_{Q<0})/Q^3 vs candidates (exact) ---")
    for x in checks:
        if Qc(x)==0: continue
        dR=lagrange(*Rpos_fit,x)-lagrange(*Rneg_fit,x)   # oriented jump
        Gext=dR/Qc(x)**3
        gv,gs,gn=G_verifier(x),G_student2(x),G_neg16m2(x)
        v["verifier"]&=(Gext==gv); v["student2"]&=(Gext==gs); v["neg16m2"]&=(Gext==gn)
        print(f"      t={float(x):+.4f}: G_ext={Gext}  vs -32wmwt={gv}[{Gext==gv}] "
              f"-16max={gs}[{Gext==gs}] -16wm^2={gn}[{Gext==gn}]")
    print(f"    VERDICT {name}: verifier(-32 w_m w_t)={v['verifier']} | "
          f"student2(-16 max)={v['student2']} | (-16 w_m^2)={v['neg16m2']}")
    return v

def find_independent_line(base, chan, cap=6):
    """search small-integer on-shell directions d at 'base' crossing a clean,
       discriminating Q_chan wall; return (d, t_approx) or None."""
    m,(p,q)=chan
    pbar=[x for x in PLU if x not in (p,q)][0]
    rng=range(-cap,cap+1)
    from itertools import product
    for d in product(rng,repeat=6):
        if sum(d)!=0: continue
        if sum(SIG[i]*base[i]*d[i] for i in range(6))!=0: continue
        if sum(SIG[i]*d[i]*d[i] for i in range(6))!=0: continue
        if all(x==0 for x in d): continue
        D=[F(x) for x in d]
        def w_of(t): return [base[i]+t*D[i] for i in range(6)]
        def Qc(t):   w=w_of(t); return w[p]*w[p]+w[q]*w[q]-w[m]*w[m]
        # look for a sign change of target Q in a modest window, isolated & discriminating
        prev=Qc(F(-3))
        tt=F(-3)
        while tt<3:
            tt+=F(1,10); cur=Qc(tt)
            if prev==0 or cur==0: prev=cur; continue
            if prev*cur<0:
                root=(tt-F(1,10)+tt)/2
                wr=w_of(root)
                if wr[m]!=2*wr[pbar] and wr[m]!=0 and wr[pbar]!=0:
                    return D, tt-F(1,20)
            prev=cur
    return None

def main():
    print("md5(bg.cpp) =", md5(BG_SRC), "(expect 41715c4af3ee5a61b1c4bfce40426ac8)")
    assert md5(BG_SRC)=="41715c4af3ee5a61b1c4bfce40426ac8"
    a=bg_amp_over_i([F(-8),F(2),F(3),F(4),F(5),F(-6)])
    pp=P_pole([F(-8),F(2),F(3),F(4),F(5),F(-6)])
    print(f"anchor {{-8,2,3,4,5,-6}}: A_6/i={a} (exp -9190656/7); P_pole={pp} (exp 42588288/7); "
          f"R_spline={a-pp} (exp -7396992)")
    assert a==F(-9190656,7) and pp==F(42588288,7) and a-pp==F(-7396992)

    out={}
    # LINE A: verifier's own V3 example line, channel (1;46)=(m=0,{3,5}) -> t=leg5(idx4)
    PA=[F(8),F(2),F(-3),F(-5),F(4),F(-6)]; DA=[F(-3),F(-2),F(1),F(3),F(-1),F(2)]
    out["A"]=analyze_line(PA,DA,(0,(3,5)),"A(verifier-V3, chan 1;46)",F(188,100))

    # LINE B: independent PI line, DIFFERENT base and channel (2;45)=(m=1,{3,4}) -> t=leg6(idx5)
    PB=[F(-8),F(2),F(3),F(4),F(5),F(-6)]
    chanB=(1,(3,4))
    found=find_independent_line(PB, chanB, cap=5)
    if found:
        DB,tapp=found
        print(f"\n[search] independent line B at base {PB}: d={[str(x) for x in DB]}, t_approx~{float(tapp):.3f}")
        out["B"]=analyze_line(PB,DB,chanB,"B(independent, chan 2;45)",tapp)
    else:
        print("\n[search] no clean independent line B found in cap; skipping.")
    print("\n===== SUMMARY =====", out)

if __name__=="__main__":
    main()
