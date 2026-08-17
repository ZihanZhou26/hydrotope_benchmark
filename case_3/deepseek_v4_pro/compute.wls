Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeA[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Rationalize[fw], sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  amp
];

(* Test various n *)
Do[
  Print["=== n=", n, " ==="];
  fw = Range[n-2];
  Print["  freeW = ", fw];
  amp = computeA[n, fw];
  Print["  A", n, " = ", N[amp, 30]];
  Print["  A", n, " simplified = ", Simplify[amp]];
  ,
  {n, 4, 7}
]
