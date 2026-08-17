#!/usr/bin/env python3
"""PI round-8 INDEPENDENT verification of student s1_020 (the four-block form).

Claim under test (student round 7, derivations/round7_four_block_channel_form.md):
  With (u,v,r,s)=(w2,w3,w4,w5), Om=u+v+r+s,
    B_M = u^2+v^2+uv+ur+us+vr+vs+rs,
    B_P = r^2+s^2+uv+ur+us+vr+vs+rs,
    L   = (u+r)(u+s)(v+r)(v+s),
    C(u;r,s) = r^3(u+s)+s^3(u+r),
  the banked 31-term A-piece core H_A equals the FOUR-BLOCK form
    H_A = 64 rs (r^2+s^2)/B_P
        - 32 r^2 s^2 (r^2+s^2) Om / (u (u+r)(u+s) B_M)
        - 32 rs Om C(u;r,s) / (u L)
        - 64 rs (r^2+s^2)(u+r+s) / (v (u+r)(u+s))
  and H_B(u,v,r,s) = H_A(r,s,u,v).

Two independent PI checks, transcribed BY THE PI from the derivation:
  (1) SYMBOLIC: cancel( fourblock_H_A - core_H_A ) == 0 as a rational function of
      (u,v,r,s), where core_H_A is the PI's own round-7 transcription of the
      31-term core (round7_verify_compact.Fpoly/H_A). Independent of the
      student's reconstructed P_A/Q_A files.
  (2) NUMERIC: fourblock_H_A (and fourblock_H_B via the swap) reproduce a FRESH
      bg_r8 exactly (fractions.Fraction) at in-piece points of pieces A and B.
"""
import sys, os
from fractions import Fraction as F
import sympy as sp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import round7_verify_compact as r7   # reuse bg harness + PI's own 31-term core

# point bg_r7 module at the fresh round-8 binary
r7.BG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg_r8")


def fourblock_H_A_vals(u, v, r, s):
    """Four-block H_A evaluated with any field supporting +,-,*,/ (Fraction or sympy)."""
    Om = u + v + r + s
    e2 = u*v + u*r + u*s + v*r + v*s + r*s
    B_M = u**2 + v**2 + e2
    B_P = r**2 + s**2 + e2
    L = (u + r)*(u + s)*(v + r)*(v + s)
    C = r**3*(u + s) + s**3*(u + r)
    t1 = 64*r*s*(r**2 + s**2) / B_P
    t2 = -32*r**2*s**2*(r**2 + s**2)*Om / (u*(u + r)*(u + s)*B_M)
    t3 = -32*r*s*Om*C / (u*L)
    t4 = -64*r*s*(r**2 + s**2)*(u + r + s) / (v*(u + r)*(u + s))
    return t1 + t2 + t3 + t4


def fourblock_H_A(om):
    return fourblock_H_A_vals(om[1], om[2], om[3], om[4])


def fourblock_H_B(om):
    # H_B(u,v,r,s) = H_A(r,s,u,v)  => swap (u,v)<->(r,s)
    u, v, r, s = om[1], om[2], om[3], om[4]
    return fourblock_H_A_vals(r, s, u, v)


def symbolic_check():
    u, v, r, s = sp.symbols('u v r s')
    fb = fourblock_H_A_vals(u, v, r, s)
    # PI's own 31-term core H_A (round7 transcription), in the same variables
    m1, m2 = u + v, u*v
    p1, p2 = r + s, r*s
    Om = u + v + r + s
    e2 = u*v + u*r + u*s + v*r + v*s + r*s
    B_M = e2 + u**2 + v**2
    B_P = e2 + r**2 + s**2
    L = (u + r)*(u + s)*(v + r)*(v + s)
    Fp = r7.Fpoly(m1, p1, m2, p2)  # sympy expr since args are sympy
    core = -32*r*s*Om*Fp / (u*v*L*B_M*B_P)
    diff = sp.cancel(fb - core)
    print("SYMBOLIC  cancel(fourblock_H_A - core_H_A) =", diff)
    # also confirm H_B swap consistency: fourblock_H_B via swap equals swapped core
    fbB = fourblock_H_A_vals(r, s, u, v)
    coreB = -32*u*v*Om*r7.Fpoly(p1, m1, p2, m2) / (r*s*L*B_M*B_P)
    diffB = sp.cancel(fbB - coreB)
    print("SYMBOLIC  cancel(fourblock_H_B - core_H_B) =", diffB)
    return diff == 0 and diffB == 0


if __name__ == "__main__":
    print("PI round-8 independent check of s1_020 (four-block form)\n")
    print("bg binary:", r7.BG)
    print("== check 1: SYMBOLIC identity (four-block == PI's 31-term core) ==")
    sym_ok = symbolic_check()
    print()
    print("== check 2: NUMERIC vs fresh bg_r8 (exact Fraction, in-piece) ==")
    a_ok, a_bad = r7.run_piece("piece A / fourblock_H_A", [9, -8, -3, -4], fourblock_H_A)
    b_ok, b_bad = r7.run_piece("piece B / fourblock_H_B", [4, 3, 8, 7], fourblock_H_B)
    print()
    ok = sym_ok and a_bad == 0 and b_bad == 0 and a_ok > 0 and b_ok > 0
    print(f"RESULT: symbolic={'PASS' if sym_ok else 'FAIL'}  "
          f"numeric A={a_ok}/{a_ok+a_bad} B={b_ok}/{b_ok+b_bad}  "
          f"=> {'ALL PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)
