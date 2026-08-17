(* Verification script for the two-minus formula in report.md.
   It imports only ../OnShellBG.m plus this generated script. *)
code = Import[FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}], "Text"];
defs = StringSplit[code, "(* ================================================================ *)\n(*  VI. TESTS"][[1]];
ToExpression[defs];

Clear[FormulaAmp, TwoMinusKinematics, RelErr, BGOnShellOrLimit];
FormulaAmp[ws_List, g_:1] := Module[{n = Length[ws]}, I*2^(n - 1)*ws[[1]]*ws[[2]]^(2 n - 5)/g^(n - 3)];
TwoMinusKinematics[n_Integer, freeW_List, g_:1] := Module[{sigmas},
  sigmas = Join[{-1, -1}, Table[1, n - 2]];
  MakeKinematics[n, freeW, sigmas, g]
];
RelErr[a_, b_] := Module[{den = Max[1, Abs[N[a, 50]], Abs[N[b, 50]]]}, N[Abs[a - b]/den, 20]];

(* n=4 is a removable 0/0 in the unmodified BG recursion.  Evaluate the
   on-shell value as the eps->0 limit of an energy-conserving deformation. *)
BGOnShellOrLimit[4, freeW_List, g_:1] := Module[{w2=freeW[[1]], w3=freeW[[2]], eps, ws, sig, ks, amp},
  sig = {-1, -1, 1, 1};
  ws = {-w3 - eps, w2, w3, -w2 + eps};
  ks = sig*ws^2/g;
  amp = Quiet[BGAmplitude[ks, ws, g]];
  FullSimplify[Limit[amp, eps -> 0, Direction -> "FromAbove"]]
];
BGOnShellOrLimit[n_Integer /; n >= 5, freeW_List, g_:1] := Module[{ks, ws},
  {ks, ws} = TwoMinusKinematics[n, freeW, g];
  FullSimplify[BGAmplitude[ks, ws, g]]
];

cases = {
  {4, {2, 3}, 1, "generic n=4"},
  {4, {1/10, 7}, 1, "small omega2 n=4"},
  {4, {5, 1/2}, 2, "g=2 n=4"},
  {5, {2, 5/2, 3}, 1, "prompt-style"},
  {5, {1, 3, 7}, 1, "spread"},
  {5, {1/10, 3, 7}, 1, "small omega2"},
  {5, {10, 11, 12}, 3/2, "large, g=3/2"},
  {6, {3/2, 2, 5/2, 3}, 1, "prompt-style"},
  {6, {1, 3, 5, 7}, 1, "spread"},
  {6, {1/10, 3, 5, 7}, 1, "small omega2"},
  {6, {10, 11, 12, 13}, 2, "large, g=2"},
  {7, {3/2, 2, 5/2, 3, 7/2}, 1, "prompt-style"},
  {7, {1/2, 2, 3, 4, 5}, 1, "small-ish omega2"},
  {7, {4, 5, 6, 7, 8}, 3/2, "large, g=3/2"}
};

Print["Two-minus formula verification (A_formula = i 2^(n-1) w1 w2^(2n-5)/g^(n-3))"];
Print[StringRiffle[{"n", "g", "freeW", "allW", "BG", "formula", "relerr", "note"}, " | "]];
Do[
  n = tc[[1]]; freeW = tc[[2]]; g = tc[[3]]; note = tc[[4]];
  {ks, ws} = TwoMinusKinematics[n, freeW, g];
  bg = BGOnShellOrLimit[n, freeW, g];
  fm = FullSimplify[FormulaAmp[ws, g]];
  err = RelErr[bg, fm];
  Print[StringRiffle[ToString /@ {n, g, InputForm[freeW], InputForm[ws], InputForm[bg], InputForm[fm], ScientificForm[err, 3], note}, " | "]];
, {tc, cases}]
