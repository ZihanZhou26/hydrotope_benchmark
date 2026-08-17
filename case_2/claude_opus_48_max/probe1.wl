Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/bg_defs.wl"];

gVal = 1;

(* two-minus sector sign vector *)
sig[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* Compute A_n at a given set of free frequencies (w2..w_{n-1}) *)
amp[n_, freeW_] := Module[{ks, ws},
  {ks, ws} = MakeKinematics[n, freeW, sig[n], gVal];
  {ws, ks, BGAmplitude[ks, ws, gVal]}];

Do[
  Module[{fw, r, fw2, r2},
   (* pick a point *)
   fw = Table[1 + j/3, {j, 1, n - 2}];
   r = amp[n, fw];
   Print["=== n=", n, " ==="];
   Print["  freeW = ", fw];
   Print["  allW  = ", r[[1]]];
   Print["  allK  = ", r[[2]]];
   Print["  sumW = ", Total[r[[1]]], "  sumK = ", Total[r[[2]]]];
   Print["  A_", n, " = ", r[[3]]];
   (* scale frequencies by 2: free freqs *2, check homogeneity *)
   fw2 = 2 fw;
   r2 = amp[n, fw2];
   Print["  A_", n, "(2w)/A_", n, "(w) = ", r2[[3]]/r[[3]], "   (=2^deg)"];
   ],
  {n, 4, 6}];
