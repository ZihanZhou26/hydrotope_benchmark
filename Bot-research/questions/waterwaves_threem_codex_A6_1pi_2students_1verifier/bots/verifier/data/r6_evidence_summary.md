# Round-6 verifier evidence summary

Oracle: bots/verifier/code/bg_r6 (md5 41715c4af3ee5a61b1c4bfce40426ac8, byte-identical
to shared bg.cpp and both students' copies). Pipeline: bots/verifier/code/r6_core.py
(exact Fraction; P_pole/R_Q transcribed from written formulas; amplitudes only from bg_r6 --amp).

## Anchor reproduction (r6_core.py)
- A6/i = -9190656/7 ; P_pole form1 == form2 = 42588288/7 ; R_spline = -7396992
- R_Q = -136630560 ; S = R_spline - R_Q = 129233568   (== student-1 s1_008 anchor)

## Check A — R_Q global re-confirmation (r6_checkA.json)
Isolated Q-wall crossings: 24/24 have R_spline JUMP while S=R_spline-R_Q is SMOOTH
and CONTINUOUS. Coverage: channels {(0,3,4),(0,3,5),(0,4,5),(1,3,4),(2,3,4)},
4 q-chambers, 4 energy-sign chambers {++--+-,+----+,-++++-,---+++}.
(Plus round-5's 27/27 over 9 channels x 4 chambers.)  => R_Q = -32 sum (Q_{m;pq})_+^3 w_m w_tbar CONFIRMED.

## Check B — S structure (r6_checkB2.py)
- S dual-S3 symmetric: 0/36 permutation violations. Degree-8 homogeneous: yes.
- Within a single chamber S is a general (non-symmetric) deg-8 poly living in the
  285-dim on-shell space (Hilbert series (1+t)/(1-t)^4, [t^8]=285) — matches student-1's
  "rank-285". The 17-dim dual-symmetric basis is only for the GLOBAL R_0, not S per chamber.

## Check C — cure test of student-2 R_q^cand (s2_011) (r6_checkC.json)
Guard: core=F+(a+b)D reduces to the round-3-verified F11 same-energy brick (exact).
T = S - R_q^cand tested across 18 isolated q-walls:
  S jumps (control):                 18/18
  T = S - R_q^cand SMOOTH:            0/18
  T = S - R_q^cand still JUMPS:       18/18   => candidate does NOT yield a smooth global R_0.

## Check C2 — the per-wall brick is LOCALLY correct (r6_checkC2.py)
At 24 isolated q-wall crossings (all minus-block environments):
  jump divisible by q_mp (order-1):                 24/24
  H_extract(t0) == -32 beta^2 [F+(a+b)D] (F11 gen): 24/24  (guard vs BG)
  H_extract == student-2 H_cand OFF the wall:       24/24  (the crossed (m,p) brick is right)

## Check C3 — same-sector ties are NOT the culprit (r6_checkC3.py)
20/20 isolated same-sector magnitude ties: S smooth AND R_q^cand smooth.

## Debug — the actual failure mechanism (r6_debug.py + block-switch check)
At the q_{23}=0 wall on line P=(8,2,-3,-5,4,-6), d=(3,0,1,-3,0,-1), t0=-1/2:
  S jump                         = -6726202626037344/152587890625
  brick (2,3) term jump          = -6726202626037344/152587890625   (== S jump; the (m,p) brick is right)
  brick (1,4) term jump          = -20269364451552/48828125         (SPURIOUS)
  brick (1,5) term jump          = 31539155654876793183/1220703125000 (SPURIOUS)
Cause: brick (1,4)'s four-leg beta argmin flips leg3(plus)->leg2(minus) across |w2|=|w3|;
student-2's plus-block and minus-block DISAGREE there:
  H_cand(1,4) below = -1490802280435/12800000  vs  above = -1439384171371/12800000
while its own wall q_{14}=12 is uncrossed. So the two-block beta-selector injects a
spurious discontinuity at every q-wall via the OTHER bricks -> R_q^cand not continuous
-> no smooth global R_0. This is exactly student-1's "environment dependence beyond the
four-leg-minimum selector" (rank 17<18), independently reproduced and localized.
