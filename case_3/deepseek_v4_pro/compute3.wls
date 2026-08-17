Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeA[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  fwRational = Map[Rationalize, fw];
  {ks, ws} = MakeKinematics[n, fwRational, sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  amp
];

(* More test cases *)
testCases = {
  {5, {1, 2, 4}},
  {5, {1, 3, 4}},
  {5, {2, 4, 6}},
  {5, {1, 5, 9}},
  {5, {3, 4, 5}},
  {5, {4, 5, 6}},
  {6, {1, 2, 3, 5}},
  {6, {1, 3, 5, 7}},
  {6, {2, 4, 6, 8}},
  {6, {3, 4, 5, 6}}
};

Do[
  {n, fw} = tc;
  amp = computeA[n, fw];
  Print["n=", n, " fw=", fw, " A=", N[amp, 20], " simp=", Simplify[amp]];
  ,
  {tc, testCases}
]

(* Try symbolic n=5 *)
Print["\n=== Symbolic n=5 ==="];
Block[{n = 5, sigmas, ks, ws, amp, w2, w3, w4},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, {w2, w3, w4}, sigmas, gVal];
  Print["ws = ", ws];
  Print["ks = ", ks];
  amp = BGAmplitude[ks, ws, gVal];
  Print["A5 = ", Simplify[amp]];
  Print["A5 factorized = ", Factor[amp]];
];
