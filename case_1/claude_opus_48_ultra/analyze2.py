"""Reconstruct A_5 as an exact rational function of one varied plus-frequency,
then factor to read off the channel (pole) structure.

We use MakeKinematics with free = {w2(minus), w3(plus), w4(plus)=t} and vary t.
w1 (minus) and w5 (plus) are derived rationally in t. A_5(t) is then an exact
rational function of t; its denominator reveals the physical channels."""
from bg import amp_two_minus, make_kinematics, two_minus_sigma
from fractions import Fraction as Q
import sympy as sp

t = sp.symbols('t')

def A_of_t(b2, a3, tval):
    """im(A_5) with free freqs (w2,w3,w4)=(b2,a3,tval)."""
    A,_,wL = amp_two_minus(5, [Q(b2), Q(a3), Q(tval)])
    return A.im, wL

# Fixed generic values for w2 (minus) and w3 (plus); vary w4 = t.
b2, a3 = Q(2), Q(5,2)

# sample many t values (avoid t that make sumFree=0 etc.)
tvals = [Q(k,3) for k in range(1, 60) if k not in (0,)]  # 1/3,2/3,...
pts = []
for tv in tvals:
    try:
        im, wL = A_of_t(b2, a3, tv)
        pts.append((tv, im))
    except Exception as e:
        pass

print(f"collected {len(pts)} points")

# Reconstruct rational function P(t)/Q(t) by trying degrees.
def fit_rational(pts, dp, dq):
    # A(t)*Q(t) = P(t), Q monic-free: set Q(t)=1+sum_{j>=1} q_j t^j, P=sum p_i t^i
    # unknowns: p_0..p_dp, q_1..q_dq.  Equation per point: sum p_i t^i - A*sum_{j>=1} q_j t^j = A
    import sympy as sp
    nun = (dp+1) + dq
    rows = []
    rhs = []
    for (tv, Av) in pts:
        row = []
        for i in range(dp+1):
            row.append(sp.Rational(tv**i))
        for j in range(1, dq+1):
            row.append(-sp.Rational(Av)*sp.Rational(tv**j))
        rows.append(row)
        rhs.append(sp.Rational(Av))
    M = sp.Matrix(rows)
    v = sp.Matrix(rhs)
    # need at least nun points; use all, solve least... use exact solve on first nun, verify rest
    if len(pts) < nun:
        return None
    Msq = M[:nun, :]
    vsq = v[:nun, :]
    if Msq.det() == 0:
        return None
    sol = Msq.solve(vsq)
    # verify on remaining points
    p = sol[:dp+1]
    qs = sol[dp+1:]
    Pexpr = sum(p[i]*t**i for i in range(dp+1))
    Qexpr = 1 + sum(qs[j]*t**(j+1) for j in range(dq))
    ok = True
    for (tv, Av) in pts[nun:]:
        val = (Pexpr/Qexpr).subs(t, sp.Rational(tv))
        if sp.simplify(val - sp.Rational(Av)) != 0:
            ok = False; break
    return (Pexpr, Qexpr, ok)

found = None
for total in range(2, 26):
    for dq in range(0, total+1):
        dp = total - dq
        try:
            r = fit_rational(pts, dp, dq)
        except Exception:
            r = None
        if r and r[2]:
            found = (dp, dq, r[0], r[1])
            break
    if found: break

if found:
    dp, dq, P, Q = found
    print(f"FIT: deg P={dp}, deg Q={dq}, verified on held-out points")
    Pf = sp.factor(P); Qf = sp.factor(Q)
    print("Numerator   P(t) =", Pf)
    print("Denominator Q(t) =", Qf)
else:
    print("no fit found in range")
