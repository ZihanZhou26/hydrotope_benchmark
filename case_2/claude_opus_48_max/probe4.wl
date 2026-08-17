Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/bg_defs.wl"];
gVal = 1;
sig[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* Symbolic n=5 in a definite chamber.
   Free omegas a=w2, b=w3, c=w4 ; solve w1,w5.
   Choose chamber by assumption: a is SMALLEST positive, b,c larger. *)
$Assumptions = 0 < a < b < c;

Module[{ks, ws, amp},
  {ks, ws} = MakeKinematics[5, {a, b, c}, sig[5], gVal];
  ws = Simplify[ws];
  ks = Simplify[ks];
  Print["allW = ", ws];
  Print["allK = ", ks];
  Print["sumW = ", Simplify[Total[ws]], "  sumK = ", Simplify[Total[ks]]];
  Print["Computing A5 symbolically..."];
  amp = BGAmplitude[ks, ws, gVal];
  Print["raw amp (head): ", Head[amp]];
  amp = Simplify[amp, 0 < a < b < c];
  Print["A5 (simplified) = ", amp];
  Print["A5/(-I) = ", Simplify[amp/(-I), 0 < a < b < c]];
  Print["FullSimplify A5/(-I) = ", FullSimplify[amp/(-I), 0 < a < b < c]];
];
