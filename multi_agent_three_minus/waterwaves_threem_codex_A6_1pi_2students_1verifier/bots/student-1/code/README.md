# student-1 exact oracle + A6 pole checks

```bash
cd /home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier

# build exact oracle in this student sandbox
cp bg.cpp bots/student-1/bg.cpp
(cd bots/student-1 && g++ -O2 -std=c++17 bg.cpp -lgmpxx -lgmp -o bg)

# final exact run: fresh BG evaluations over the full diverse seed set
python3 bots/student-1/code/pole_batch.py --qdir . --samples 80 --a4-checks 6 --near-pole

# optional: regenerate without near-pole diagnostics
python3 bots/student-1/code/pole_batch.py --qdir . --samples 80 --a4-checks 6
```

Outputs
- `bots/student-1/data/pole_results.json` (machine-readable run payload)
- `bots/student-1/derivations/pole_batch_report.md` (compact summary)

Notes
- `S1 = sum Q*B_T/d_T` is the degree-eight pole formula. The script
  independently recomputes every amplitude with the freshly built exact BG
  binary.
- `S0 = sum B_T/d_T` is retained only as a degree-six negative control.
- The frequencies in `data/exact_samples.json` are used only as diverse
  kinematic seeds; stored amplitudes are never trusted or read as oracle
  answers. No chamber coefficient table is loaded.
- Real resonant `(-,-,+,+)` kinematics are necessarily exchange-degenerate,
  so pointwise BG A4 calibration collects zero safe points. The obstruction is
  recorded explicitly instead of evaluating the singular locus.
