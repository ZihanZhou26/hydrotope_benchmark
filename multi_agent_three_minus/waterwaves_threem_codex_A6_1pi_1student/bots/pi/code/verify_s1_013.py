#!/usr/bin/env python3
"""PI round-4: independent SYMBOLIC verification of student claim s1_013.

s1_013 asserts exact factorizations of the BG inverse propagator
    h_S = omega_S^2 - |q_S|,   q_S = sum_{i in S} sigma_i omega_i^2,   g=1,
where omega_S = sum of the (signed) leg frequencies in S.

We verify the displayed identities as pure polynomial identities in the signed
leg frequencies, on each branch of |q_S|:

 (P) two same-sign legs (freqs x,y):          h = 2 x y            (branch-free)
 (M) mixed pair (minus x, plus y), q=y^2-x^2:
        |q|/h = (y-x)/(2x)  if q>0 ;  (x-y)/(2y)  if q<0
 (T) mixed triple (minus x,y ; plus z), q=z^2-x^2-y^2:
        h = 2 (x+z)(y+z)                  if q<0
        h = 2 (x^2+y^2+xy+z(x+y))         if q>0
 (A) all-same-sign triple (freqs x,y,z):      h = 2 e_2(x,y,z) = 2 p
"""
import sympy as sp

x, y, z = sp.symbols('x y z', real=True)
ok = True


def check(name, lhs, rhs):
    global ok
    d = sp.simplify(sp.expand(lhs - rhs))
    good = (d == 0)
    ok = ok and good
    print(f"  [{'PASS' if good else 'FAIL'}] {name}:  lhs-rhs = {d}")


print("=" * 72)
print("s1_013 symbolic verification (pure frequency-polynomial identities)")

# (P) two same-sign legs: omega_S = x+y, |q_S| = x^2+y^2
hP = (x + y) ** 2 - (x ** 2 + y ** 2)
check("(P) same-sign pair  h = 2xy", hP, 2 * x * y)

# (M) mixed pair: minus x, plus y ; omega_S = x+y ; q = y^2 - x^2
#   q>0 branch: |q| = y^2 - x^2
hM_pos = (x + y) ** 2 - (y ** 2 - x ** 2)
check("(M) mixed pair q>0  h = 2x(x+y)", hM_pos, 2 * x * (x + y))
check("(M) mixed pair q>0  |q|/h = (y-x)/(2x)",
      (y ** 2 - x ** 2) / hM_pos, (y - x) / (2 * x))
#   q<0 branch: |q| = x^2 - y^2
hM_neg = (x + y) ** 2 - (x ** 2 - y ** 2)
check("(M) mixed pair q<0  h = 2y(x+y)", hM_neg, 2 * y * (x + y))
check("(M) mixed pair q<0  |q|/h = (x-y)/(2y)",
      (x ** 2 - y ** 2) / hM_neg, (x - y) / (2 * y))

# (T) mixed triple: minus x,y ; plus z ; omega_S = x+y+z ; q = z^2 - x^2 - y^2
#   q<0 branch: |q| = x^2 + y^2 - z^2
hT_neg = (x + y + z) ** 2 - (x ** 2 + y ** 2 - z ** 2)
check("(T) mixed triple q<0  h = 2(x+z)(y+z)", hT_neg, 2 * (x + z) * (y + z))
#   q>0 branch: |q| = z^2 - x^2 - y^2
hT_pos = (x + y + z) ** 2 - (z ** 2 - x ** 2 - y ** 2)
check("(T) mixed triple q>0  h = 2(x^2+y^2+xy+z(x+y))",
      hT_pos, 2 * (x ** 2 + y ** 2 + x * y + z * (x + y)))

# (A) all-same-sign triple: omega_S = x+y+z, |q_S| = x^2+y^2+z^2
hA = (x + y + z) ** 2 - (x ** 2 + y ** 2 + z ** 2)
e2 = x * y + x * z + y * z
check("(A) same-sign triple  h = 2 e_2 = 2p", hA, 2 * e2)

# Is the q>0 mixed-triple quadratic genuinely irreducible over Q?
Q = sp.expand(x ** 2 + y ** 2 + x * y + z * (x + y))
fac = sp.factor(Q)
print(f"  q>0 triple quadratic factor(x^2+y^2+xy+z(x+y)) = {fac}  "
      f"({'IRREDUCIBLE' if fac == Q else 'reducible'})")

print("=" * 72)
print(f"s1_013 SYMBOLIC RESULT: {'ALL PASS' if ok else 'SOME FAIL'}")
