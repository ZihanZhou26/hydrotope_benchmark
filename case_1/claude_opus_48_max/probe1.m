Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

gVal = 1;

(* two-minus sigma for given n *)
twoMinusSigma[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* compute A_n at given free frequencies (length n-2) in two-minus sector *)
ampTwoMinus[n_, freeW_] := Module[{sig, ks, ws},
  sig = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, gVal];
  {ks, ws, BGAmplitude[ks, ws, gVal]}];

Do[
 Module[{freeW, ks, ws, amp, t},
  Switch[n,
   4, freeW = {7/2, 5/2},
   5, freeW = {3/2, 5/2, 7/2},
   6, freeW = {3/2, 2, 5/2, 7/2},
   7, freeW = {3/2, 2, 5/2, 3, 7/2}];
  t = AbsoluteTiming[{ks, ws, amp} = ampTwoMinus[n, freeW];][[1]];
  Print["=== n = ", n, " ==="];
  Print["  freeW = ", freeW];
  Print["  all w = ", ws];
  Print["  all k = ", ks];
  Print["  sum w = ", Total[ws], "   sum sigma w^2 (=g sum k) = ", gVal*Total[ks]];
  Print["  A_", n, " = ", amp, "  = ", N[amp, 16]];
  Print["  time = ", t, " s"];
  ],
 {n, {4, 5, 6, 7}}]

(* homogeneity check at n=5: scale free freqs by lambda=2 *)
Print["--- homogeneity check (n=5) ---"];
Module[{a1, a2, freeW},
  freeW = {3/2, 5/2, 7/2};
  a1 = ampTwoMinus[5, freeW][[3]];
  a2 = ampTwoMinus[5, 2*freeW][[3]];
  Print["  A(w)      = ", a1];
  Print["  A(2w)     = ", a2];
  Print["  ratio     = ", a2/a1, "  = 2^", N[Log[2, a2/a1]]];
];
Module[{a1, a2, freeW},
  freeW = {3/2, 2, 5/2, 7/2};
  a1 = ampTwoMinus[6, freeW][[3]];
  a2 = ampTwoMinus[6, 2*freeW][[3]];
  Print["  n=6 ratio = ", a2/a1, "  = 2^", N[Log[2, a2/a1]]];
];
