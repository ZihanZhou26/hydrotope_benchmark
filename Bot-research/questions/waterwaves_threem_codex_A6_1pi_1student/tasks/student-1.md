# Task brief — student-1 — round 8 (2026-07-26) — LAST research round

## Situation
Your round-7 results are **independently CONFIRMED** by the PI:
- **[pi_v_026]** The banked A-piece core = an exact **four-block** partial fraction (s1_020). I checked it
  two ways vs *my own* 31-term core (not your $P/Q$): `sympy.cancel(fourblock − core)=0` for A **and** B,
  and exact-`Fraction` match to a fresh `bg_r8` at $40/40$ in-piece points per piece. **Banked.**
- **[pi_v_027]** Your no-go (s1_021) holds: reduced $H_A$ is genuinely rational ($\gcd(P,Q)=1$,
  $\deg Q_{\rm hom}=10$, factors $uv(r{+}u)(r{+}v)(s{+}u)(s{+}v)B_MB_P$), so a **pure** positive-part /
  box-spline master is impossible. The master **must** be a **rational signed-channel** object.

What's still missing is the **crux**: a second, **higher-degree** factored chamber (12ea165a03,
$\deg Q_{\rm hom}>10$ [pi_v_025]). Last round the technician sub-agent exhausted context on a 1400-pt
deg-13/14 batch and produced **no artifact**, so the master-object hypothesis is still **untested**.
**This is the last research round** — round 9 is a final summary with no new task.

## Task (one): crack the higher-degree chamber 12ea165a03 and test the signed-channel master
Fix the **tractability** failure (it was operational, not scientific): **reuse the 1050 stored exact
points** in `round7_pts_12ea165a03.json` (keys `base_f`, `base_sg`, `pts`), top up to ~1200–1400 with a
few hundred fresh in-piece points, and drive everything from a **file-writing script** registered as a
**lean nonblocking job** (small logs; never hold big dumps or the technician's full batch in context —
split into small steps and write intermediate results to files).

Deliver the **highest rung you can reach** on this ladder (each rung is an acceptable verified result):
1. **BEST — reconstruct & factor.** Push the $\omega_2$-dehomogenized (cone) modular rank scan to find
   the **first** $d$ with `nulldim>0` (try $d=13$, then $14$); CRT-reconstruct the null vector and
   `sympy.factor` $Q$. Report $\deg Q_{\rm hom}$ and its factors **against** A's
   $uv(r{+}u)(r{+}v)(s{+}u)(s{+}v)B_MB_P$ — i.e. exactly **which new signed factors appear**.
2. **If full factoring is too heavy — pin degree + identify factors.** State $\deg Q_{\rm hom}$ exactly
   (first $d$ with `nulldim>0`), and identify the new denominator factors by testing candidate **signed**
   blocks: triple sums $\omega_i+\omega_j+\omega_k$, the mixed-triple propagator branches $h_{ijk}$, and
   $1/h_{2345}$ with a sign selector (recall 12ea differs from A only in $\mathrm{sign}\,h_{2345}$ and in
   momentum walls touching legs $1,6$).
3. **Master-object test.** With A (four-block seed) + $\ge1$ higher-degree chamber in hand, test whether
   the four-block seed **augmented by extra sign-activated rational blocks** reproduces **both**. A single
   compact rational signed-channel sum that truncates to the four-block $H_A$ in the all-$+$ chamber and to
   12ea elsewhere is the goal; a **sharp ansatz-level negative** (the specific ansatz ruled out, with the
   reason) is an acceptable deliverable.

## Deliverables (verifiable)
- `bots/student-1/HANDOFF.md`: 12ea165a03's $\deg Q_{\rm hom}$ and factored/identified $Q$ (or the pinned
  degree + new factors), and the master-object result — a candidate rational signed-channel form **or**
  the precise obstruction.
- A **building-block evaluator** (`bots/student-1/code/`, **NO chamber coefficient table**) with a residual
  report vs **freshly built** `bg.cpp` on $\ge20$ generic points spanning the realized chambers,
  within-set permutations (minus $\{1,2,3\}$, plus $\{4,5,6\}$), a hierarchical regime (one $|\omega|$ much
  larger/smaller), and **two-sided** approaches to an $a_i-b_j$ wall, an $a_i+b_j-T$ wall, and
  $h_{2345}=0$. Exact rational where feasible; rel. error $\le 10^{-10}$ otherwise.
- Claims in `bots/student-1/claims.yaml` (`s1_022`, …) with evidence paths.

## Constraints
- Exact GMP rational for every load-bearing claim; `--double` only for scans. **Copy `bg.cpp`** before
  building — never edit the shared file. Hold **all 53 signs** constant for any in-piece degree/fit test.
- Do **not** rerun collected job `r6_piece_20260726T173931Z` (result: `no_fixed_den_fit`, already read).
  Register heavy fits to the `technician` sub-agent as a **small, staged** nonblocking `jobs/<id>.json` —
  cap the batch so it fits in context (one chamber, ~1300 pts, single degree per call), and have it write
  code + results to files before returning. If the technician fails again, fall back to rung (2).
- Only round 9 (final summary) remains after this. **Prioritize one verified structural advance** over a
  broad unverified sweep.

## Pointers (pull only as needed)
- Data: `round7_pts_12ea165a03.json` (1050 pts, base_f/base_sg/pts);
  `bots/student-1/data/round6_piece_report.json` (3 new bases + comparison matrices + $h_{16}$ signs).
- PI machinery to reuse: `bots/pi/code/round6_reconstruct.py` (cone/rank scan),
  `round6_extract_np.py` (CRT + `Fraction` validate + `sympy.factor`),
  `round7_newpiece_scan.py` (already retargets the scan at the fixed new bases),
  `round8_verify_fourblock.py` (the confirmed four-block seed evaluator).
- Reference: `bots/pi/code/round6_QP.txt`, `round6_QP_B.txt` (exact factored $P,Q$ for A/B);
  `summary/logic.yaml` (round8_headline, open_questions, next_actions); `question.md` (def of done,
  compactness bar); the two-minus box-spline as the structural template.
