Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

(* Build full kinematics for n=5 two-minus, then test permutation symmetry
   of BGAmplitude by relabeling legs (permuting BOTH momenta and omegas). *)

sig5 = {-1, -1, 1, 1, 1};
{ks0, ws0} = MakeKinematics[5, {2, 3, 5}, sig5, 1];
Print["base ws = ", ws0, "   ks = ", ks0];
ampBase = BGAmplitude[ks0, ws0, 1];
Print["A(base) = ", ampBase];

(* swap legs 1<->2 (both minus) *)
perm12 = {2, 1, 3, 4, 5};
Print["A(swap 1<->2) = ", BGAmplitude[ks0[[perm12]], ws0[[perm12]], 1]];

(* swap legs 3<->4 (both plus) *)
perm34 = {1, 2, 4, 3, 5};
Print["A(swap 3<->4) = ", BGAmplitude[ks0[[perm34]], ws0[[perm34]], 1]];

(* cycle the three plus legs 3->4->5->3 *)
perm345 = {1, 2, 5, 3, 4};
Print["A(cycle 3,4,5) = ", BGAmplitude[ks0[[perm345]], ws0[[perm345]], 1]];

(* arbitrary perm of all 5 *)
permX = {3, 1, 5, 2, 4};
Print["A(perm {3,1,5,2,4}) = ", BGAmplitude[ks0[[permX]], ws0[[permX]], 1]];

Print[];
Print["Conclusion checks (should A be invariant under same-sigma perms?):"];
Print["  inv under 1<->2 ? ", BGAmplitude[ks0[[perm12]], ws0[[perm12]], 1] == ampBase];
Print["  inv under 3<->4 ? ", BGAmplitude[ks0[[perm34]], ws0[[perm34]], 1] == ampBase];
