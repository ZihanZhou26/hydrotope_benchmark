(* sign-frozen symbolic evaluator: override mag to freeze sign at a base pt *)
Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];

(* redefine mag to use frozen signs from global $signRules *)
Clear[mag];
mag[k_] := Module[{v = k /. $signRules},
  If[NumericQ[v] && v != 0, Sign[v]*k,
    Print["WARN: sign undetermined for ", k, " -> ", v]; Abs[k]]];

twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* --- symbolic A_5 in free freqs {w2,w3,w4}, base = {3/2,2,5/2} --- *)
Module[{n=5, sig, ks, ws, amp, base},
  sig = twoMinus[n];
  base = {w2 -> 3/2, w3 -> 2, w4 -> 5/2};
  (* symbolic kinematics *)
  {ks, ws} = MakeKinematics[n, {w2, w3, w4}, sig, 1];
  Print["symbolic ws = ", ws];
  (* freeze signs: need sign of every momentum that mag sees.
     all such momenta are sums of ks; ks are rational in w2,w3,w4.
     set $signRules from base. *)
  $signRules = base;
  amp = BGAmplitude[ks, ws, 1];
  amp = Simplify[amp];
  Print["A_5(w2,w3,w4) = ", amp];
  Print["--- factored ---"];
  Print["A_5 = ", Factor[amp]];
  Print["--- check at base: ", amp /. base, "  (expect -891/2 I) ---"];
];

Print["DONE probe3"];
