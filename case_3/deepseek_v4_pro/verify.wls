(* ================================================================ *)
(*  Verification script for A_n = i * 2^{n-1} * w1 * w2^{2n-5}     *)
(*  Two-minus sector, deep water waves                               *)
(* ================================================================ *)

Get["../OnShellBG.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

formula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

testOne[n_, fw_] := Module[{sigmas, ks, ws, amp, pred, match},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Return[{False, 0, 0, 0}]];
  amp = BGAmplitude[ks, ws, gVal];
  pred = formula[n, ws];
  match = FullSimplify[amp - pred] === 0;
  {match, ws[[1]], ws[[2]], amp}
];

Print["========================================"];
Print[" Verification of A_n = i 2^{n-1} w1 w2^{2n-5}"];
Print[" Two-minus sector, deep water waves"];
Print["========================================"];

allPassed = True;
totalCases = 0;

Do[
  Module[{n = tc[[1]], fwList = tc[[2]], passed},
   passed = True;
   Do[
     Module[{res, match, w1, w2, amp},
      res = testOne[n, fw];
      match = res[[1]];
      If[!match, passed = False; allPassed = False];
      totalCases++;
      If[!match, 
        Print["FAIL: n=", n, " fw=", fw, " w1=", N[res[[2]], 6], " w2=", N[res[[3]], 6]];
        Print["  actual=", N[res[[4]], 10], " predicted=", N[formula[n, {res[[2]], res[[3]]}], 10]];
      ];
     ],
     {fw, fwList}
   ];
   Print["n=", n, ": ", If[passed, "PASS", "FAIL"], 
         " (", Length[fwList], " cases)"];
  ],
  {tc, {
    {5, {{1,2,3},{1,3,4},{1,4,5},{1,5,6},{1,2,4},{1,3,5},{1,5,7},
         {2,3,4},{2,3,5},{2,4,5},{2,4,6},{2,5,7},
         {3,4,5},{3,5,6},{3,5,7},{3,6,9},{4,5,6}}},
    {6, {{1,2,3,4},{1,2,3,5},{1,3,4,5},{1,3,5,7},
         {2,3,4,5},{2,3,5,7},{2,4,5,6},{2,5,7,9},
         {3,4,5,6},{3,5,7,9},{3,7,8,9},{1,4,5,7}}},
    {7, {{1,2,3,4,5},{1,3,4,5,6},{2,3,4,5,6},
         {2,3,5,7,9},{3,4,5,6,7},{1,4,5,7,9},{2,5,7,9,11}}},
    {8, {{1,2,3,4,5,6}}}
  }}
];

Print["\nTotal cases: ", totalCases, "  All passed: ", allPassed];

(* Non-generic: large freq *)
Print["\n--- Non-generic: large frequency ---"];
{ks, ws} = MakeKinematics[5, {1, 2, 100}, twoMinusSigma[5], gVal];
amp = BGAmplitude[ks, ws, gVal];
pred = formula[5, ws];
Print["n=5 fw={1,2,100}: match=", FullSimplify[amp-pred]===0];

(* Non-generic: very small w2 *)
{ks, ws} = MakeKinematics[5, {1/10, 2, 3}, twoMinusSigma[5], gVal];
amp = BGAmplitude[ks, ws, gVal];
pred = formula[5, ws];
Print["n=5 fw={1/10,2,3}: match=", FullSimplify[amp-pred]===0];

Print["\nDone."];
