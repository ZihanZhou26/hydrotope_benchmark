<< bg_core.m
Unprotect[mag]; ClearAll[mag];
mag[z_] := Abs[z];
(* fix plus free freqs b=3,c=5, vary a=w2 symbolically, keep Abs *)
sig = {-1,-1,1,1,1};
b = 3; cc = 5;
{ks, ws} = MakeKinematics[5, {a, b, cc}, sig, 1];
Print["ws = ", Simplify[ws, a \[Element] Reals]];
Print["ks = ", Simplify[ks, a \[Element] Reals]];
amp = BGAmplitude[ks, ws, 1];
res = FullSimplify[amp/I, a \[Element] Reals];
Print["c = A/I = ", res];
