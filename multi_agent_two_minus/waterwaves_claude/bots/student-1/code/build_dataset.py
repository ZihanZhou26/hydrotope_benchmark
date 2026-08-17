"""Build a clean exact-rational dataset of A_n (= i*a_n) in the two-minus sector,
for n=4 (delta-limit),5,6,7, over many in-sector kinematic points spanning all
chambers + non-generic regimes. Writes data/dataset.csv with the full omega
vector, a_n (exact), and the chamber label. Also records the closed-form value
and the relative residual (0 = bit-exact)."""
import sympy as sp, random, csv, os
import bgio
from n4_limit import a4_limit
from verify_universal import a_pred, chamber_label

HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,"..","data","dataset.csv")

def rows_for_n(n, npts, seed):
    random.seed(seed)
    vals=[sp.Rational(a) for a in range(1,12)]+[sp.Rational(a,2) for a in range(1,14,2)]+[sp.Rational(a,3) for a in range(1,16)]
    out=[]; ntot=0
    while len(out)<npts and ntot<400*npts:
        ntot+=1
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set([abs(x) for x in om]))<n: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        pred=a_pred(n,om)
        rel = 0 if sp.simplify(a-pred)==0 else sp.Rational(sp.nsimplify((pred-a)/a))
        out.append((n,[str(x) for x in om],str(a),chamber_label(n,om),str(pred),str(rel)))
    return out

if __name__=="__main__":
    allrows=[]
    # n=4 via delta-limit at several (a,b)
    for (a,b) in [(1,3),(2,5),(1,2),(2,3),(3,4),(1,4),(3,5),(4,7),(1,5),(2,7)]:
        lim,_=a4_limit(a,b)
        om=[sp.Rational(-b),sp.Rational(a),sp.Rational(b),sp.Rational(-a)]
        pred=a_pred(4,om)
        rel = 0 if sp.Rational(int(lim))==pred else "NONZERO"
        allrows.append((4,[str(x) for x in om],str(int(lim)),chamber_label(4,om)+"(limit)",str(pred),str(rel)))
    for n,npts,seed in [(5,40,11),(6,40,12),(7,25,13)]:
        allrows += rows_for_n(n,npts,seed)
    with open(OUT,"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["n","omega (in order, exact)","a_n (exact; A_n=i*a_n)","chamber (b=#below P, m=#mid, h=#high)","closed_form_pred","rel_residual(0=bit-exact)"])
        for r in allrows:
            w.writerow([r[0],";".join(r[1]) if isinstance(r[1],list) else r[1],r[2],r[3],r[4],r[5]])
    nz=sum(1 for r in allrows if r[5] not in ("0",))
    print(f"wrote {len(allrows)} rows to {OUT}; nonzero-residual rows: {nz}")
    print("per-n counts:", {n:sum(1 for r in allrows if r[0]==n) for n in (4,5,6,7)})
