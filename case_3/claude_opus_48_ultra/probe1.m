Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];

gVal = 1;

twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

probe[n_, freeW_] := Module[{sig, ks, ws, amp, t},
  sig = twoMinus[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, gVal];
  t = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal]][[1]];
  Print["n=", n, "  freeW=", freeW];
  Print["   all w = ", ws];
  Print["   all k = ", ks];
  Print["   sum w = ", Total[ws], "   sum sig*w^2 = ", Total[sig*ws^2]];
  Print["   A_", n, " = ", Simplify[amp]];
  Print["   A_", n, " (N) = ", N[amp, 20]];
  Print["   time = ", Round[t, 0.01], " s\n"];
  {n, freeW, ws, amp}
];

(* n=4: free = {w2, w3}, with sigma2=-1, sigma3=+1 *)
probe[4, {3/2, 2}];
probe[4, {2, 5}];
probe[4, {7/3, 11/5}];

(* n=5: free = {w2,w3,w4} *)
probe[5, {3/2, 2, 5/2}];
probe[5, {2, 3, 7}];

(* n=6 *)
probe[6, {3/2, 2, 5/2, 3}];

(* n=7 *)
probe[7, {3/2, 2, 5/2, 3, 7/2}];

Print["DONE probe1"];
