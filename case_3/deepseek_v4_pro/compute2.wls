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

(* Test various n with different kinematics *)
testCases = {
  {4, {2, 3}},
  {4, {3, 5}},
  {4, {1, 3}},
  {5, {1, 2, 3}},
  {5, {2, 3, 5}},
  {5, {3, 5, 7}},
  {6, {1, 2, 3, 4}},
  {6, {2, 3, 5, 7}},
  {7, {1, 2, 3, 4, 5}},
  {7, {2, 3, 5, 7, 11}}
};

Do[
  {n, fw} = tc;
  Print["n=", n, " freeW=", fw];
  amp = computeA[n, fw];
  Print["  A", n, " = ", N[amp, 30]];
  Print["  simplified = ", Simplify[amp]];
  ,
  {tc, testCases}
]
