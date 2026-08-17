(* Numeric exploration of A_n in two-minus sector *)

(* Copy essential functions *)
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
  DownValues[BGCurrent] = Select[DownValues[BGCurrent], !FreeQ[#, Pattern | Blank] &];
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
  If[Length[freeW] != n - 2, Print["ERROR"]; Return[$Failed]];
  If[sigmas[[1]] + sigmas[[n]] != 0, Print["ERROR"]; Return[$Failed]];
  sumFree = Total[freeW];
  sigmaFree = sigmas[[2 ;; n - 1]];
  sumSigmaW2 = Total[sigmaFree*freeW^2];
  wn = -(sigmas[[1]]*sumFree^2 + sumSigmaW2)/(2*sigmas[[1]]*sumFree);
  w1 = -(sumFree + wn);
  allW = Join[{w1}, freeW, {wn}];
  allK = sigmas*allW^2/g;
  {allK, allW}]

gVal = 1;

(* Function to compute amplitude with numeric rational inputs *)
ComputeA[n_, wVals_List] := Module[{sigmas, ks, ws, amp},
  sigmas = Join[{-1, -1}, Table[1, {n - 2}]];
  {ks, ws} = MakeKinematics[n, wVals[[2 ;; n - 1]], sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  amp]

(* Test n=4 with some values *)
Print["=== n=4 tests ==="];
Print["Using parametrization: w1=-w3, w2=free, w3=free, w4=-w2"];
Do[
  w2 = RandomInteger[{1, 10}];
  w3 = RandomInteger[{1, 10}];
  If[w2 == w3, w3++]; (* avoid degenerate *)
  amp = ComputeA[4, {-w3, w2, w3, -w2}];
  Print["  w2=", w2, " w3=", w3, " => A4 = ", N[amp, 20], "  |A4| = ", N[Abs[amp], 20]];
  , {5}]

(* Try computing with MakeKinematics for n=4 *)
Print[""];
Print["=== n=4 using MakeKinematics ==="];
Do[
  sigmas = {-1, -1, 1, 1};
  freeW = {RandomInteger[{1,10}], RandomInteger[{1,10}]};
  {ks, ws} = MakeKinematics[4, freeW, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  Print["  freeW=", freeW, " => ws=", N[ws], " A4 = ", N[amp, 20]];
  , {3}]
