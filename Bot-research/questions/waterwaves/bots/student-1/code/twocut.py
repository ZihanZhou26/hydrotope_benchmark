"""Search for the universal two-cutoff closed form.
Define truncated inclusion-exclusion over ALL plus legs at a cutoff x:
   D(x) = sum_{S subset of plus} (-1)^|S| max(0, x - sum_{j in S} t_j)^(n-3)
P=min(w1^2,w2^2), Q=max. Test candidate combinations of D(P), D(Q) vs C_actual."""
import sympy as sp, random, itertools
import bgio

def D(x, plus_sq, p):
    tot=sp.Integer(0)
    for r in range(len(plus_sq)+1):
        for S in itertools.combinations(plus_sq,r):
            base=x-sum(S)
            if base>0:
                tot += (-1)**r * base**p
    return tot

def Cval(n,om,a): return a/(2**(n-1)*om[0]*om[1])

def test(n, npts, seed):
    random.seed(seed)
    vals=[sp.Rational(a) for a in range(1,11)]+[sp.Rational(a,2) for a in range(1,14,2)]+[sp.Rational(a,3) for a in range(1,16)]
    cands={'D(P)':0,'D(P)-D(Q)+Q^p':0,'D(P)+D(Q)-2 D@minQ?':0,'D(P)-[D(Q)-Q^p]':0}
    nP=nPQ=ntot=0
    fails=[]
    while ntot<npts:
        fw=[random.choice(vals) for _ in range(n-2)]
        if len(set(fw))<len(fw): continue
        r=bgio.onshell(n, fw)
        if not r["ok"]: continue
        om=[sp.Rational(x.numerator,x.denominator) for x in r["omega"]]
        if len(set([abs(x) for x in om]))<n: continue
        a=sp.Rational(r["a"].numerator,r["a"].denominator)
        C=Cval(n,om,a)
        P=min(om[0]**2,om[1]**2); Q=max(om[0]**2,om[1]**2)
        psq=[om[j]**2 for j in range(2,n)]
        p=n-3
        DP=D(P,psq,p); DQ=D(Q,psq,p)
        ntot+=1
        nP += (C==DP)
        # candidate: C = DP - (DQ - Q^p)   i.e. DP - DQ + Q^p
        cand1 = DP - DQ + Q**p
        nPQ += (C==cand1)
        if C!=cand1 and len(fails)<6:
            fails.append((P,Q,sorted(psq),C,DP,DQ,cand1))
    print(f"n={n}: C==D(P): {nP}/{ntot};  C==D(P)-D(Q)+Q^p: {nPQ}/{ntot}")
    for f in fails:
        P,Q,psq,C,DP,DQ,c1=f
        print(f"   FAIL P={P} Q={Q} psq={psq}")
        print(f"        C={C}  DP={DP}  DQ={DQ}  DP-DQ+Q^p={c1}  C-DP={sp.simplify(C-DP)}  C-cand1={sp.simplify(C-c1)}")

if __name__=="__main__":
    test(5, 60, 3)
    test(6, 50, 6)
