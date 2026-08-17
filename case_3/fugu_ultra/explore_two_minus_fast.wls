code = Import[FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}], "Text"];
defs = StringSplit[code, "(* ================================================================ *)\n(*  VI. TESTS"][[1]];
ToExpression[defs];
Clear[TwoMinusAmp];
TwoMinusAmp[n_, freeW_] := Module[{sigmas, ks, ws, amp},
  sigmas = Join[{-1,-1}, Table[1, n-2]];
  {ks, ws} = MakeKinematics[n, freeW, sigmas, 1];
  amp = BGAmplitude[ks, ws, 1];
  {ws, ks, FullSimplify[amp], N[amp,30]}
];
Print["TWO MINUS EXPLORATION"];
cases = {{4,{2,3}}, {5,{2,5/2,3}}, {5,{1,3,7}}, {5,{1/10,3,7}}, {6,{3/2,2,5/2,3}}, {6,{1,3,5,7}}, {6,{1/10,3,5,7}}, {7,{3/2,2,5/2,3,7/2}}};
Scan[(n = #[[1]]; fw = #[[2]];
  Print["n=", n, " free=", fw];
  res=TwoMinusAmp[n, fw];
  Print["ws=", res[[1]]];
  Print["amp exact InputForm=", InputForm[res[[3]]]];
  Print["amp N=", res[[4]]];) &, cases]
