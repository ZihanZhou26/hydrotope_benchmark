Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeNumeric[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  fwRat = Map[Rationalize, fw];
  {ks, ws} = MakeKinematics[n, fwRat, sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  amp/I (* strip the I factor - all amps are pure imaginary *)
];

(* Generate test points *)
n5cases = {
  {1,2,3}, {2,1,3}, {3,2,1},
  {1,3,4}, {2,3,5}, {3,4,5}, {3,5,7},
  {1,4,5}, {2,4,6}, {3,5,8}, {2,5,7},
  {1,5,9}, {4,5,6}, {5,7,11}, {2,6,10}
};

Print["=== n=5 test ==="];
Do[
  fw = c;
  ampOverI = computeNumeric[5, fw];
  {ks, ws} = MakeKinematics[5, Map[Rationalize, fw], twoMinusSigma[5], gVal];
  
  (* Print ws and amp for analysis *)
  Print["fw=", fw, " ws=", N[ws, 8]];
  Print["  A/i = ", N[ampOverI, 16]];
  
  (* Try different candidate formulas *)
  prodAll = Product[ws[[i]], {i,1,5}];
  prod12 = ws[[1]]*ws[[2]];
  prodPos = Product[ws[[i]], {i,3,5}];
  prodNeg = ws[[1]]*ws[[2]];
  
  w1 = ws[[1]]; w2 = ws[[2]]; w3 = ws[[3]]; w4 = ws[[4]]; w5 = ws[[5]];
  
  (* Try: A/i = (w1 w2)^2 * something *)
  r1 = ampOverI / (w1^2 * w2^2);
  (* Try: A/i = w1 w2 * product of all w *)
  r2 = ampOverI / (w1 * w2 * w3 * w4 * w5);
  (* Try: A/i = (w1 w2) * (sum over something) *)
  r3 = ampOverI / (w1 * w2);
  (* Try: A/i related to w1+w2 or similar *)
  
  Print["  A/(i w1 w2) = ", N[r3, 12]];
  Print["  A/(i prod) = ", N[r2, 12]];
  ,
  {c, n5cases}
]
