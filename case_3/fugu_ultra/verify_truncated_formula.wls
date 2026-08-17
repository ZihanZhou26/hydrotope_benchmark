(* Verification script for report.md.  This generated script imports only
   ../OnShellBG.m among pre-existing files. *)
code = Import[FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}], "Text"];
defs = StringSplit[code, "(* ================================================================ *)\n(*  VI. TESTS"][[1]];
ToExpression[defs];

Clear[pp, TP, FormulaAmp, TwoMinusKinematics, RelErr, BGOnShellOrLimit];
pp[x_] := If[x > 0, x, 0];
TP[m_Integer, t_, a_List] := Sum[(-1)^Length[S] pp[t - Total[S]]^m, {S, Subsets[a]}];

(* Two-minus closed form in the physical channel: choose p to be the one
   sigma=- leg whose frequency sign is shared by exactly n-3 sigma=+ legs;
   q is the other sigma=- leg. *)
FormulaAmp[ws_List, g_:1] := Module[{n=Length[ws], m, cands, a, p, q, R, F},
  m = n - 3;
  cands = Select[{1,2}, Function[a, Length[Select[Range[3,n], Sign[ws[[#]]] == Sign[ws[[a]]] &]] == m]];
  If[Length[cands] < 1, Return[$Failed]];
  a = cands[[1]]; p = ws[[a]]; q = ws[[3-a]];
  R = Select[Range[3,n], Sign[ws[[#]]] == Sign[p] &];
  F = TP[m, p^2, ws[[R]]^2];
  FullSimplify[I*2^(n-1)*q*p*F/g^(n-3)]
];
TwoMinusKinematics[n_Integer, freeW_List, g_:1] := Module[{sigmas},
  sigmas = Join[{-1, -1}, Table[1, n - 2]];
  MakeKinematics[n, freeW, sigmas, g]
];
RelErr[a_, b_] := Module[{den = Max[1, Abs[N[a, 50]], Abs[N[b, 50]]]}, N[Abs[a - b]/den, 20]];

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
  {4, {2, 3}, 1, "n=4, p smaller"},
  {4, {5, 1/2}, 2, "n=4, p larger, g=2"},
  {5, {2, 5/2, 3}, 1, "prompt-style"},
  {5, {1/10, 3, 7}, 1, "small p"},
  {5, {10, 1, 1}, 1, "p much larger"},
  {5, {2, -5/2, 3}, 1, "crossed sign, same channel"},
  {5, {-2, 5/2, -3}, 1, "time-reversed/crossed"},
  {6, {3/2, 2, 5/2, 3}, 1, "prompt-style"},
  {6, {1/10, 3, 5, 7}, 1, "small p"},
  {6, {10, 1, 2, 3}, 1, "p much larger"},
  {6, {2, -5, 3, 4}, 1, "crossed sign"},
  {7, {3/2, 2, 5/2, 3, 7/2}, 1, "prompt-style"},
  {7, {1/2, 2, 3, 4, 5}, 1, "small p"},
  {7, {4, 1, 2, 3, 5}, 3/2, "mixed magnitudes, g=3/2"}
};

Print["Two-minus truncated-power formula verification"];
Print[StringRiffle[{"n", "g", "freeW", "allW", "BG", "formula", "relerr", "note"}, " | "]];
Do[
  n = tc[[1]]; freeW = tc[[2]]; g = tc[[3]]; note = tc[[4]];
  {ks, ws} = TwoMinusKinematics[n, freeW, g];
  bg = BGOnShellOrLimit[n, freeW, g];
  fm = FormulaAmp[ws, g];
  err = If[fm === $Failed, $Failed, RelErr[bg, fm]];
  Print[StringRiffle[ToString /@ {n, g, InputForm[freeW], InputForm[ws], InputForm[bg], InputForm[fm], If[err === $Failed, "FAILED-CHANNEL", ScientificForm[err, 3]], note}, " | "]];
, {tc, cases}]
