(* Fast fully-numeric BG for two-minus sector *)
(* Uses float arithmetic throughout - much faster *)

magK[k_] := N[Abs[k]];

EKernelN[3, ps_List] := Module[{},
  -0.5*(magK[ps[[1]]]*magK[ps[[2]]] + ps[[1]]*ps[[2]])
];

EKernelN[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp2, result},
  qp2 = magK[p2];
  result = qp2^(n - 3)*EKernelN[3, {p1, p2, Total[rest]}]/(n - 2)!;
  Do[result -= qp2^m/m!*
    EKernelN[n - m, Join[{p1, p2 + Total[rest[[1 ;; m]]]}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result
];

FKernelN[3, ps_List] := -1 - ps[[1]]*ps[[2]]/(magK[ps[[1]]]*magK[ps[[2]]]);

FKernelN[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp1, qp2, result, sigM},
  qp1 = magK[p1]; qp2 = magK[p2];
  result = 2*EKernelN[n, ps]/qp1;
  Do[sigM = p2 + Total[rest[[1 ;; m]]];
    result -= 2*EKernelN[m + 2, Join[{-sigM, p2}, rest[[1 ;; m]]]]*
      FKernelN[n - m, Join[{p1, sigM}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result/qp2
];

VertexN[n_Integer, moms_List, omegas_List] := Module[{result = 0},
  Do[result += omegas[[p[[1]]]]*omegas[[p[[2]]]]*FKernelN[n, moms[[p]]],
    {p, Permutations[Range[n]]}];
  (-I/2)*result
];

PropagatorN[omega_, k_, g_] := -I/(omega^2/magK[k] - g);

SetPartitions[S_List, 1] := {{S}}
SetPartitions[S_List, k_Integer] /; k > Length[S] := {}
SetPartitions[S_List, k_Integer] := Module[{mn = Min[S], result = {}},
  Do[Module[{fp = Join[{mn}, sub], rem, sps},
    rem = Complement[S, fp];
    If[Length[rem] >= k - 1,
      sps = SetPartitions[rem, k - 1];
      Do[AppendTo[result, Join[{fp}, sp]], {sp, sps}]]],
    {sub, Subsets[Complement[S, {mn}], {0, Length[S] - k}]}];
  result
];

$kListN = {}; $wListN = {}; $gValN = 1;

Clear[BGCurrentN];
BGCurrentN[{i_Integer}] := 1

BGCurrentN[S_List] := BGCurrentN[S] = Module[
  {omegaS, kS, resultN = 0},
  omegaS = Total[$wListN[[S]]];
  kS = Total[$kListN[[S]]];
  Do[Do[Module[{sMoms, sOmegas, vMoms, vOmegas},
    sMoms = Table[Total[$kListN[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wListN[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, -kS];
    vOmegas = Prepend[sOmegas, -omegaS];
    resultN += VertexN[m + 1, vMoms, vOmegas]*
      Product[BGCurrentN[part[[j]]], {j, m}]],
    {part, SetPartitions[S, m]}],
    {m, 2, Length[S]}];
  resultN*PropagatorN[omegaS, kS, $gValN]
]

BGAmplitudeN[momenta_List, omegas_List, g_] := Module[
  {n = Length[momenta], rest, resultN = 0},
  $kListN = momenta; $wListN = omegas; $gValN = g;
  DownValues[BGCurrentN] = Select[DownValues[BGCurrentN], !FreeQ[#, Pattern | Blank] &];
  rest = Range[2, n];
  Do[Do[Module[{sMoms, sOmegas, vMoms, vOmegas},
    sMoms = Table[Total[$kListN[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wListN[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, $kListN[[1]]];
    vOmegas = Prepend[sOmegas, $wListN[[1]]];
    resultN += VertexN[m + 1, vMoms, vOmegas]*
      Product[BGCurrentN[part[[j]]], {j, m}]],
    {part, SetPartitions[rest, m]}],
    {m, 2, n - 1}];
  resultN
];

(* Two-minus sigma *)
twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

(* Kinematics solver (numeric) *)
MakeKinematicsN[n_Integer, freeW_List, sigmas_List, g_] := Module[
  {sumFree, sigmaFree, sumSigmaW2, wn, w1, allW, allK},
  sumFree = Total[freeW];
  sigmaFree = sigmas[[2 ;; n - 1]];
  sumSigmaW2 = Total[sigmaFree*freeW^2];
  wn = -(sigmas[[1]]*sumFree^2 + sumSigmaW2)/(2*sigmas[[1]]*sumFree);
  w1 = -(sumFree + wn);
  allW = Join[{w1}, freeW, {wn}];
  allK = sigmas*allW^2/g;
  {allK, allW}
];

computeN[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematicsN[n, fw, sigmas, 1.0];
  amp = BGAmplitudeN[ks, ws, 1.0];
  {ws, amp}
];

(* Test formula: A_n = i * 2^{n-1} * w1 * w2^{2n-5} *)
(* This works when w2 < all plus-sigma w's *)
testFormula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

(* Comprehensive test *)
Print["Testing formula A_n = i * 2^{n-1} * w1 * w2^{2n-5}"];
Print["(Expected to work when w2 < all plus-sigma free w's)"];

allCases = {};
Do[
  Do[
    fw = N[{w2, w3, w4}];
    {ws, amp} = computeN[5, fw];
    pred = testFormula[5, ws];
    diff = Abs[amp - pred] / Max[Abs[amp], Abs[pred]];
    cond = (w2 < w3) && (w2 < w4);
    AppendTo[allCases, {fw, cond, diff < 10^-10}];
    If[!cond || diff > 10^-10,
      Print[If[cond, "MATCH_FAIL: ", "OTHER: "], "fw=", fw, " w2<all=", cond, 
            " diff=", N[diff, 3]]];
    ];
    ,
    {w2, 1, 8},
    {w3, 1, 8},
    {w4, 1, 8}
  ];
];

Print["Total cases: ", Length[allCases]];
Print["w2 < all and match: ", Count[allCases, {{_,_,_}, True, True}]];
Print["w2 < all but fail: ", Count[allCases, {{_,_,_}, True, False}]];
Print["w2 >= some and match: ", Count[allCases, {{_,_,_}, False, True}]];
Print["w2 >= some and fail: ", Count[allCases, {{_,_,_}, False, False}]];
