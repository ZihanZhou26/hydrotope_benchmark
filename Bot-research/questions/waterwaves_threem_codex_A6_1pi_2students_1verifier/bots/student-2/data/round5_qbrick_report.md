# Round-5 Q-wall brick reconstruction

- built bg: `/home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/bots/student-2/bg`
- build command: `g++ -O2 -std=c++17 -o /home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/bots/student-2/bg /home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_2students_1verifier/bots/student-2/bg.cpp -lgmpxx -lgmp`
- candidate lines checked: `27`
- wall attempts: `558`
- certified walls: `27`
- representative walls (q_1_46): `3`

## Channel coverage
- q_1_45: `3`
- q_1_46: `3`
- q_1_56: `3`
- q_2_45: `3`
- q_2_46: `3`
- q_2_56: `3`
- q_3_45: `3`
- q_3_46: `3`
- q_3_56: `3`

- representative solve status: `insufficient_rank`
- representative residual pass: `0` / `0`

## Channel transport checks

## Fixed selector candidate `-16*max(w_m^2,w_t^2)` checks
- summary: `648` / `648`
- branch selection: m=456, t=192, tie=0
- q_1_45: `72` / `72` | m=72, t=0, tie=0
- q_1_46: `72` / `72` | m=72, t=0, tie=0
- q_1_56: `72` / `72` | m=72, t=0, tie=0
- q_2_45: `72` / `72` | m=24, t=48, tie=0
- q_2_46: `72` / `72` | m=48, t=24, tie=0
- q_2_56: `72` / `72` | m=72, t=0, tie=0
- q_3_45: `72` / `72` | m=0, t=72, tie=0
- q_3_46: `72` / `72` | m=24, t=48, tie=0
- q_3_56: `72` / `72` | m=72, t=0, tie=0

## Fixed diagnostic `-16*w_m^2` checks
- summary: `456` / `648`
- q_1_45: `72` / `72`
- q_1_46: `72` / `72`
- q_1_56: `72` / `72`
- q_2_45: `24` / `72`
- q_2_46: `48` / `72`
- q_2_56: `72` / `72`
- q_3_45: `0` / `72`
- q_3_46: `24` / `72`
- q_3_56: `72` / `72`