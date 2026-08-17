"""
Identify G(s)=a_6 in the n=6 one-soft-leg region, minus=(-8,2).
a_6 = 2^5 * w1*w2 * P(s^2) = -512 * P(x), x=s^2.  Fit P(x) (cubic in x) and inspect.
"""
import mpmath as mp
import sympy as sp
import bg_float
mp.mp.dps = 45
w1, w2 = mp.mpf(-8), mp.mpf(2)
A_, B_ = mp.mpf(6), mp.mpf(68)
sig6 = [-1, -1, 1, 1, 1, 1]


def a6(s, t):
    S = A_ - s - t
    Q = B_ - s * s - t * t
    disc = 2 * Q - S * S
    if disc < 0:
        return None
    r = mp.sqrt(disc)
    legs = (t, (S + r) / 2, (S - r) / 2)
    if not all(mp.mpf(2) < abs(v) < mp.mpf(8) for v in legs):
        return None
    A = bg_float.amp_from_allW([w1, w2] + list(legs), sig6)
    if abs(A.real) > mp.mpf('1e-18'):
        return None
    return A.imag


# collect (x=s^2, P=a_6/-512) for several s
data = []
for sval in ['1/4', '1/2', '3/4', '1', '5/4', '3/2', '7/4']:
    s = mp.mpf(sp.Rational(sval))
    v = None
    for tt in ['4', '3.5', '4.5', '5', '3']:
        v = a6(s, mp.mpf(tt))
        if v is not None:
            break
    if v is not None:
        x = sp.Rational(sval) ** 2
        P = v / mp.mpf(-512)
        data.append((x, P, sp.Rational(sval)))
        print(f"  s={sval}: x=s^2={x}, a_6={mp.nstr(v,14)}, P=a_6/-512={mp.nstr(P,14)}", flush=True)

# recognize P as rational and fit cubic P(x)=a x^3+b x^2+c x+d
print("\n  recognizing P as rationals and fitting cubic in x=s^2:", flush=True)
pts = []
for x, P, s in data:
    Prat = sp.nsimplify(mp.nstr(P, 30), rational=True)
    pts.append((x, Prat))
    print(f"    x={x}: P={Prat}", flush=True)

a, b, c, d, X = sp.symbols('a b c d X')
eqs = [a * x**3 + b * x**2 + c * x + d - P for (x, P) in pts[:4]]
sol = sp.solve(eqs, [a, b, c, d], dict=True)
if sol:
    s0 = sol[0]
    Px = s0[a] * X**3 + s0[b] * X**2 + s0[c] * X + s0[d]
    print(f"\n  cubic fit P(x) = {sp.factor(Px)}", flush=True)
    print(f"  check remaining points:", flush=True)
    for (x, P) in pts[4:]:
        print(f"    x={x}: fit={Px.subs(X,x)} actual={P} {'OK' if sp.simplify(Px.subs(X,x)-P)==0 else 'NO'}", flush=True)
    # boundary x=w2^2=4 should give 64
    print(f"  P(4) [boundary, expect 64] = {Px.subs(X,4)}", flush=True)
    # interleaving min is w2^2=4, w1^2=64
    print(f"  note w2^2=4, w1^2=64", flush=True)
