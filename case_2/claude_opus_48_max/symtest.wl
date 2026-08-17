Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* take an on-shell point; permuting plus legs (3..n) or minus legs (1,2)
   keeps both conservation laws -> stays on shell. Test if A is invariant. *)
ws0 = genPt[5, {1, 4, 8}];
Print["base w = ", ws0, "  A=", ampR[ws0]];

Print["\n-- permute MINUS legs {1,2} --"];
Module[{w}, w = ws0; w[[{1, 2}]] = ws0[[{2, 1}]];
  Print["  swap 1<->2: w=", w, "  A=", ampR[w]]];

Print["\n-- permute PLUS legs {3,4,5} --"];
Do[Module[{w, perm}, perm = p; w = ws0;
   w[[3 ;; 5]] = ws0[[3 ;; 5]][[perm]];
   Print["  perm ", perm, ": w=", w, "  A=", ampR[w]]],
  {p, Permutations[{1, 2, 3}]}];

Print["\n-- also: is A invariant under swapping a plus and minus leg? (NOT expected) --"];
Module[{w}, w = ws0; w[[{2, 3}]] = ws0[[{3, 2}]];
  Print["  swap 2<->3: w=", w, "  on-shell? sumw=", Total[w],
   " mom=", Total[kvec[w]], "  A=", ampR[w]]];
