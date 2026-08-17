(* Test condition: |w2| < all other |w_i| for formula to hold *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

formula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

testCase[n_, fw_] := Module[{sigmas, ks, ws, amp, pred, match, cond},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Return[None]];
  amp = BGAmplitude[ks, ws, gVal];
  pred = formula[n, ws];
  match = FullSimplify[amp - pred] === 0;
  cond = AllTrue[ws[[3 ;;]], Abs[#] > Abs[ws[[2]]] &];
  Print["fw=", fw, " ws=", N[ws, 6]];
  Print["  |w2|=", Abs[ws[[2]]], " min(|w_rest|)=", N[Min[Abs[ws[[3 ;;]]]], 6],
        " cond=", cond, " match=", match];
  If[!match, Print["  actual=", N[amp, 10], " pred=", N[pred, 10]]];
  {cond, match}
];

Print["=== n=5 ==="];
testCase[5, {1, 2, 3}];
testCase[5, {2, 3, 5}];
testCase[5, {-1, 2, 3}];
testCase[5, {-1, 3, 5}];
testCase[5, {-2, 3, 4}];
testCase[5, {2, 1, 3}];
testCase[5, {2, 1, 1}];
testCase[5, {3, 1, 1}];
testCase[5, {3, 1, 2}];
testCase[5, {4, 1, 1}];
