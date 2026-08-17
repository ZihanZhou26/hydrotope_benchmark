Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeCase[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  {ws, amp}
];

(* Test formula: A_n = i * 2^{n-1} * w1 * w2^{2n-5} *)
testFormula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

(* Test cases *)
testCases = {
  {5, {1, 2, 3}},
  {5, {2, 3, 5}},
  {5, {3, 5, 7}},
  {5, {1, 3, 4}},
  {5, {2, 4, 6}},
  {5, {1, 5, 9}},
  {5, {2, 1, 1}},
  {5, {3, 1, 1}},
  {5, {4, 5, 6}},
  {6, {1, 2, 3, 4}},
  {6, {2, 3, 5, 7}},
  {6, {1, 3, 5, 7}},
  {7, {1, 2, 3, 4, 5}},
  {7, {2, 3, 5, 7, 11}}
};

Do[
  {n, fw} = tc;
  {ws, amp} = computeCase[n, fw];
  pred = testFormula[n, ws];
  
  Print["n=", n, " fw=", fw];
  Print["  ws=", N[ws, 8]];
  Print["  actual=", N[amp, 16]];
  Print["  predicted=", N[pred, 16]];
  Print["  match=", Simplify[amp - pred] === 0];
  Print["  w1=", ws[[1]], " w2=", ws[[2]]];
  ,
  {tc, testCases}
]
