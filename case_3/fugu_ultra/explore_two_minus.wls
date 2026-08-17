Get[FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}]];
Clear[TwoMinusAmp];
TwoMinusAmp[n_, freeW_] := Module[{sigmas, ks, ws, amp},
  sigmas = Join[{-1,-1}, Table[1, n-2]];
  {ks, ws} = MakeKinematics[n, freeW, sigmas, 1];
  amp = BGAmplitude[ks, ws, 1];
  {ws, ks, FullSimplify[amp], N[amp,20]}
];
Print["TWO MINUS EXPLORATION"];
Do[
  Print["n=", n, " free=", fw];
  res=TwoMinusAmp[n, fw];
  Print["ws=", res[[1]]];
  Print["ks=", res[[2]]];
  Print["amp exact=", InputForm[res[[3]]]];
  Print["amp N=", res[[4]]];
, { {n, fw}, {{4,{2,3}}, {5,{2,5/2,3}}, {5,{1,3,7}}, {6,{3/2,2,5/2,3}}, {6,{1,3,5,7}}, {7,{3/2,2,5/2,3,7/2}}} }]
