# Pole-batch exact batch report

Generated: 2026-07-26T07:44:36.410483Z

## Inputs
- target samples: 80
- actual samples: 77
- bg binary: `/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/bots/student-1/bg`
- source plan: exact=80, integer=80; selected exact=72, integer=5
- seed failure summary: accepted=77 failed_bg=3 rejected_zero_denom=0

## Structural coverage
- distinct sorted words: 4
- distinct chamber signatures: 15
- selected sorted-word counts: {'+---++': 11, '-+++--': 23, '-++-+-': 6, '-++--+': 37}
- selected chamber-signature counts: {'-------++--++--++--++--++++++--++------++--++--++--++--+++++++': 1, '-------++--++--++--++--++--++--++--++--++--++--++--++--+++++++': 2, '-------++--++--++------++--++--++--++--++++++--++--++--+++++++': 1, '-------+-+-+-+-+-+-+-+-+++++++-+-------+-+-+-+-+-+-+-+-+++++++': 17, '-------+-+-+-+-+-+-+-+-+++++-+-+-+-----+-+-+-+-+-+-+-+-+++++++': 1, '-------+-+-+-+-+-+-+-+-+++-+++-+---+---+-+-+-+-+-+-+-+-+++++++': 1, '-------+-+-+-+-+-+-+-+-+++-+-+-+-+-+---+-+-+-+-+-+-+-+-+++++++': 1, '-------+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+++++++': 20, '-------+-+-+-+-+-+-----+-+-+-+-+-+-+-+-+++++-+-+-+-+-+-+++++++': 1, '-------+-+-+-+-+---+---+-+-+-+-+-+-+-+-+++-+++-+-+-+-+-+++++++': 1, '-------+-+-+-+-+-------+-+-+-+-+-+-+-+-+++++++-+-+-+-+-+++++++': 8, '-------+-------+++++++-+++++++-+-------+-------+++++++-+++++++': 3, '-------+-------++--++--++--++--++--++--++--++--+++++++-+++++++': 2, '-------+-------+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+++++++-+++++++': 10, '-------+-------+-------+-------+++++++-+++++++-+++++++-+++++++': 8}

## A4 (-,-,+,+) on-shell calibration
- requested: 6
- attempted (grid points): 4032
- collected: 0
- obstructions: all real resonant 4pt seeds are exchange-degenerate in this signature; no reliable A4 calibration point found.

## Explicit kernel formulas
- B_T = -64 * w_m * w_t * Q * H(min(w_m^2, Q); w_p, w_q) * H(min(w_t^2, Q); w_r, w_s)
- Q = w_p^2 + w_q^2 - w_m^2, d = 2 (w_m+w_p)(w_m+w_q)
- S1 = sum(Q * B_T / d) with propagator factor D = d / Q

## S1 diagnostics (primary candidate C=1)
- total points: 77
- integer points with integral residual y- S1: 16/16
- rational points with L^8(y-S1) integral: 61/61
- nonzero residual count: 77
- raw residual denominator histogram: {'1': 18, '4': 1, '8': 7, '32': 6, '125': 1, '216': 1, '289': 12, '343': 2, '729': 7, '1331': 1, '2048': 2, '2197': 2, '2744': 1, '3375': 1, '5832': 1, '6561': 6, '10648': 1, '390625': 6, '5764801': 1}
- scaled residual denominator histogram: {'1': 61}

## S0 diagnostics (negative control)
- S0 is degree-6; y and S1 are degree-8; no dimensionless constant coefficient can represent the pole part.
- tested C=1 on S0: nonzero residual points=77
- raw residual denominator histogram: {'1': 17, '2': 4, '5': 2, '6': 5, '7': 11, '11': 1, '13': 2, '17': 3, '18': 1, '22': 1, '68': 1, '85': 7, '243': 6, '340': 1, '768': 1, '1280': 1, '2187': 5, '10935': 1, '78125': 3, '234375': 2, '546875': 1, '823543': 1}

## Near-pole diagnostics
- status: ok_non_normalizing
- notes: non-normalizing finite-path family, not used for ranking coefficients
- ranking_used: False
- endpoint |d*(y-S1)| magnitudes: {'+ branch': {'start_abs_dY': '2033904722458889970015/17179869184', 'end_abs_dY': '9873090905917543588951942735723285/2898970305929165116070244'}, '- branch': {'start_abs_dY': '5280550372603519016293/55788550416', 'end_abs_dY': '11552096932766128538004394248108443/3526974145950713568133956'}}
  - step 1/1: |dY|=2033904722458889970015/17179869184
  - step 1/2: |dY|=186923877203450894451430373/6126315941057796
  - step 1/3: |dY|=136273259944822326898849697611/10011291503906250000
  - step 1/4: |dY|=14302853441750279971001350079793/1866585911861003723776
