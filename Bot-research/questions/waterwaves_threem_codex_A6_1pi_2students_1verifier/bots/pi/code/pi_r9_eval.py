#!/usr/bin/env python3
"""
Independent PI re-implementation (round 9) of the round-8 compact A_6 candidate
(student-1 s1_010), transcribed BY HAND from the WRITTEN LaTeX derivation

    bots/student-1/derivations/s1_010_round8_compact_hinge_candidate.md

NOT imported from any student or verifier evaluator.  Uses exact rationals only
(fractions.Fraction).  This is the object the definition of done requires the PI
to build independently before writing SOLVED.md.

Formula (three-minus sector, M={1,2,3} minus, P={4,5,6} plus):

    A_6 = i g^{-3} ( P_pole + R_Q + R_0 + R_q )

with R_0 = H_0(u,v,e_-,e_+), R_q = 4 sum h_mp H_1 + 2 sum h h H_2, and the
settled pole part P_pole and triple-wall orbit R_Q.  All auxiliary quantities
are defined in the code below exactly as displayed in s1_010.
"""
from fractions import Fraction as F

M = (1, 2, 3)      # minus legs
P = (4, 5, 6)      # plus legs


def pp(x):
    """Positive part (x)_+ = max(x,0)."""
    return x if x > 0 else (x * 0)


# ---------------------------------------------------------------------------
# Seed polynomials (transcribed verbatim from s1_010).
# ---------------------------------------------------------------------------

def H1(a, b, s, v):
    """H_1(a,b,s,v) = 2[ ... ]  (46 monomials in the bracket)."""
    br = (
        12*s**6 - 21*s**5*a - 22*s**5*b - 115*s**4*v - 48*s**4*a*b - 58*s**4*b**2
        + 36*s**3*v*a + 44*s**3*v*b + 13*s**3*a**3 + 12*s**3*a**2*b - 5*s**3*a*b**2 - 4*s**3*b**3
        + 268*s**2*v**2 + 25*s**2*v*a**2 + 308*s**2*v*a*b + 323*s**2*v*b**2
        - 16*s**2*a**4 - 66*s**2*a**3*b - 62*s**2*a**2*b**2 + 30*s**2*a*b**3 + 42*s**2*b**4
        + 240*s*v**2*a + 240*s*v**2*b - 92*s*v*a**3 + 14*s*v*a**2*b + 328*s*v*a*b**2 + 222*s*v*b**3
        - 64*s*a**4*b - 212*s*a**3*b**2 - 206*s*a**2*b**3 - 32*s*a*b**4 + 26*s*b**5
        - 8*v**3 + 42*v**2*a**2 + 72*v**2*a*b + 30*v**2*b**2
        - 36*v*a**4 - 112*v*a**3*b - 78*v*a**2*b**2 + 36*v*a*b**3 + 38*v*b**4
        + 4*a**6 - 44*a**4*b**2 - 112*a**3*b**3 - 112*a**2*b**4 - 40*a*b**5
    )
    return 2*br


def H2(a, b, s, v, c):
    """H_2(a,b,s,v,c) = -4[ ... ]  (23 monomials in the bracket)."""
    br = (
        4*c*s**2 + 4*c*s*a + 4*c*s*b + 22*c*a**2 + 4*c*a*b - 22*c*b**2
        + 4*s**4 + 4*s**3*a + 4*s**3*b - 8*s**2*v + 12*s**2*a**2 - 16*s**2*b**2
        - 8*s*v*a - 8*s*v*b + s*a**3 - 9*s*a*b**2 - 4*s*b**3
        - 23*v*a**2 + 19*v*b**2 + 12*a**4 + 22*a**3*b - 12*a**2*b**2 - 22*a*b**3
    )
    return -4*br


def H0(u, v, em, ep):
    """H_0(u,v,e_-,e_+) = 16[ ... ]  (13 monomials in the bracket)."""
    br = (
        69*em**2*v - 126*em*ep*u**2 - 18*em*ep*v - 40*em*u*v**2
        + 42*ep**2*u**2 - 57*ep**2*v - 52*ep*u**5 + 204*ep*u**3*v - 54*ep*u*v**2
        + 4*u**8 - 32*u**6*v + 68*u**4*v**2 - 16*u**2*v**3
    )
    return 16*br


# ---------------------------------------------------------------------------
# The four pieces.
# ---------------------------------------------------------------------------

def others(leg, group):
    return tuple(x for x in group if x != leg)


def Rq_piece(w):
    """R_q = 4 sum_{m,p} h_mp H_1 + 2 sum_{m,p,phi} h_{r,phi(r)} h_{s,phi(s)} H_2."""
    Rq = F(0)
    # single-hinge term
    for m in M:
        r, s = others(m, M)
        for p in P:
            h_mp = pp(w[p]**2 - w[m]**2)
            if h_mp != 0:
                Rq += 4 * h_mp * H1(w[m], w[p], w[r]+w[s], w[r]*w[s])
    # matching (double-hinge) term
    for m in M:
        r, s = others(m, M)
        for p in P:
            t, z = others(p, P)
            for (pr, ps) in ((t, z), (z, t)):   # the two bijections phi: r->pr, s->ps
                h_r = pp(w[pr]**2 - w[r]**2)
                h_s = pp(w[ps]**2 - w[s]**2)
                if h_r != 0 and h_s != 0:
                    c = w[r]*w[pr] + w[s]*w[ps]
                    Rq += 2 * h_r * h_s * H2(w[m], w[p], w[r]+w[s], w[r]*w[s], c)
    return Rq


def R0_piece(w):
    u = w[1] + w[2] + w[3]
    v = w[1]*w[2] + w[1]*w[3] + w[2]*w[3]
    em = w[1]*w[2]*w[3]
    ep = w[4]*w[5]*w[6]
    return H0(u, v, em, ep)


def RQ_piece(w):
    """R_Q = -32 sum_{m; {p,q}} (Q_{m;pq})_+^3 w_m w_t,  t = P\\{p,q}."""
    RQ = F(0)
    for m in M:
        for (p, q) in ((4, 5), (4, 6), (5, 6)):
            t = others(p, others(q, P))[0]  # the omitted plus leg
            Q = w[p]**2 + w[q]**2 - w[m]**2
            if Q > 0:
                RQ += -32 * Q**3 * w[m] * w[t]
    return RQ


def Hblk(B, c, d, w):
    """H(B;c,d) = B - (B-w_c^2)_+ - (B-w_d^2)_+ + (B-w_c^2-w_d^2)_+."""
    return B - pp(B - w[c]**2) - pp(B - w[d]**2) + pp(B - w[c]**2 - w[d]**2)


def Ppole_piece(w):
    """P_pole = -64 sum_{Q_{m;pq}>0} (w_m w_t Q^2 / d) H(min(w_m^2,Q);p,q) H(min(w_t^2,Q);r,s)."""
    Pp = F(0)
    for m in M:
        r, s = others(m, M)
        for (p, q) in ((4, 5), (4, 6), (5, 6)):
            t = others(p, others(q, P))[0]
            Q = w[p]**2 + w[q]**2 - w[m]**2
            if Q > 0:
                d = 2*(w[m]+w[p])*(w[m]+w[q])
                if d == 0:
                    raise ZeroDivisionError("d_{m;pq}=0 pole locus; evaluate off it")
                Hpq = Hblk(min(w[m]**2, Q), p, q, w)
                Hrs = Hblk(min(w[t]**2, Q), r, s, w)
                Pp += -64 * (w[m]*w[t]*Q**2) * Hpq * Hrs / d
    return Pp


# ---------------------------------------------------------------------------
# Assembly.
# ---------------------------------------------------------------------------

def components(w):
    """Return the four stripped pieces (g=1 building blocks)."""
    return {
        "P_pole": Ppole_piece(w),
        "R_Q": RQ_piece(w),
        "R_0": R0_piece(w),
        "R_q": Rq_piece(w),
    }


def A6_over_i(w, g=F(1)):
    """A_6 / i  =  g^{-3} ( P_pole + R_Q + R_0 + R_q )."""
    c = components(w)
    stripped = c["P_pole"] + c["R_Q"] + c["R_0"] + c["R_q"]
    return stripped / g**3


def as_w(seq):
    """Build a 1-indexed dict of Fractions from a length-6 iterable (legs 1..6)."""
    return {i+1: F(seq[i]) for i in range(6)}


if __name__ == "__main__":
    # Anchor self-test.
    w = as_w([F(-8), F(2), F(3), F(4), F(5), F(-6)])
    c = components(w)
    print("anchor omega = {-8,2,3,4,5,-6}")
    print("  P_pole =", c["P_pole"], " (expect 42588288/7)")
    print("  R_Q    =", c["R_Q"], " (expect -136630560)")
    print("  R_0    =", c["R_0"])
    print("  R_q    =", c["R_q"])
    print("  S=R_0+R_q =", c["R_0"] + c["R_q"], " (expect 129233568)")
    print("  A_6/i  =", A6_over_i(w), " (expect -9190656/7)")
