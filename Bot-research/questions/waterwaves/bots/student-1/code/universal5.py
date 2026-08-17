"""Test a UNIVERSAL (all-chamber) closed form for n=5:
  a_5 = 16 * w1*w2 * C5,  m=min(|w1|,|w2|),
  C5 = m^4 - sum_{plus legs j with |w_j|<m} (m^2 - w_j^2)^2
across random in-sector points spanning all chambers."""
import sympy as sp, random
import bgio

def C5(omega):
    w1,w2=omega[0],omega[1]
    m2=sp.Min(w1**2,w2**2)
    s=m2**2
    for j in range(2,5):
        wj2=omega[j]**2
        if wj2<m2:
            s=s-(m2-wj2)**2
    return s

def conj5(omega):
    return 16*omega[0]*omega[1]*C5(omega)

if __name__=="__main__":
    random.seed(7)
    vals=[sp.Rational(x) for x in range(1,11)]+[sp.Rational(k,2) for k in (1,3,5,7,9,11)]+[sp.Rational(k,3) for k in (1,2,4,5,7)]
    nok=0; ntot=0; fails=[]
    while ntot<120:
        fw=[random.choice(vals) for _ in range(3)]
        if len(set(fw))<3: continue
        r=bgio.onshell(5, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set([abs(x) for x in om]))<5: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        c=conj5(om)
        ok=(sp.simplify(a-c)==0)
        ntot+=1; nok+=ok
        if not ok and len(fails)<8:
            mags=sorted([abs(x) for x in om])
            fails.append((om,a,c))
    print(f"n=5 universal conjecture holds on {nok}/{ntot} random in-sector points")
    for om,a,c in fails:
        nbelow=sum(1 for j in range(2,5) if om[j]**2<sp.Min(om[0]**2,om[1]**2))
        print(f"  FAIL omega={[str(x) for x in om]} a={a} conj={c}  #plus<m={nbelow}")
