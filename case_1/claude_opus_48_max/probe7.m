Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
ampAt[n_, freeW_] := Module[{ks, ws, a},
  {ks, ws} = MakeKinematics[n, freeW, twoMinusSigma[n], 1];
  a = BGAmplitude[ks, ws, 1];
  {ws, a}];

Print["=== Test prediction A_n = 2^(n-1) I w1 w2^(2n-5) in ascending chamber ==="];
tests = {
  {4, {2, 3}}, {4, {1, 5}},
  {5, {2, 3, 5}}, {5, {1, 4, 9}},
  {6, {2, 3, 5, 7}}, {6, {1, 2, 4, 8}}, {6, {3, 4, 5, 6}},
  {7, {2, 3, 5, 7, 11}}, {7, {1, 2, 3, 4, 5}}
};
Do[Module[{n, fw, ws, a, w1, w2, pred},
   {n, fw} = t;
   {ws, a} = ampAt[n, fw];
   w1 = ws[[1]]; w2 = ws[[2]];
   pred = 2^(n - 1) I w1 w2^(2 n - 5);
   Print["n=", n, " free=", fw];
   Print["   ws=", N[ws, 5]];
   Print["   BG    = ", a];
   Print["   pred  = ", pred, "   match? ", Simplify[a - pred] === 0];
   ],
  {t, tests}]

Print[];
Print["=== Does it depend ONLY on w1,w2? vary plus legs, keep w2 smallest ==="];
(* n=6: change which free freqs but keep ascending & w2 smallest, see if BG
   matches 2^(n-1) I w1 w2^(2n-5) always *)
Do[Module[{ws, a, w1, w2, pred},
   {ws, a} = ampAt[6, fw];
   w1 = ws[[1]]; w2 = ws[[2]];
   pred = 2^5 I w1 w2^7;
   Print["n=6 free=", fw, "  BG=", N[a,6], "  pred=", N[pred,6],
     "  match? ", Simplify[a - pred] === 0]],
  {fw, {{2, 3, 5, 7}, {2, 10, 11, 13}, {2, 3, 100, 101}, {5, 6, 7, 8}}}]
