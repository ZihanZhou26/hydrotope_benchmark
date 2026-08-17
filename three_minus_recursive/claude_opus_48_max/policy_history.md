# policy_history.md — record of every policy change

Each entry: trigger (A/B), diagnosis, old version -> new version, the exact rule
change, and the next action that used the updated rule.

---

## v0 (initial)
The mandated starting policy. No trigger; this is the baseline.
Rules: (1) build reliable oracle harness; (2) collect exact small-case data;
(3) infer simple invariants; (4) propose simplest candidate explaining a
nontrivial subset; (5) try to break the candidate before trusting it.

---

(updates appended below)

## v0 -> v1 (Trigger B: two candidates, no passing data)
- Trigger: B. Candidates C2a (A1, sum over minus-pairs) and C2b (B1, sum over plus-pairs)
  at n=6 both passed 0/58 exact points — two attempts in a row with no inputs passed.
- Habit that failed: rule 4 ("propose the simplest candidate explaining a nontrivial
  subset"). At n=6 the simplest pure-polynomial box-spline candidate explains NONE of the
  data, because the n=6 amplitude is RATIONAL (carries propagator-denominator poles), not
  piecewise-polynomial like n<=5.
- Diagnosis/implication: the analytic structure (polynomial vs rational; pole/denominator
  factors; chamber walls) MUST be determined before guessing a closed form. The huge
  denominators in the oracle's n=6 B values (e.g. .../301805364403125) were the tell.
- Rule change: added rule 6 (map analytic structure first via scans/line-fits/symbolic).
- Next action that uses rule 6: the chamber/pole mapping (ACTION_TRACE steps 7,8,9 —
  negative-t scan, wall-free exact rational fit, 2-var symbolic chamber computation) and
  the next n=6 closed-form candidate, which will be rational (numerator / product of
  propagator denominators), not a pure box spline.
- Honesty note: steps 7-9 were already the realization that drove this rule; v1 formalizes
  it. All n=6 closed-form CANDIDATES from here cite rule 6.
