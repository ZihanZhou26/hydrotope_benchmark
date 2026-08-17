Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/bg_defs.wl"];
gVal = 1;
sig[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

amp[n_, freeW_] := Module[{ks, ws, a},
  {ks, ws} = MakeKinematics[n, freeW, sig[n], gVal];
  a = BGAmplitude[ks, ws, gVal];
  {ws, a}];

(* ---- n=5: many simple points ---- *)
Print["################ n = 5 ################"];
pts5 = {{1, 2, 3}, {2, 3, 5}, {1, 2, 4}, {1, 3, 5}, {2, 5, 11}, {1, 1, 1},
        {3, 1, 2}, {1, 4, 2}, {2, 1, 5}, {3, 5, 2}};
Do[Module[{r}, r = amp[5, p];
   Print["w=", r[[1]], "   A5=", r[[2]], "  =", If[r[[2]]=!=0, FactorInteger[Im[r[[2]]]], 0]]],
  {p, pts5}];

Print["\n################ n = 6 ################"];
pts6 = {{1, 2, 3, 4}, {2, 3, 5, 7}, {1, 2, 3, 5}, {1, 1, 1, 1}, {1, 2, 4, 8}};
Do[Module[{r}, r = amp[6, p];
   Print["w=", r[[1]], "   A6=", r[[2]]]],
  {p, pts6}];

Print["\n################ n = 7 ################"];
pts7 = {{1, 2, 3, 4, 5}, {1, 1, 1, 1, 1}, {2, 3, 5, 7, 11}};
Do[Module[{r}, r = amp[7, p];
   Print["w=", r[[1]], "   A7=", r[[2]]]],
  {p, pts7}];
