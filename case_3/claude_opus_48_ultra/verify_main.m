(* ================================================================ *)
(*  verify_main.m  — verify  A_n = 2^(n-1) I w1 w2^(2n-5) / g^(n-3)  *)
(*  in the principal chamber (free minus leg w2 = smallest |w|).     *)
(* ================================================================ *)
Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];

twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
gVal = 1;

(* the conjectured closed form *)
Formula[n_, w_, g_] := 2^(n - 1) I w[[1]] w[[2]]^(2 n - 5) / g^(n - 3);

relerr[a_, b_] := If[b === 0 || b == 0, Abs[N[a]], Abs[N[(a - b)/b]]];

isPrincipal[w_] := (w[[2]]^2 == Min[w^2]);  (* |w2| strictly smallest *)

check[n_, freeW_] := Module[{sig, ks, ws, amp, fo, re},
  sig = twoMinus[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  fo = Formula[n, ws, gVal];
  re = relerr[fo, amp];
  Print["  n=", n, " free=", freeW,
    "  principal?=", isPrincipal[ws]];
  Print["     w=", N[ws, 6]];
  Print["     BG     = ", N[amp, 16]];
  Print["     formula= ", N[fo, 16]];
  Print["     relerr = ", N[re], If[re == 0, "   [EXACT match]", "   <-- MISMATCH"]];
  {n, freeW, re, isPrincipal[ws]}
];

Print["==================================================================="];
Print["  PRINCIPAL-CHAMBER VERIFICATION  (exact rational arithmetic)"];
Print["  Formula:  A_n = 2^(n-1) i w1 w2^(2n-5) / g^(n-3)"];
Print["==================================================================="];

Print["\n----- n=5 : sorted positive + extreme hierarchies -----"];
check[5, {3/2, 2, 5/2}];
check[5, {2, 3, 7}];
check[5, {1, 10, 100}];           (* huge plus legs *)
check[5, {1/1000, 1, 1}];          (* tiny w2 *)
check[5, {1, 1000, 1000000}];      (* extreme plus hierarchy *)
check[5, {1/7, 13/11, 99/2}];      (* generic, w2 smallest *)

Print["\n----- n=6 : sorted positive + extreme -----"];
check[6, {3/2, 2, 5/2, 3}];
check[6, {1, 3, 5, 7}];
check[6, {2, 3, 7, 11}];
check[6, {1/100, 5, 50, 500}];     (* tiny w2, huge plus *)
check[6, {1, 1000, 2000, 3000}];

Print["\n----- n=7 : sorted positive + extreme -----"];
check[7, {3/2, 2, 5/2, 3, 7/2}];
check[7, {1, 2, 3, 4, 5}];
check[7, {1/10, 2, 4, 8, 16}];

Print["\n----- (documentation) NON-principal points: formula NOT expected to hold -----"];
check[5, {1000, 1, 1}];            (* w2 largest -> chamber B *)
check[5, {7/3, 11/5, 13/7}];       (* chamber C *)
check[6, {5, 1, 2, 3}];            (* w2 not smallest *)

Print["\nDONE verify_main"];
