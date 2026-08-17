#!/usr/bin/env python3
"""Write the fitted coefficients as explicit polynomials:
  B  (base): polynomial in invariants (e1,e2,e3m,e3p)
  P0 (single-(1=1) coeff): polynomial in x=w1,y=w4,A1=w2+w3,A2=w2 w3,B1=w5+w6,B2=w5 w6
     [reference wall {a1=b4}, 0-indexed legs 0,3 -> human legs 1,4]
  R0 (pair-(1=1) coeff): polynomial in the raw frequencies (reference pair {(1,4),(2,5)})
so the closed form is
  N_6 = B + orbit-sum (k03)_+ P0 + orbit-sum (k03)_+(k14)_+ R0 + (1=2) corr (Q).
"""
from fractions import Fraction as F
import pickle, sympy as sp

labels,rcoef=pickle.load(open("r6_coeffs.pkl","rb"))
e1,e2,e3m,e3p=sp.symbols('e1 e2 e3m e3p')
x,y,A1,A2,B1,B2=sp.symbols('x y A1 A2 B1 B2')   # P0 vars (mode P)
w=sp.symbols('w1 w2 w3 w4 w5 w6')               # R0 raw vars (1-indexed -> w[0..5])

def rat(fr): return sp.Rational(fr.numerator,fr.denominator)

Bexpr=sp.Integer(0); P0=sp.Integer(0); R0=sp.Integer(0)
nbase=nsing=npair=0
for (lab,c) in zip(labels,rcoef):
    if lab[0]=='base':
        a,b,cc,d=lab[1]
        term=rat(c)*(e1**a*e2**b*(e3m**cc*e3p**d + (-1)**a*e3m**d*e3p**cc))
        Bexpr+=term; nbase+=1
    elif lab[0]=='single':
        e=lab[1]   # exponents of (x,y,A1,A2,B1,B2)
        mon=x**e[0]*y**e[1]*A1**e[2]*A2**e[3]*B1**e[4]*B2**e[5]
        P0+=rat(c)*mon; nsing+=1
    elif lab[0]=='pair':
        e=lab[1]   # raw exponents on (w1..w6)
        mon=sp.prod([w[i]**e[i] for i in range(6)])
        R0+=rat(c)*mon; npair+=1

Bexpr=sp.expand(Bexpr); P0=sp.expand(P0); R0=sp.expand(R0)
print(f"#base={nbase} #single={nsing} #pair={npair}\n")
print("B (in invariants e1=e1plus, e2, e3m, e3p):")
sp.pprint(sp.factor(Bexpr)); print()
print("P0 (single-(1=1) coeff; x=w1,y=w4,A1=w2+w3,A2=w2w3,B1=w5+w6,B2=w5w6), deg in w =",
      sp.Poly(P0.subs({x:w[0],y:w[3],A1:w[1]+w[2],A2:w[1]*w[2],B1:w[4]+w[5],B2:w[4]*w[5]}),*w).total_degree())
print("  #terms:",len(P0.as_ordered_terms()))
print("\nR0 (pair-(1=1) coeff, reference pair walls {a1=b4},{a2=b5}); total deg:",
      sp.Poly(R0,*w).total_degree(),"  #terms:",len(R0.as_ordered_terms()))
sp.pprint(sp.factor(R0))

# save symbolic for reuse
pickle.dump({'B':Bexpr,'P0':P0,'R0':R0}, open("r6_polys.pkl","wb"))
print("\nsaved r6_polys.pkl")
