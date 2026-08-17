Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

(* Symbolic A4 in two-minus sector.
   Free frequencies w2 (minus leg), w3 (plus leg). Solve w1, w4.
   Keep symbolic, then inspect.  g = 1. *)

sig = {-1, -1, 1, 1};
{ks, ws} = MakeKinematics[4, {w2, w3}, sig, 1];
Print["ws = ", ws // Simplify];
Print["ks = ", ks // Simplify];

(* Compute amplitude symbolically. Abs will appear for internal momenta. *)
amp = BGAmplitude[ks, ws, 1];
Print["raw amp (with Abs) = "];
Print[amp];

Print["----- FullSimplify assuming w2>0, w3>0 -----"];
ampS = FullSimplify[amp, Assumptions -> {w2 > 0, w3 > 0}];
Print[ampS];

Print["----- Try assuming w3 > w2 > 0 -----"];
ampS2 = FullSimplify[amp, Assumptions -> {w3 > w2 > 0}];
Print[ampS2];

Print["----- Try assuming w2 > w3 > 0 -----"];
ampS3 = FullSimplify[amp, Assumptions -> {w2 > w3 > 0}];
Print[ampS3];
