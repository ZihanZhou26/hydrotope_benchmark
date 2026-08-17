Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
Clear[mag];
mag[k_] := Module[{v = k /. $signRules},
  If[NumericQ[v] && v != 0, Sign[v]*k, Print["WARN sign ", k]; Abs[k]]];
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* symbolic A_n with g kept, base region (positive free freqs) *)
symF[n_, baseFree_] := Module[{sig, ks, ws, amp, freeSym, baseRules},
  sig = twoMinus[n];
  freeSym = Table[Symbol["v" <> ToString[i]], {i, 1, n - 2}];
  baseRules = Thread[freeSym -> baseFree];
  {ks, ws} = MakeKinematics[n, freeSym, sig, g];
  $signRules = Append[baseRules, g -> 1];   (* g>0 region *)
  amp = BGAmplitude[ks, ws, g];
  amp = FullSimplify[amp, Assumptions -> (g > 0 && And @@ (# > 0 & /@ freeSym))];
  {ws, amp, freeSym, baseRules}
];

Module[{r},
  r = symF[5, {3/2, 2, 5/2}];
  Print["=== n=5 ==="];
  Print["A_5(v,g) = ", r[[2]]];
  Print["  /. (express w1,w2): w1=", r[[1,1]], "  w2=", r[[1,2]]];
  Print["  candidate 16 I w1 w2^5/g^2 - A : ",
    FullSimplify[16 I r[[1,1]] r[[1,2]]^5 / g^2 - r[[2]], Assumptions->g>0]];
];

Module[{r},
  r = symF[6, {3/2, 2, 5/2, 3}];
  Print["\n=== n=6 ==="];
  Print["A_6(v,g) = ", r[[2]]];
  Print["  candidate 32 I w1 w2^7/g^3 - A : ",
    FullSimplify[32 I r[[1,1]] r[[1,2]]^7 / g^3 - r[[2]], Assumptions->g>0]];
];

Print["\nDONE probe5"];
