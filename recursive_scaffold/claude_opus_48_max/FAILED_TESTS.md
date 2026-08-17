# FAILED_TESTS

The final formula passes every test **inside its claimed domain** (the
interleaving region; see SCOPE.md). It does **not** pass the following tests,
which lie **outside the claimed domain** (non-interleaving: some plus leg `|ω|`
is below both minus `|ω|` or above both). These are kept here per the scaffold —
they are genuine `BGAmplitude` values that the formula does not reproduce, and
they are exactly why the domain is narrowed. All values are `a_n = Im(A_n)`,
g=1, exact rational (from `verify1a.py`; `A_n = i·a_n`).

| n | allW = (ω₁..ωₙ), minus legs first | BGAmplitude a_n (exact) | formula a_n | in domain? |
|---|---|---|---|---|
| 5 | (−127/54, 7/3, −1/3, 5/2, −58/27) | −47849536/531441 | −17075912/6561 | NO (non-interleaving) |
| 5 | (44/21, 1/3, −2/3, −2, 5/21) | 1284800/12252303 | 704/5103 | NO |
| 6 | (608/93, 7/2, 1/3, −2, −7, −85/62) | 983987200/268119 | 125178536/93 | NO |
| 6 | (49/9, −3, −1/3, −5/3, 4, −40/9) | −5331200/729 | −381024 | NO |
| 7 | (−97, 7/3, 2, −5, −4, 5, 290/3) | −27697116160/2187 | −250515192256/19683 | NO |
| 7 | (−1033/198, −1, 5, 5/3, 1/3, −1/2, −28/99) | 395962618240/28529701497 | 33056/99 | NO |
| 5 | fw={2,3,1/50} → (−37751/12550, 2, 3, 1/50, −505/251) | −754982249/2451171875 | −9664256/6275 | NO (soft plus leg) |
| 5 | fw={50,2,3} → (−269/55, 50, 2, 3, −2756/55) | −3098880/11 | −45072472075168/20131375 | NO (large free minus) |

Summary of the broad scan (`verify1a.py`): on random MakeKinematics points the
formula passed **every** interleaving point (n=5: 12/12, n=6: 10/10, n=7: 11/11)
and **failed every** non-interleaving point (n=5: 0/28, n=6: 0/30, n=7: 0/29) —
a clean dichotomy confirming the domain boundary.

**No failures remain inside the claimed (interleaving) domain.**

Abandoned candidate (not a final-formula failure, kept for the record): C1, the
homogeneous-polynomial ansatz in (e₁,e₂,P₃), was inconsistent on the very first
exact fit (a_n is not polynomial) and was discarded — it never became the
candidate.
