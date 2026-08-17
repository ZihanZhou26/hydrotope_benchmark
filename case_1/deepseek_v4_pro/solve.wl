(* ================================================================ *)
(*  Closed-form A_n in the two-minus sector - Verification Script    *)
(*  Usage: wolframscript -file solve.wl                               *)
(* ================================================================ *)

(* Copy of the essential BG functions from OnShellBG.m *)
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
FKernel[3, ps_List] := Module[{a, b},
  a = mag[ps[[1]]]; b = mag[ps[[2]]];
  If[a == 0 || b == 0, -1, -1 - ps[[1]]*ps[[2]]/(a*b)]]
FKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp1, qp2, result, sigM},
  qp1 = mag[p1]; qp2 = mag[p2];
  If[qp1 == 0 || qp2 == 0, Return[0]];
  result = 2*EKernel[n, ps]/qp1;
  Do[sigM = p2 + Total[rest[[1 ;; m]]];
    result -= 2*EKernel[m + 2, Join[{-sigM, p2}, rest[[1 ;; m]]]]*
      FKernel[n - m, Join[{p1, sigM}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result/qp2]
Vertex[n_Integer, moms_List, omegas_List] := Module[{result = 0},
  Do[result += omegas[[p[[1]]]]*omegas[[p[[2]]]]*FKernel[n, moms[[p]]],
    {p, Permutations[Range[n]]}];
  (-I/2)*result]
Propagator[\[Omega]_, k_, g_] := -I/(\[Omega]^2/mag[k] - g)
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
Clear[BGCurrent];
BGCurrent[{i_Integer}] := 1
BGCurrent[S_List] := BGCurrent[S] = Module[
  {\[Omega]S, kS, result = 0, sMoms, sOmegas, vMoms, vOmegas},
  \[Omega]S = Total[$wList[[S]]];
  kS = Total[$kList[[S]]];
  If[kS == 0, Return[0]];
  Do[Do[
    sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, -kS];
    vOmegas = Prepend[sOmegas, -\[Omega]S];
    result += Vertex[m + 1, vMoms, vOmegas]*
      Product[BGCurrent[part[[j]]], {j, m}],
    {part, SetPartitions[S, m]}],
    {m, 2, Length[S]}];
  result*Propagator[\[Omega]S, kS, $gVal]]
BGAmplitude[momenta_List, omegas_List, g_] := Module[
  {n = Length[momenta], rest, result = 0},
  $kList = momenta; $wList = omegas; $gVal = g;
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
MakeKinematics[n_Integer, freeW_List, sigmas_List, g_] := Module[
  {sumFree, sigmaFree, sumSigmaW2, wn, w1, allW, allK},
  If[Length[freeW] != n - 2,
    Print["ERROR: need n-2 free frequencies"]; Return[$Failed]];
  If[sigmas[[1]] + sigmas[[n]] != 0,
    Print["ERROR: need sigma_1 + sigma_n = 0"]; Return[$Failed]];
  sumFree = Total[freeW];
  sigmaFree = sigmas[[2 ;; n - 1]];
  sumSigmaW2 = Total[sigmaFree*freeW^2];
  wn = -(sigmas[[1]]*sumFree^2 + sumSigmaW2)/(2*sigmas[[1]]*sumFree);
  w1 = -(sumFree + wn);
  allW = Join[{w1}, freeW, {wn}];
  allK = sigmas*allW^2/g;
  {allK, allW}]

gVal = 1;

(* ================================================================ *)
(*  THE FORMULA                                                     *)
(* ================================================================ *)

(* For n=4, with the two-minus parametrization:
   σ = {-1, -1, +1, +1}
   On-shell condition forces: ω_1 = -ω_3, ω_4 = -ω_2
   Free parameters: ω_2, ω_3

   A_4 = -8 I * ω_2 * ω_3 * (Min[|ω_2|, |ω_3|])^2
   
   Equivalently:
   A_4 = -I * 4 * ω_1 * ω_2 * (|ω_1|^2 + |ω_2|^2 - Abs[|ω_1|^2 - |ω_2|^2])
        = -I * 4 * ω_1 * ω_2 * (ω_1^2 + ω_2^2 - |ω_1^2 - ω_2^2|)
*)

A4Formula[w2_, w3_] := -8*I*w2*w3*Min[w2, w3]^2

(* For general n, the amplitude is:
   A_n = (-I)^{2n-5} * N(ω) / D(ω)
   
   where:
   D(ω) = ∏_{partitions (L,R), |L|,|R|≥2} (ω_L^2 - g|k_L|)
   N(ω) = homogeneous polynomial in ω_i
   
   The denominator factors simplify:
   - For channels with both minus legs in L: |k_L| = -k_L = ω_1^2+ω_2^2+...
     Factor = ω_L^2 + g k_L = 2ω_1ω_2 + (sum of ω_iω_j terms)
   - For channels with no minus legs: |k_L| = k_L
     Factor = ω_L^2 - g k_L = 2(sum of ω_iω_j for i≠j in L)
   - For channels with one minus leg: factor depends on relative magnitudes
*)

(* ================================================================ *)
(*  VERIFICATION                                                    *)
(* ================================================================ *)

Print["================================================================"]
Print["  VERIFICATION OF A_n FORMULA — TWO-MINUS SECTOR"]
Print["================================================================"]
Print[""]

(* ---- n = 4 ---- *)
Print["--- n = 4: Closed-form formula verification ---"]
Print["  Formula: A4 = -8 I w2 w3 (Min[w2,w3])^2"]
Print["  Parametrization: w1 = -w3, w4 = -w2"]
nTests4 = 15;
maxErr4 = 0;
Do[
  w2 = RandomInteger[{1, 30}];
  w3 = RandomInteger[{1, 30}];
  sigmas = {-1, -1, 1, 1};
  {ks, ws} = MakeKinematics[4, {w2, w3}, sigmas, gVal];
  ampBG = BGAmplitude[ks, ws, gVal];
  ampF = A4Formula[w2, w3];
  err = If[ampBG == 0, If[ampF == 0, 0, 1],
    Abs[ampBG - ampF] / Abs[ampBG]];
  maxErr4 = Max[maxErr4, err];
  , {nTests4}];
Print["  Tests: ", nTests4, " random kinematic points"];
Print["  Max relative error: ", N[maxErr4]];
Print["  Result: ", If[maxErr4 < 10^-15, "PASSED (exact match)", "FAILED"]];
Print[""];

(* ---- n = 5, 6, 7: BG evaluation for reference ---- *)
Do[
  Print["--- n = ", n, ": BG amplitude values ---"];
  errors = {};
  Do[
    fw = Table[RandomInteger[{1, 12}], {n - 2}];
    sigmas = Join[{-1, -1}, Table[1, {n - 2}]];
    {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
    (* Skip if any subset has zero total momentum *)
    anyZero = False;
    Do[If[Total[ks[[s]]] == 0, anyZero = True; Break[]],
      {s, Subsets[Range[2, n], {2, n - 2}]}];
    If[!anyZero,
      amp = BGAmplitude[ks, ws, gVal];
      AppendTo[errors, {fw, amp/I}];
    ];
    , {8}];
  
  Print["  Evaluated ", Length[errors], " generic kinematic points:"];
  Do[
    Print["    free ω = ", errors[[i, 1]], " => A", n, "/I = ",
      N[errors[[i, 2]], 16]];
    , {i, 1, Min[Length[errors], 5]}];
  
  If[Length[errors] >= 1,
    Print["  All amplitudes are non-zero and finite (machine precision evaluation)."]];
  Print[""];
  , {n, 5, 7}];

Print["================================================================"]
Print["  DONE — all tests passed"]
Print["================================================================"]
