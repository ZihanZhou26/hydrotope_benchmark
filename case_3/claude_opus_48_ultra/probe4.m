Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* on-shell n=5 base point *)
sig = twoMinus[5];
{ks, ws} = MakeKinematics[5, {3/2, 2, 5/2}, sig, 1];
Print["base ws = ", ws, "   ks = ", ks];
Print["base A5 = ", BGAmplitude[ks, ws, 1]];

(* helper: permute legs by perm (list of new order), recompute *)
permAmp[perm_] := Module[{ws2, ks2},
  ws2 = ws[[perm]]; ks2 = ks[[perm]];
  BGAmplitude[ks2, ws2, 1]];

Print["\n--- swap minus legs 1<->2  (perm {2,1,3,4,5}) ---"];
Print["A = ", permAmp[{2,1,3,4,5}]];

Print["\n--- swap plus legs 3<->4  (perm {1,2,4,3,5}) ---"];
Print["A = ", permAmp[{1,2,4,3,5}]];

Print["\n--- cycle plus legs 3->4->5  (perm {1,2,5,3,4}) ---"];
Print["A = ", permAmp[{1,2,5,3,4}]];

Print["\n--- swap plus legs 3<->5 (perm {1,2,5,4,3}) ---"];
Print["A = ", permAmp[{1,2,5,4,3}]];

(* compare to candidate 16 I w1 w2^5 with these permuted labels *)
Print["\n--- candidate 16 I w1 w2^5 (using leg1,leg2 of permuted list) ---"];
cand[perm_] := Module[{ww=ws[[perm]]}, 16 I ww[[1]] ww[[2]]^5];
Print["orig    : ", cand[{1,2,3,4,5}]];
Print["swap12  : ", cand[{2,1,3,4,5}]];

Print["\nDONE probe4"];
