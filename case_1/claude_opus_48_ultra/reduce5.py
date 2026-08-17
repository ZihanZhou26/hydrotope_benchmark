import sympy as sp, pickle

w1,w2,w3,w4,w5=sp.symbols('w1 w2 w3 w4 w5')
with open("sbg_A5.pkl","rb") as f:
    s=pickle.load(f)
ns={k:getattr(sp,k) for k in dir(sp)}
ns.update({'w1':w1,'w2':w2,'w3':w3,'w4':w4,'w5':w5})
A=eval(s, ns)

sumF=w2+w3+w4
w5sol=((sumF)**2 + w2**2 - w3**2 - w4**2)/(-2*sumF)
w1sol=-(sumF+w5sol)

Asub=sp.together(A.subs({w5:w5sol, w1:w1sol}))
Asub=sp.cancel(Asub)
print("A_5 on manifold (chamber of ref), function of (w2,w3,w4):")
print("  =", Asub)
print()
num,den=sp.fraction(sp.together(Asub/sp.I))
print("A/I numerator factored:\n", sp.factor(num))
print("A/I denominator factored:\n", sp.factor(den))
print()
chk=Asub.subs({w2:2,w3:sp.Rational(5,2),w4:3}); print("check (2,5/2,3):", sp.simplify(chk),"(exp -2304 I)")
chk2=Asub.subs({w2:2,w3:3,w4:4}); print("check (2,3,4):", sp.simplify(chk2),"(exp -8704/3 I)")
chk3=Asub.subs({w2:3,w3:4,w4:5}); print("check (3,4,5):", sp.simplify(chk3),"(exp -28512 I)")
