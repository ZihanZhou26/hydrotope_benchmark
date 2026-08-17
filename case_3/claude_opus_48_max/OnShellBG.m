(* ================================================================ *)
(*  OnShellBG.m                                                     *)
(*  Self-contained Berends-Giele recursion for 1D water waves       *)
(*  evaluated on the resonant manifold (energy + momentum cons).    *)
(*                                                                  *)
(*  Usage: wolframscript -file OnShellBG.m                          *)
(*  All arithmetic is exact (rational), so results are rigorous.    *)
(* ================================================================ *)


(* ================================================================ *)
(*  I. INTERACTION KERNELS (exact)                                  *)
(* ================================================================ *)

mag[k_] := Abs[k]

EKernel[3, ps_List] := -1/2 (mag[ps[[1]]]*mag[ps[[2]]] + ps[[1]]*ps[[2]])

EKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp2, result},
  qp2 = mag[p2];
  result = qp2^(n - 3)*EKernel[3, {p1, p2, Total[rest]}]/(n - 2)!;
  Do[result -= qp2^m/m!*
    EKernel[n - m, Join[{p1, p2 + Total[rest[[1 ;; m]]]}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result]

FKernel[3, ps_List] := -1 - ps[[1]]*ps[[2]]/(mag[ps[[1]]]*mag[ps[[2]]])

FKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp1, qp2, result, sigM},
  qp1 = mag[p1]; qp2 = mag[p2];
  result = 2*EKernel[n, ps]/qp1;
  Do[sigM = p2 + Total[rest[[1 ;; m]]];
    result -= 2*EKernel[m + 2, Join[{-sigM, p2}, rest[[1 ;; m]]]]*
      FKernel[n - m, Join[{p1, sigM}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result/qp2]


(* ================================================================ *)
(*  II. VERTEX AND PROPAGATOR                                       *)
(* ================================================================ *)

Vertex[n_Integer, moms_List, omegas_List] := Module[{result = 0},
  Do[result += omegas[[p[[1]]]]*omegas[[p[[2]]]]*FKernel[n, moms[[p]]],
    {p, Permutations[Range[n]]}];
  (-I/2)*result]

(* No regularization: exact arithmetic, no poles in this sector *)
Propagator[\[Omega]_, k_, g_] := -I/(\[Omega]^2/mag[k] - g)


(* ================================================================ *)
(*  III. SET PARTITIONS (for BG recursion)                          *)
(* ================================================================ *)

SetPartitions[S_List, 1] := {{S}}
SetPartitions[S_List, k_Integer] /; k > Length[S] := {}
SetPartitions[S_List, k_Integer] := Module[{mn = Min[S], result = {}},
  Do[Module[{fp = Join[{mn}, sub], rem, sps},
    rem = Complement[S, fp];
    If[Length[rem] >= k - 1,
      sps = SetPartitions[rem, k - 1];
      Do[AppendTo[result, Join[{fp}, sp]], {sp, sps}]]],
    {sub, Subsets[Complement[S, {mn}], {0, Length[S] - k}]}];
  result]


(* ================================================================ *)
(*  IV. BERENDS-GIELE RECURSION                                     *)
(* ================================================================ *)

Clear[BGCurrent];
BGCurrent[{i_Integer}] := 1

BGCurrent[S_List] := BGCurrent[S] = Module[
  {\[Omega]S, kS, result = 0},
  \[Omega]S = Total[$wList[[S]]];
  kS = Total[$kList[[S]]];
  Do[Do[Module[{sMoms, sOmegas, vMoms, vOmegas},
    sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, -kS];
    vOmegas = Prepend[sOmegas, -\[Omega]S];
    result += Vertex[m + 1, vMoms, vOmegas]*
      Product[BGCurrent[part[[j]]], {j, m}]],
    {part, SetPartitions[S, m]}],
    {m, 2, Length[S]}];
  result*Propagator[\[Omega]S, kS, $gVal]]

BGAmplitude[momenta_List, omegas_List, g_] := Module[
  {n = Length[momenta], rest, result = 0},
  $kList = momenta; $wList = omegas; $gVal = g;
  (* Clear memoized currents *)
  DownValues[BGCurrent] =
    Select[DownValues[BGCurrent], !FreeQ[#, Pattern | Blank] &];
  rest = Range[2, n];
  Do[Do[Module[{sMoms, sOmegas, vMoms, vOmegas},
    sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, $kList[[1]]];
    vOmegas = Prepend[sOmegas, $wList[[1]]];
    result += Vertex[m + 1, vMoms, vOmegas]*
      Product[BGCurrent[part[[j]]], {j, m}]],
    {part, SetPartitions[rest, m]}],
    {m, 2, n - 1}];
  result]


(* ================================================================ *)
(*  V. KINEMATIC SOLVER                                             *)
(* ================================================================ *)

(*  Given:  n, free frequencies {w2,...,w_{n-1}}, sign vector sigma, g
    Returns: {momenta, signedOmegas}
    Requires sigma_1 + sigma_n = 0 for a linear solution.

    Energy conservation:   w1 + w2 + ... + wn = 0
    Momentum conservation: sigma_1*w1^2 + ... + sigma_n*wn^2 = 0

    Substituting w1 = -(w2+...+wn) into momentum conservation
    and using sigma_1 + sigma_n = 0 to cancel the wn^2 term gives
    a linear equation for wn.                                        *)

MakeKinematics[n_Integer, freeW_List, sigmas_List, g_] := Module[
  {sumFree, sigmaFree, sumSigmaW2, wn, w1, allW, allK},

  If[Length[freeW] != n - 2,
    Print["ERROR: need n-2 free frequencies"]; Return[$Failed]];
  If[sigmas[[1]] + sigmas[[n]] != 0,
    Print["ERROR: need sigma_1 + sigma_n = 0"]; Return[$Failed]];

  sumFree = Total[freeW];  (* w2 + ... + w_{n-1} *)
  sigmaFree = sigmas[[2 ;; n - 1]];
  sumSigmaW2 = Total[sigmaFree*freeW^2];  (* sum sigma_i*wi^2, i=2..n-1 *)

  (* From momentum conservation (linear in wn): *)
  wn = -(sigmas[[1]]*sumFree^2 + sumSigmaW2)/(2*sigmas[[1]]*sumFree);
  w1 = -(sumFree + wn);

  allW = Join[{w1}, freeW, {wn}];
  allK = sigmas*allW^2/g;
  {allK, allW}]


(* ================================================================ *)
(*  VI. TESTS                                                       *)
(* ================================================================ *)

gVal = 1;

Print["================================================================"]
Print["  On-Shell BG: Vanishing of A_n for sigma = {-1,+1,...,+1}"]
Print["  (exact rational arithmetic, no floating point)"]
Print["================================================================\n"]

(* --- Test each n --- *)
testCases = {
  {5, {3/2, 2, 5/2}},
  {6, {3/2, 2, 5/2, 3}},
  {7, {3/2, 2, 5/2, 3, 7/2}},
  {8, {1, 2, 3, 4, 5, 6}}
};

Do[
  Block[{n, freeW, sigmas, ks, ws, amp, elapsed},
  n = tc[[1]]; freeW = tc[[2]];
  sigmas = Join[{-1}, Table[1, n - 1]];
  {ks, ws} = MakeKinematics[n, freeW, sigmas, gVal];

  Print["--- n = ", n, " ---"];
  Print["  sigma  = ", sigmas];
  Print["  free w = ", freeW];
  Print["  all w  = ", ws];
  Print["  all k  = ", ks];
  Print["  sum w  = ", Total[ws], "  sum k = ", Total[ks]];

  elapsed = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal]][[1]];

  Print["  A_", n, " = ", Simplify[amp]];
  Print["  Time: ", Round[elapsed, 0.1], " sec\n"];
  ],
  {tc, testCases}
]

(* --- Additional 6-point with different kinematics --- *)
Print["--- n = 6, different kinematics ---"];
Do[Block[{sigmas, ks, ws, amp},
  sigmas = {-1, 1, 1, 1, 1, 1};
  {ks, ws} = MakeKinematics[6, fw, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["  free w = ", fw, " => A6 = ", Simplify[amp]];
  ],
  {fw, {{1, 3, 5, 7}, {2, 3, 7, 11}}}
]
Print[];

(* --- Flipped signs: sigma = {+1,-1,...,-1} --- *)
Print["--- n = 6, sigma = {+1,-1,-1,-1,-1,-1} ---"];
Block[{sigmas, ks, ws, amp},
  sigmas = {1, -1, -1, -1, -1, -1};
  {ks, ws} = MakeKinematics[6, {3/2, 2, 5/2, 3}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["  A6 = ", Simplify[amp], "\n"];
]

(* --- Nonzero comparison: sigma = {-1,-1,+1,+1,+1} at 5-point --- *)
Print["--- n = 5, sigma = {-1,-1,+1,+1,+1} (should be NONZERO) ---"];
Block[{sigmas, ks, ws, amp},
  sigmas = {-1, -1, 1, 1, 1};
  {ks, ws} = MakeKinematics[5, {2, 5/2, 3}, sigmas, gVal];
  Print["  sigma = ", sigmas];
  Print["  all w = ", ws];
  Print["  all k = ", ks];
  Print["  sum w = ", Total[ws], "  sum k = ", Total[ks]];
  amp = BGAmplitude[ks, ws, gVal];
  Print["  A5 = ", N[amp, 20]];
  Print["  |A5| = ", N[Abs[amp], 20]];
  Print["  (nonzero confirms the code is computing nontrivially)\n"];
]

Print["================================================================"]
Print["  Done."]
Print["================================================================"]
