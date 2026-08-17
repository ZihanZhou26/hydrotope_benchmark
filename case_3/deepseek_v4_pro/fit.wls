(* Numeric-only BG for faster computation *)
Get["BGlib.m"];
gVal = 1.0; (* use float for speed *)

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

(* Faster numeric version - use N on inputs immediately *)
computeNumericFast[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  fwFloat = N[fw];
  {ks, ws} = MakeKinematics[n, fwFloat, sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  {ws, amp}
];

(* Test more points and compute ratios *)
n5cases = {
  {3,5,7}, {2,3,5}, {1,2,3}, {1,3,4}, {2,4,6},
  {1,5,9}, {3,4,5}, {4,5,6}, {2,5,7}, {1,3,5},
  {2,3,7}, {1,4,7}, {3,7,11}, {2,6,10}, {5,7,9}
};

Print["=== n=5 ==="];
Do[
  fw = c;
  {ws, amp} = computeNumericFast[5, fw];
  w1=ws[[1]]; w2=ws[[2]]; w3=ws[[3]]; w4=ws[[4]]; w5=ws[[5]];
  
  AoverI = amp/I;
  
  prodAll = w1*w2*w3*w4*w5;
  prod12 = w1*w2;
  prod345 = w3*w4*w5;
  
  (* Try: A/i = -2 * w1*w2 * sum_{i<j} w_i w_j / something *)
  sumProd = w1*w2 + w1*w3 + w1*w4 + w1*w5 + w2*w3 + w2*w4 + w2*w5 + w3*w4 + w3*w5 + w4*w5;
  
  (* Try: A/i = -2 * (product of all w) / (something simple) *)
  
  Print["fw=", fw];
  Print["  ws=", ws];
  Print["  A/i=", AoverI];
  Print["  prodAll=", prodAll, " A/(i*prod)=", -AoverI/prodAll];
  Print["  w1*w2=", prod12, " A/(i*w1*w2)=", -AoverI/prod12];
  (* Maybe A/i = w1*w2 * something with S and S2 *)
  S = w3+w4;
  S2 = w3^2+w4^2;
  delta = (S^2 - S2)/(2*(w2+S));
  Print["  S=",S," S2=",S2," delta=",delta];
  Print["  w1=", -S+delta, " (check: ", w1, ")"];
  Print["  w5=", -w2-delta, " (check: ", w5, ")"];
  ,
  {c, n5cases}
]
