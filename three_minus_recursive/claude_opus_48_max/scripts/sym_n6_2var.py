"""Compute n=6 three-minus B symbolically in 2 free vars (w4,w5), w2=2,w3=3 fixed,
in the chamber of ref point (w4=5,w5=4). Prints exact rational B(w4,w5)."""
import time, sympy as sp
import sym_engine

w4, w5 = sp.symbols('w4 w5', real=True)
w2v, w3v = sp.Integer(2), sp.Integer(3)
# sigma=(-1,-1,-1,1,1,1); free legs 2,3,4,5 (sig -1,-1,+1,+1); solve w1,w6
free = [w2v, w3v, w4, w5]
sg = [-1, -1, -1, 1, 1, 1]
s0 = sp.Integer(-1)
sumFree = sum(free)
sumSig = -w2v**2 - w3v**2 + w4**2 + w5**2   # sig[1..4]*free^2
w6 = -(s0*sumFree**2 + sumSig) / (2*s0*sumFree)
w1 = -(sumFree + w6)
W = [w1, w2v, w3v, w4, w5, w6]
ref = {w4: 5, w5: 4}
t0 = time.time()
A = sym_engine.amp_symbolic(W, sg, ref, g=1)
B = sp.cancel(sp.im(A))
print("elapsed", round(time.time()-t0, 1), "s")
num, den = sp.fraction(sp.together(B))
print("B numerator   =", sp.factor(num))
print("B denominator =", sp.factor(den))
print("B at (w4=5,w5=4):", sp.nsimplify(B.subs({w4: 5, w5: 4})))
