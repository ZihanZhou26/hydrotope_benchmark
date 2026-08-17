Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
Clear[mag];
mag[k_] := Module[{v = k /. $signRules},
  If[NumericQ[v] && v != 0, Sign[v]*k, Print["WARN sign ", InputForm@k]; Abs[k]]];
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* symbolic A_5 (g=1) in the sign-region of a given numeric base free pt.
   Returns reduced rational function in v1,v2,v3 and value at base. *)
regionForm[baseFree_] := Module[{sig, ks, ws, amp, vs, baseRules, w1, w2, wn},
  sig = twoMinus[5];
  vs = {v1, v2, v3};
  baseRules = Thread[vs -> baseFree];
  {ks, ws} = MakeKinematics[5, vs, sig, 1];
  $signRules = baseRules;
  amp = BGAmplitude[ks, ws, 1];
  amp = Together[amp];
  Print["base free = ", baseFree];
  Print["  w(symbolic) w1=", ws[[1]]//Together, "  w5=", ws[[5]]//Together];
  Print["  w(numeric)  = ", ws /. baseRules];
  Print["  A_5 reduced = ", amp];
  Print["  A_5 at base = ", amp /. baseRules, "\n"];
  {amp, ws, baseRules}
];

Print["===== R1: {3/2,2,5/2} (base region) ====="];
regionForm[{3/2, 2, 5/2}];
Print["===== R3: {1000,1,1} (free minus huge) ====="];
regionForm[{1000, 1, 1}];
Print["===== R5: {-3/2,2,5/2} (free minus negative) ====="];
regionForm[{-3/2, 2, 5/2}];
Print["===== R6: {7/3,11/5,13/7} (unsorted) ====="];
regionForm[{7/3, 11/5, 13/7}];
Print["===== R7: {1,5,2} (free plus reordered) ====="];
regionForm[{1, 5, 2}];
Print["===== R8: {3,1,1} (free minus largest, modest) ====="];
regionForm[{3, 1, 1}];

Print["DONE probe7"];
