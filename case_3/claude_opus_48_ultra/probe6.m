Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
gVal = 1;

(* candidates (g=1):
   P  = 2^(n-1) I w1 w2^(2n-5)                 [labeled / region form]
   M  = 2^(n-1) I w1 w2 min(w1^2,w2^2)^(n-3)   [symmetric "min"]
   X  = 2^(n-1) I w1 w2 max(w1^2,w2^2)^(n-3)   [symmetric "max"]  *)
candP[n_, w_] := 2^(n-1) I w[[1]] w[[2]]^(2 n - 5);
candM[n_, w_] := 2^(n-1) I w[[1]] w[[2]] Min[w[[1]]^2, w[[2]]^2]^(n - 3);
candX[n_, w_] := 2^(n-1) I w[[1]] w[[2]] Max[w[[1]]^2, w[[2]]^2]^(n - 3);

relerr[a_, b_] := If[b == 0, Abs[a], Abs[(a - b)/b]] // N;

test[n_, freeW_] := Module[{sig, ks, ws, amp, P, M, X},
  sig = twoMinus[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  P = candP[n, ws]; M = candM[n, ws]; X = candX[n, ws];
  Print["n=", n, " free=", freeW];
  Print["   w=", ws, "   |w1|=", N@Abs[ws[[1]]], " |w2|=", N@Abs[ws[[2]]]];
  Print["   A      = ", amp, "  (", N[amp], ")"];
  Print["   relerr  P=", relerr[P, amp], "  M=", relerr[M, amp], "  X=", relerr[X, amp]];
];

Print["===== n=5 across regions ====="];
test[5, {3/2, 2, 5/2}];        (* base; |w2|<|w1| *)
test[5, {2, 3, 7}];            (* |w2|<|w1| *)
test[5, {1000, 1, 1}];         (* free minus HUGE -> |w2|>>|w1| : discriminator *)
test[5, {1/1000, 1, 1}];       (* free minus tiny *)
test[5, {-3/2, 2, 5/2}];       (* free minus NEGATIVE *)
test[5, {5, -2, 3}];           (* a plus leg free negative *)
test[5, {7/3, 11/5, 13/7}];    (* generic rationals *)

Print["\n===== n=6 across regions ====="];
test[6, {3/2, 2, 5/2, 3}];
test[6, {1000, 1, 1, 1}];      (* discriminator *)
test[6, {-2, 3, 5, 7}];
test[6, {1, 3, 5, 7}];

Print["\n===== n=7 across regions ====="];
test[7, {3/2, 2, 5/2, 3, 7/2}];
test[7, {500, 1, 1, 1, 1}];    (* discriminator *)

Print["\nDONE probe6"];
