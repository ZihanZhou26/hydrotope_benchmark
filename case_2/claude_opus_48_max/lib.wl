(* Shared library: BG defs + helpers for chamber signatures and fitting *)
Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/bg_defs.wl"];
gVal = 1;
sig[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* signed external momenta from omega vector in two-minus sector *)
kvec[ws_] := sig[Length[ws]]*ws^2;

(* chamber signature: sign of k_T for all nonempty T subset of {2..n}.
   (k_1 + k_T handled via complement; total k=0.) *)
chamberSig[ws_] := Module[{n = Length[ws], k = kvec[ws], subs},
  subs = Subsets[Range[2, n]];
  subs = DeleteCases[subs, {}];
  Sign[Total[k[[#]]] & /@ subs]];

(* elementary symmetric polys of the PLUS legs {3..n} *)
plusESP[ws_] := Module[{n = Length[ws], pl},
  pl = ws[[3 ;;]];
  Table[SymmetricPolynomial[j, pl], {j, 1, n - 2}]];

(* generate an on-shell point in two-minus sector with free freqs freeW *)
genPt[n_, freeW_] := Module[{ks, ws},
  {ks, ws} = MakeKinematics[n, freeW, sig[n], gVal];
  ws];

(* compute amplitude / (-I), should be real rational *)
ampR[ws_] := Module[{a}, a = BGAmplitude[kvec[ws], ws, gVal];
  If[a === Indeterminate || ! NumericQ[a], Indeterminate, a/(-I)]];
