(* Test the condition: w2 > all plus-sigma w's *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeNumeric[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  amp
];

testFormula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

(* Test various conditions *)
testCases = {
  (* w2 > all plus-sigma w *)
  {5, {5, 1, 2}},
  {5, {4, 1, 2}},
  {5, {6, 2, 3}},
  {5, {10, 1, 3}},
  (* w2 between plus-sigma w *)
  {5, {3, 2, 5}},
  {5, {2, 1, 5}},
  {5, {1, 2, 3}},  (* w2=1, w3=2, w4=3: w2 < all *)
  (* w2 < all plus-sigma w *)
  {5, {1, 3, 4}},
  {5, {2, 3, 5}},
  (* degenerate plus-sigma: w3 = w4 *)
  {5, {2, 1, 1}},
  {5, {3, 1, 1}},
  {5, {4, 1, 1}},
  {5, {1, 2, 2}}
};

Do[
  {n, fw} = tc;
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Continue[]];
  amp = computeNumeric[n, fw];
  pred = testFormula[n, ws];
  
  match = Simplify[amp - pred] === 0;
  
  w2 = fw[[1]];
  cond1 = w2 > Max[fw[[2 ;;]]]; (* w2 > all plus-sigma *)
  cond2 = w2 < Min[fw[[2 ;;]]]; (* w2 < all plus-sigma *)
  
  Print["fw=", fw, " ws=", N[ws, 6], " w2>all=", cond1, " w2<all=", cond2, " match=", match];
  If[!match,
    Print["  actual=", N[amp, 10], " pred=", N[pred, 10], " ratio=", N[amp/pred, 10]]
  ];
  ,
  {tc, testCases}
]
