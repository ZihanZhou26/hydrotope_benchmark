Get["codex_work/bg_core.wl"];

PrintCase[free_] := Module[{ws, ks, amp, sigmas, n, subsetSums},
  n = Length[free] + 2;
  sigmas = Join[{-1, -1}, Table[1, n - 2]];
  {ks, ws} = TwoMinusKinematics[free];
  amp = Simplify[BGAmplitude[ks, ws, 1]/I];
  subsetSums = Sort[DeleteCases[Table[Total[ks[[s]]], {s, Subsets[Range[n], {1, n - 1}]}], 0]];
  Print["free=", free, " ws=", ws, " ampI=", amp];
  Print["  ks=", ks];
  Print["  pos=", Select[subsetSums, # > 0 &], " neg=", Select[subsetSums, # < 0 &]];
];

Do[PrintCase[free], {free, {
  {2, 5/2, 3},
  {2, 5/2, -3},
  {2, -5/2, 3},
  {-2, 5/2, 3},
  {1, 2, 5},
  {5, 1, 2},
  {1, -2, 5},
  {-1, 2, 5},
  {3, 4, -10},
  {3, -4, -10},
  {-3, -4, 10}
}}]
