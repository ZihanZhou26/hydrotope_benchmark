import pickle, sympy as sp
from fractions import Fraction as Q
from fit_kabs import P0_basis_vals, PEXPS, sym2, msym_list

with open("kabs_sol5.pkl","rb") as f:
    sol=[Q(s) for s in pickle.load(f)]

w=sp.symbols('w1 w2 w3 w4 w5')  # w[0..4]; minus w1,w2 ; plus w3,w4,w5
# rebuild P0 basis symbolically in same order as P0_basis_vals
def sym2s(a, vars2):
    out=[]
    for p in range(a, a//2 -1, -1):
        q=a-p
        if p<q: break
        from itertools import permutations
        ps=set(permutations((p,q)))
        out.append(sum(vars2[0]**e[0]*vars2[1]**e[1] for e in ps))
    return out
def msym_s(b, vars3):
    parts=[]
    def rec(rem,maxp,cur):
        if rem==0: parts.append(tuple(cur)); return
        if len(cur)==3: return
        for p in range(min(maxp,rem),0,-1): rec(rem-p,p,cur+[p])
    rec(b,b,[])
    from itertools import permutations
    out=[]
    for lam in parts:
        exps=tuple(list(lam)+[0]*(3-len(lam)))
        ps=set(permutations(exps))
        out.append(sum(vars3[0]**e[0]*vars3[1]**e[1]*vars3[2]**e[2] for e in ps))
    if b==0: out=[sp.Integer(1)]
    return out

minus=(w[0],w[1]); plus=(w[2],w[3],w[4])
P0basis=[]
for a in range(0,7):
    b=6-a
    s2=sym2s(a,minus) if a>0 else [sp.Integer(1)]
    s3=msym_s(b,plus)
    for u in s2:
        for v in s3:
            P0basis.append(u*v)
nb0=len(P0basis)

P0=sum(sp.Rational(sol[j])*P0basis[j] for j in range(nb0) if sol[j]!=0)
print("nb0=",nb0,"  P0 =", sp.factor(P0))

# |k| part: for each PEXPS monomial idx, coeff sol[nb0+idx], building sum_{mu,j} mono*|kmuj|
# print the P-polynomial (coefficient of |k_{mu j}|) as function of (wmu, wj, wmup, e1', e2')
wmu,wj,wmup,e1,e2=sp.symbols('wmu wj wmup e1 e2')
P=0
for idx,(a,b,c,d,e) in enumerate(PEXPS):
    co=sol[nb0+idx]
    if co!=0:
        P+=sp.Rational(co)*wmu**a*wj**b*wmup**c*e1**d*e2**e
print("P(wmu,wj,wmup,e1',e2') =", sp.factor(P))
print("  (the |k| part of A is  sum_{mu in {1,2}, j in plus}  P * |wj^2 - wmu^2| ,")
print("   where wmup=other minus leg, e1',e2'=elem sym of other two plus legs)")
