Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

(* n=4 two-minus: the on-shell conditions FORCE w1 = -w3, w4 = -w2, hence
   k2 + k4 = 0 and w2 + w4 = 0, so the {2,4} sub-current propagator is a
   removable 0/0 and a direct numeric BGAmplitude returns Indeterminate.
   The amplitude is the finite limit, obtained by keeping Abs[.] symbolic.   *)

sig = {-1, -1, 1, 1};
{ks, ws} = MakeKinematics[4, {w2, w3}, sig, 1];
Print["forced kinematics: ws = ", ws, "   ks = ", Simplify[ks]];
Print["  -> k2+k4 = ", Simplify[ks[[2]] + ks[[4]]], ",  w2+w4 = ", Simplify[ws[[2]] + ws[[4]]],
      "   (both identically 0 => removable 0/0)"];

amp = BGAmplitude[ks, ws, 1];

Print[];
Print["A_4 (symbolic limit), assuming 0 < w2 < w3  [ascending / canonical]:"];
a4asc = FullSimplify[amp, Assumptions -> {0 < w2 < w3}];
Print["   FullSimplify[BG]   = ", a4asc];
Print["   canonical 8 I w1 w2^3 = ", Simplify[8 I ws[[1]] w2^3], "   (w1 = -w3)"];
Print["   equal? ", Simplify[a4asc - 8 I ws[[1]] w2^3] === 0];

Print[];
Print["A_4 for the other ordering 0 < w3 < w2:"];
a4desc = FullSimplify[amp, Assumptions -> {0 < w3 < w2}];
Print["   FullSimplify[BG]   = ", a4desc, "   (= -8 I w2 w3^3, the swapped piece)"];

Print[];
Print["Numeric examples (ascending w2<w3): A_4 = -8 I w2^3 w3"];
Do[Print["   (w2,w3)=", p, "  A_4 = ", -8 I p[[1]]^3 p[[2]],
     "   canonical(8 I w1 w2^3)= ", 8 I (-p[[2]]) p[[1]]^3],
  {p, {{3/2, 5/2}, {1, 4}, {2, 7}}}]
