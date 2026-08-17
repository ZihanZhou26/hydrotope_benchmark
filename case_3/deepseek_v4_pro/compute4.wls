Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeA[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  fwRational = Map[Rationalize, fw];
  {ks, ws} = MakeKinematics[n, fwRational, sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  {ws, amp}
];

(* Compute more test cases and try to find formula *)
(* For each case, compute ws, A, and various products *)

testCasesN5 = {
  {1, 2, 3}, {1, 2, 4}, {1, 3, 4}, {2, 3, 4},
  {2, 3, 5}, {3, 5, 7}, {2, 4, 6}, {1, 5, 9},
  {3, 4, 5}, {4, 5, 6}, {1, 3, 5}, {2, 4, 8},
  {1, 4, 5}, {2, 5, 7}, {3, 6, 9}
};

Do[
  {ws, amp} = computeA[5, fw];
  prodAll = Product[ws[[i]], {i, 1, 5}];
  prod12 = ws[[1]]*ws[[2]];
  prod345 = ws[[3]]*ws[[4]]*ws[[5]];
  ampByProd = amp / prodAll;
  Print["fw=", fw, " ws=", N[ws, 10], " A=", N[amp, 10], 
        " prod=", N[prodAll, 10], " A/prod=", N[ampByProd, 10]];
  ,
  {fw, testCasesN5}
]
