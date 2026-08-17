Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];

twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* --- (A) g-dependence: compute A_5 with symbolic g at a fixed rational point --- *)
Print["=== (A) g-dependence ==="];
Module[{n=5, freeW={3/2,2,5/2}, sig, ks, ws, amp},
  sig = twoMinus[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, g];   (* g symbolic *)
  amp = BGAmplitude[ks, ws, g];
  Print["A_5(g) = ", Simplify[amp]];
];

(* --- (B) homogeneity in omega at g=1: scale all free freqs by lambda --- *)
Print["\n=== (B) omega-homogeneity (g=1) ==="];
Module[{n=5, base={3/2,2,5/2}, sig, vals},
  sig = twoMinus[n];
  vals = Table[
    Module[{ks,ws,amp}, {ks,ws}=MakeKinematics[n, lam*base, sig, 1];
      amp = BGAmplitude[ks, ws, 1]; {lam, Simplify[amp]}],
    {lam, {1, 2, 3}}];
  Print["A_5 at lambda*base: ", vals];
  Print["ratios A(2)/A(1), A(3)/A(1): ",
    {vals[[2,2]]/vals[[1,2]], vals[[3,2]]/vals[[1,2]]} //Simplify];
];

(* --- (C) same homogeneity check for n=6 --- *)
Print["\n=== (C) omega-homogeneity n=6 (g=1) ==="];
Module[{n=6, base={3/2,2,5/2,3}, sig, vals},
  sig = twoMinus[n];
  vals = Table[
    Module[{ks,ws,amp}, {ks,ws}=MakeKinematics[n, lam*base, sig, 1];
      amp = BGAmplitude[ks, ws, 1]; {lam, Simplify[amp]}],
    {lam, {1, 2}}];
  Print["A_6 ratios A(2)/A(1): ", vals[[2,2]]/vals[[1,2]]//Simplify];
];

Print["\nDONE probe2"];
