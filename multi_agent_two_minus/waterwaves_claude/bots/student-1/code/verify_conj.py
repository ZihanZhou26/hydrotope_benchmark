"""Test conjecture  a_n = 2^(n-1) * w1*w2 * min(w1^2,w2^2)^(n-3)
(w1,w2 = the two minus legs) across n and many in-sector points, and map
where it holds vs fails (relate failure to magnitude ordering)."""
import sympy as sp, random, itertools
import bgio

def conj(omega, n):
    w1,w2=omega[0],omega[1]
    return 2**(n-1)*w1*w2*sp.Min(w1**2,w2**2)**(n-3)

def describe(omega):
    mags=[abs(x) for x in omega]
    order=sorted(range(len(omega)), key=lambda i:mags[i])
    smallest=order[0]; largest=order[-1]
    tag_small = 'MINUS' if smallest in (0,1) else 'plus'
    tag_large = 'MINUS' if largest in (0,1) else 'plus'
    # are the two minus legs the global min and max?
    minus_are_extremes = set([order[0],order[-1]])=={0,1}
    # is smaller minus leg the global smallest?
    sm_minus = 0 if mags[0]<mags[1] else 1
    smaller_minus_is_global_min = (smallest==sm_minus)
    return tag_small, tag_large, minus_are_extremes, smaller_minus_is_global_min

def test_n(n, npts, seed):
    random.seed(seed)
    vals=[sp.Rational(x) for x in range(1,10)]+[sp.Rational(1,2),sp.Rational(3,2),sp.Rational(5,2),sp.Rational(7,2),sp.Rational(9,2)]
    nhold=0; nok=0; rows=[]
    tries=0
    while nhold<npts and tries<120*npts:
        tries+=1
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set([abs(x) for x in om]))<n: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        c=conj(om,n)
        ok=(sp.simplify(a-c)==0)
        nhold+=1; nok+=ok
        rows.append((om,a,c,ok)+describe(om))
    return rows

if __name__=="__main__":
    for n in (5,6):
        rows=test_n(n, 40, seed=n)
        nok=sum(1 for r in rows if r[3])
        print(f"=== n={n}: conjecture holds on {nok}/{len(rows)} random in-sector points ===")
        # correlate holding with the chamber descriptor
        from collections import Counter
        held=Counter(); failed=Counter()
        for (om,a,c,ok,ts,tl,ext,smgm) in rows:
            key=(ts,smgm)  # (smallest-leg type, smaller-minus-is-global-min)
            (held if ok else failed)[key]+=1
        print("  held by (smallest_leg_type, smaller_minus_is_global_min):", dict(held))
        print("  failed by same key:", dict(failed))
        # show a few failures
        fails=[r for r in rows if not r[3]][:3]
        for (om,a,c,ok,ts,tl,ext,smgm) in fails:
            print(f"    FAIL omega={[str(x) for x in om]} a={a} conj={c} small={ts} smGlobMin={smgm}")
