(* n=4 two-minus is kinematically DEGENERATE: on-shell forces a zero-
   momentum/zero-frequency leg pair (w4=-w2 => k2+k4=0, w2+w4=0), so the
   {2,4} channel propagator is 0/0 and BGAmplitude returns Indeterminate.
   The amplitude is FINITE as a limit (w^2/|k| -> 0 so that propagator -> i/g).
   Verify  A_4 = 2^3 i w1 w2^3 / g = 8 i w1 w2^3 / g   via a detuned limit. *)
Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
gVal = 1;

(* exact degenerate point: free {w2,w3} -> w1=-w3, w4=-w2 *)
Print["--- exact degenerate n=4 (expect Indeterminate from BG) ---"];
Module[{ws = {-2, 3/2, 2, -3/2}, ks},
  ks = {-1, -1, 1, 1} ws^2/gVal;
  Print["  w=", ws, "  BG = ", BGAmplitude[ks, ws, gVal]];
];

(* detuned family: w4 = -w2 + t,  w1 = -(w2+w3+w4),  k_i = sig_i w_i^2/g.
   As t->0 momentum conservation is restored and {2,4} propagator -> i/g. *)
detuned[w2_, w3_, t_] := Module[{w1, w4, ws, ks},
  w4 = -w2 + t; w1 = -(w2 + w3 + w4);
  ws = {w1, w2, w3, w4};
  ks = {-1, -1, 1, 1} ws^2/gVal;
  {ks, ws}];

Print["\n--- numerical limit t->0  (w2=3/2, w3=2 ; formula predicts 8 i w1 w2^3 with w1->-w3=-2) ---"];
Print["  predicted A_4 = ", N[8 I (-2) (3/2)^3, 16], "   (= -8 i w2^3 w3)"];
Do[Module[{ks, ws, amp},
   {ks, ws} = detuned[3/2, 2, t];
   amp = BGAmplitude[ks, ws, gVal];
   Print["  t=", N[t], "  A_4(t) = ", N[amp, 16]];
  ], {t, {1/10, 1/100, 1/1000, 1/10^6, 1/10^9}}];

Print["\n--- symbolic limit t->0 (sign-frozen mag at base) ---"];
Clear[mag];
mag[k_] := Module[{v = k /. $signRules},
  If[NumericQ[v] && v != 0, Sign[v]*k, Abs[k]]];
Module[{ks, ws, amp, lim},
  {ks, ws} = detuned[a, b, t];           (* a=w2, b=w3 symbolic, t symbolic *)
  $signRules = {a -> 3/2, b -> 2, t -> 1/1000};
  amp = BGAmplitude[ks, ws, gVal];
  lim = Limit[amp, t -> 0];
  Print["  lim_{t->0} A_4(a,b) = ", Simplify[lim]];
  Print["  formula 8 i w1 w2^3 with w1=-b, w2=a : ", 8 I (-b) a^3];
  Print["  difference = ", Simplify[lim - 8 I (-b) a^3]];
];

Print["\nDONE verify_n4"];
