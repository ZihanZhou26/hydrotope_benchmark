Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
gVal = 1;
Formula[n_, w_, g_] := 2^(n - 1) I w[[1]] w[[2]]^(2 n - 5)/g^(n - 3);

Do[Module[{sig, ks, ws, amp, fo, t},
   sig = twoMinus[8];
   {ks, ws} = MakeKinematics[8, freeW, sig, gVal];
   t = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal]][[1]];
   fo = Formula[8, ws, gVal];
   Print["n=8 free=", freeW, "  w2=", ws[[2]], " smallest?=", ws[[2]]^2 == Min[ws^2]];
   Print["   BG      = ", amp];
   Print["   formula = ", fo];
   Print["   relerr  = ", N[Abs[(fo - amp)/amp]], "   time=", Round[t, 0.1], "s\n"];
  ], {freeW, {{1, 2, 3, 4, 5, 6}, {1/2, 2, 3, 5, 7, 11}}}];
Print["DONE verify_n8"];
