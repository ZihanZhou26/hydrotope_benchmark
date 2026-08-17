Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
(* keep mag = Abs but teach it Abs[real^2]=real^2 *)
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

$Assumptions = v1 > 0 && v2 > 0 && v3 > 0 && g > 0;

sig = twoMinus[5];
{ks, ws} = MakeKinematics[5, {v1, v2, v3}, sig, g];
Print["ws = ", ws // Simplify];
Print["ks = ", ks // Simplify];

amp = BGAmplitude[ks, ws, g];
Print["--- raw amp computed, now simplifying ---"];
amp2 = Simplify[amp, $Assumptions];
Print["A_5 (Simplify) = ", amp2];
Print["\n--- FullSimplify ---"];
amp3 = FullSimplify[amp, $Assumptions, TimeConstraint -> 120];
Print["A_5 (FullSimplify) = ", amp3];

Print["DONE probe9"];
