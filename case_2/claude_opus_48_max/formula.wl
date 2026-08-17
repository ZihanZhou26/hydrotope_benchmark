(* ================================================================ *)
(*  Closed-form tree amplitude A_n, two-minus sector                *)
(*  sigma = (-1,-1,+1,...,+1)  (legs 1,2 are the minus legs).        *)
(*                                                                  *)
(*  A_n = -I * 2^(n-1) / g^(n-3) * w1 w2 *                          *)
(*        Sum_{S subset {3..n}} (-1)^(|S|+1) [ (w2^2 - q_S)_+ ]^(n-3)*)
(*  with q_S = Sum_{j in S} w_j^2,  (x)_+ = Max[x,0].               *)
(* ================================================================ *)

ATwoMinus[omegas_List, g_: 1] := Module[
  {n = Length[omegas], w1, w2, x, plus, m, tot},
  If[n < 4, Return[$Failed]];
  w1 = omegas[[1]]; w2 = omegas[[2]]; x = w2^2;
  plus = Range[3, n]; m = n - 3;
  tot = Total[Map[
     Function[S, Module[{qS = Total[omegas[[S]]^2], d},
       d = x - qS;
       If[d > 0, (-1)^(Length[S] + 1) d^m, 0]]],
     Subsets[plus]]];
  -I*2^(n - 1)/g^(n - 3)*w1*w2*tot];

(* active set = the chamber label *)
ActiveSet[omegas_List] := Module[{x = omegas[[2]]^2},
  Select[Subsets[Range[3, Length[omegas]]], x > Total[omegas[[#]]^2] &]];

(* quick demo when run directly *)
If[StringQ[$ScriptCommandLine] || Length[$ScriptCommandLine] > 0,
 Module[{},
  Print["A_5 at w={-4,1,2,3,-2}    = ", ATwoMinus[{-4, 1, 2, 3, -2}], "   (expect -64 I)"];
  Print["A_6 at w={-32/5,1,2,3,4,-18/5} = ", ATwoMinus[{-32/5, 1, 2, 3, 4, -18/5}], "   (expect -1024 I/5)"];
  Print["A_4 at w={-3,1,3,-1}      = ", ATwoMinus[{-3, 1, 3, -1}], "   (expect -24 I)"];
 ]];
