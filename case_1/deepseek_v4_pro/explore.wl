(* Explore A_n in the two-minus sector *)

Get["/home/zihanz/waterhedron_benchmark_blind/case_1/OnShellBG.m"];

gVal = 1;

Print["=== n=4, two-minus sector ==="];
sigmas = {-1, -1, 1, 1};
{ks, ws} = MakeKinematics[4, {w2, w3}, sigmas, gVal];
Print["omegas: ", ws];
Print["momenta: ", ks];
amp4 = BGAmplitude[ks, ws, gVal];
Print["A4 = ", Simplify[amp4]];
Print[];

Print["=== n=5, two-minus sector ==="];
sigmas = {-1, -1, 1, 1, 1};
{ks, ws} = MakeKinematics[5, {w2, w3, w4}, sigmas, gVal];
Print["omegas: ", ws];
Print["momenta: ", ks];
amp5 = BGAmplitude[ks, ws, gVal];
Print["A5 = ", Simplify[amp5]];
Print[];

Print["=== n=6, two-minus sector ==="];
sigmas = {-1, -1, 1, 1, 1, 1};
{ks, ws} = MakeKinematics[6, {w2, w3, w4, w5}, sigmas, gVal];
Print["omegas: ", ws];
Print["momenta: ", ks];
amp6 = BGAmplitude[ks, ws, gVal];
Print["A6 = ", Simplify[amp6]];
