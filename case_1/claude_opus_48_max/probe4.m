Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

sig5 = {-1, -1, 1, 1, 1};
bgAt[a_, b_, c_] := Module[{ks, ws},
  {ks, ws} = MakeKinematics[5, {a, b, c}, sig5, 1];
  BGAmplitude[ks, ws, 1]];

(* candidate chamber-A formula: a=w2,b=w3,c=w4 *)
fA[a_, b_, c_] := -16 I a^5 (a b + b^2 + a c + b c + c^2)/(a + b + c);

Print["=== Verify chamber-A formula vs BG ==="];
pts = {{2, 3, 5}, {3, 5, 7}, {1, 4, 9}, {2, 5, 6}, {7, 11, 2}, {5, 3, 2}, {9, 4, 1},
       {3, 5, -2}, {-2, 3, 5}, {4, -3, 5}};
Do[Module[{bg, f},
   bg = bgAt @@ p; f = fA @@ p;
   Print["  (a,b,c)=", p, "  BG=", N[bg], "  fA=", N[f],
     "  match? ", Simplify[bg - f] === 0]],
  {p, pts}]

Print[];
Print["=== Map: for positive (a,b,c), does fA match BG? scan orderings ==="];
scan = {{2, 3, 5}, {2, 5, 3}, {3, 2, 5}, {3, 5, 2}, {5, 2, 3}, {5, 3, 2}};
Do[Module[{bg, f},
   bg = bgAt @@ p; f = fA @@ p;
   Print["  (a,b,c)=", p, "  ratio BG/fA = ", Simplify[bg/f]]],
  {p, scan}]
