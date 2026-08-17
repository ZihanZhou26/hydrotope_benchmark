# Exact round-3 cell reconstruction: `round3_context_c`

- seed `(B,c,e)`: `(-30, 4, -5)`
- quotient-basis dimensions: degree 8 = 285, degree 6 = 140
- left solve: rank 285, 20/20 exact holdouts, 230 nonzero coefficients
- right solve: rank 285, 20/20 exact holdouts, 228 nonzero coefficients
- exact divisibility: `R_L-R_R = q_24 H_24`: `True`
- terms: jump 50, H24 29, H14 29
- residual symmetry: H14 swap(2,3) `False`; swap(5,6) `True`
- factorization: `32*(w1**4*w2*w4 + w1**4*w3**2 - w1**3*w2*w3**2 - w1**3*w3**3 - w1**2*w2**2*w3**2 - 4*w1**2*w2*w3**3 - w1**2*w2*w3**2*w4 - 2*w1**2*w2*w4**3 - w1**2*w3**4 - 2*w1**2*w3**3*w4 - 3*w1**2*w3**2*w4**2 - w1*w2**3*w3**2 - 2*w1*w2**2*w3**3 - w1*w2**2*w3**2*w4 - 2*w1*w2*w3**4 - 3*w1*w2*w3**3*w4 - 2*w1*w2*w3**2*w4**2 - w1*w3**5 - w1*w3**4*w4 - 2*w1*w3**3*w4**2 - 2*w1*w3**2*w4**3 - w2**3*w3**3 + w2**2*w3**3*w4 - w2*w3**5 + w2*w3**4*w4 + w2*w3**3*w4**2 - 2*w2*w3**2*w4**3 + w2*w4**5 - w3**3*w4**3)`
- runtime seconds: `53.028`

Full coefficients and holdouts: `/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/bots/student-2/data/round3_context_c.json`.