(* Comprehensive verification of formula A_n = i * 2^{n-1} * w1 * w2^{2n-5} *)
(* for the two-minus sector when w2 < all plus-sigma free frequencies *)

Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

formula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

testNSingle[n_, fw_] := Module[{sigmas, ks, ws, amp, pred, match},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Return[{"FAIL_MK", fw, 0, 0}]];
  amp = BGAmplitude[ks, ws, gVal];
  pred = formula[n, ws];
  match = FullSimplify[amp - pred] === 0;
  {match, ws, amp, pred}
];

Print["=== n=5 ==="];
allPass5 = True;
allCases5 = {{1,2,3},{1,3,4},{1,4,5},{1,5,6},{1,2,4},{1,3,5},{1,5,7},
  {2,3,4},{2,3,5},{2,4,5},{2,4,6},{2,5,7},{3,4,5},{3,5,6},{3,5,7},{3,6,9},{4,5,6}};
Do[
  {match, ws, amp, pred} = testNSingle[5, fw];
  If[match === "FAIL_MK", Continue[]];
  If[!match, allPass5 = False; Print["FAIL: fw=", fw]];
  ,
  {fw, allCases5}
];
Print["All n=5 (", Length[allCases5], " cases): ", If[allPass5, "PASS", "FAIL"]];

Print["\n=== n=6 ==="];
allPass6 = True;
allCases6 = {{1,2,3,4},{1,2,3,5},{1,3,4,5},{1,3,5,7},{2,3,4,5},{2,3,5,7},
  {2,4,5,6},{2,5,7,9},{3,4,5,6},{3,5,7,9},{3,7,8,9},{1,4,5,7}};
Do[
  {match, ws, amp, pred} = testNSingle[6, fw];
  If[match === "FAIL_MK", Continue[]];
  If[!match, allPass6 = False; Print["FAIL: fw=", fw]];
  ,
  {fw, allCases6}
];
Print["All n=6 (", Length[allCases6], " cases): ", If[allPass6, "PASS", "FAIL"]];

Print["\n=== n=7 ==="];
allPass7 = True;
allCases7 = {{1,2,3,4,5},{1,3,4,5,6},{2,3,4,5,6},{2,3,5,7,9},{3,4,5,6,7},
  {1,4,5,7,9},{2,5,7,9,11}};
Do[
  {match, ws, amp, pred} = testNSingle[7, fw];
  If[match === "FAIL_MK", Continue[]];
  If[!match, allPass7 = False; Print["FAIL: fw=", fw]];
  ,
  {fw, allCases7}
];
Print["All n=7 (", Length[allCases7], " cases): ", If[allPass7, "PASS", "FAIL"]];

(* Non-generic: one freq much larger *)
Print["\n=== Non-generic (large freq) ==="];
ngTests = {
  {5, {1, 2, 100}},
  {5, {1, 3, 200}},
  {6, {1, 2, 3, 50}}
};
Do[
  {match, ws, amp, pred} = testNSingle[ng[[1]], ng[[2 ;;]]];
  If[match === "FAIL_MK", Continue[]];
  Print["n=", ng[[1]], " fw=", ng[[2 ;;]], " match=", match];
  If[!match, Print["  actual=", N[amp, 10], " pred=", N[pred, 10]]];
  ,
  {ng, ngTests}
];

(* Non-generic: one freq much smaller (w2 very small) *)
Print["\n=== Non-generic (small w2) ==="];
sgTests = {{{5, 1/10, 2, 3}}, {{5, 1/100, 2, 3}}};
Do[
  fw = sg;
  {match, ws, amp, pred} = testNSingle[Length[fw]+2, fw];
  If[match === "FAIL_MK", Print["MK failed for ", fw]; Continue[]];
  Print["fw=", fw, " match=", match];
  If[!match, Print["  actual=", N[amp, 10], " pred=", N[pred, 10]]];
  ,
  {sg, sgTests}
];
