# Fast exact (and double) BG oracle (`bg.cpp`)

`bg.cpp` is a faithful C++ transcription of `OnShellBG.m` (the Berends-Giele
recursion). The engine is templated on the scalar type, so the exact and fast
paths run the SAME algorithm. It is a **pure amplitude evaluator** — no
closed-form/answer — and is safe to give a blind agent.

Verified exact-equal to `OnShellBG.m`'s `BGAmplitude` on two- and three-minus
points (n=5,6,7).

```sh
g++ -O2 -std=c++17 -o bg tools/bg.cpp -lgmpxx -lgmp     # needs libgmp/libgmpxx

# exact rational (rigorous):
./bg -n 5 -w 2,3,5 -s -1,-1,-1,1,1            # on-shell solver  -> A_5 = i*(-25344)
./bg --amp -K <n momenta> -W <n omegas>       # raw BGAmplitude, arbitrary kinematics

# fast long-double mode (for bulk scans / fitting at higher n):
./bg --double -n 8 -w 2,3,5,7,11,13 -s -1,-1,-1,1,1,1,1,1
```

`-w/-s` requires `sigma_1 + sigma_n = 0` (same kinematic solver as `MakeKinematics`).

Performance: n<=7 is sub-second (exact). `--double` is ~4x faster than exact and
avoids the exact-rational blow-up at large n (n=8 three-minus: ~9 s double vs
~35 s exact). The dominant cost is the n! Vertex permutation sum (algorithmic, so
both scalar types pay it) — n>=9 is expensive in either mode. Use `--double` for
exploration/fitting and re-confirm any final formula in the default exact mode.
