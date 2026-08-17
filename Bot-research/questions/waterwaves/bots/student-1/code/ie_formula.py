"""Test inclusion-exclusion closed form:
  a_n = 2^(n-1) * w1*w2 * C_n
  C_n = sum_{S subset of small-plus-legs} (-1)^|S| (P - sum_{j in S} t_j)^(n-3)
where P = min(w1^2,w2^2) (smaller-minus square), small-plus = plus legs with t_j<P.
Test across random in-sector points; classify failures."""
import sympy as sp, random, itertools
import bgio

def C_ie(n, om):
    w1,w2=om[0],om[1]
    P=min(w1**2,w2**2)
    sp_legs=[om[j]**2 for j in range(2,n) if om[j]**2<P]
    tot=0
    for r in range(len(sp_legs)+1):
        for S in itertools.combinations(sp_legs,r):
            tot += (-1)**r * (P - sum(S))**(n-3)
    return tot

def a_ie(n, om):
    return 2**(n-1)*om[0]*om[1]*C_ie(n,om)

def classify(n, om):
    P=min(om[0]**2,om[1]**2); Q=max(om[0]**2,om[1]**2)
    mid=sum(1 for j in range(2,n) if P<om[j]**2<Q)   # plus legs between the two minus
    below=sum(1 for j in range(2,n) if om[j]**2<P)
    return below, mid

if __name__=="__main__":
    for n in (5,6,7):
        random.seed(n)
        vals=[sp.Rational(a) for a in range(1,11)]+[sp.Rational(a,2) for a in range(1,14,2)]+[sp.Rational(a,3) for a in range(1,16)]
        nok=0; ntot=0
        from collections import Counter
        okby=Counter(); failby=Counter()
        while ntot<80:
            fw=[random.choice(vals) for _ in range(n-2)]
            if len(set(fw))<len(fw): continue
            r=bgio.onshell(n, fw, double=(n==7))
            if not r["ok"]: continue
            if n==7:
                om=[sp.Float(x,30) for x in r["omega"]]; a=sp.Float(r["im"],30)
            else:
                om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]; a=sp.Rational(r["a"].numerator,r["a"].denominator)
            if len(set([abs(x) for x in om]))<n: continue
            pred=a_ie(n,om)
            if n==7:
                ok = abs(pred-a) <= sp.Float(1e-9)*abs(a)
            else:
                ok = (sp.simplify(a-pred)==0)
            ntot+=1; nok+=bool(ok)
            below,mid=classify(n,om)
            (okby if ok else failby)[(below,mid)]+=1
        print(f"n={n}: IE formula holds {nok}/{ntot}")
        print(f"   held by (below,mid): {dict(okby)}")
        print(f"   failed by (below,mid): {dict(failby)}")
