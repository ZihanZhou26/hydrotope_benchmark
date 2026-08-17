(* Compute amplitudes for two-minus sector *)
Get["../OnShellBG.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

(* Test n=4 with symbolic kinematics *)
Print["=== n=4, symbolic ==="];
Block[{n = 4, sigmas, ks, ws, amp, w2, w3},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {w2, w3}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["freeW = {w2, w3} => A4 = ", Simplify[amp]];
];

Print["=== n=4, numeric ==="];
Block[{n = 4, sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {1, 2}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["freeW = {1,2} => A4 = ", Simplify[amp], " = ", N[amp, 20]];
];

Print["=== n=5, numeric ==="];
Block[{n = 5, sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {1, 2, 3}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["freeW = {1,2,3} => A5 = ", Simplify[amp], " = ", N[amp, 20]];
];

Print["=== n=5, different ==="];
Block[{n = 5, sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {2, 3, 5}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["freeW = {2,3,5} => A5 = ", Simplify[amp], " = ", N[amp, 20]];
];

Print["=== n=6, numeric ==="];
Block[{n = 6, sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {1, 2, 3, 4}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["freeW = {1,2,3,4} => A6 = ", Simplify[amp], " = ", N[amp, 20]];
];

Print["=== n=7, numeric ==="];
Block[{n = 7, sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {1, 2, 3, 4, 5}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["freeW = {1,2,3,4,5} => A7 = ", Simplify[amp], " = ", N[amp, 20]];
];
