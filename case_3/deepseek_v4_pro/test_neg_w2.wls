(* Test formula with negative w2 *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

formula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

computeAndCheck[n_, fw_] := Module[{sigmas, ks, ws, amp, pred, match},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Return[{"FAIL_MK"}]];
  amp = BGAmplitude[ks, ws, gVal];
  pred = formula[n, ws];
  match = FullSimplify[amp - pred] === 0;
  Print["fw=", fw, " ws=", N[ws, 6], " match=", match];
  If[!match, Print["  actual=", N[amp, 10], " pred=", N[pred, 10]]];
];

(* Test with negative w2 *)
computeAndCheck[5, {-1, 2, 3}];
computeAndCheck[5, {-2, 3, 4}];
computeAndCheck[5, {-1, 3, 5}];
computeAndCheck[6, {-1, 2, 3, 4}];
computeAndCheck[6, {-2, 3, 4, 5}];
