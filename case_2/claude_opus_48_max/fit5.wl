Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* Generate a batch of n=5 points with diverse free freqs (all positive,
   chosen so leg-2 freq is the smallest -> aim for one chamber). *)
freqsets = Flatten[Table[{a, b, c},
   {a, {1, 2, 3}}, {b, {4, 5, 7}}, {c, {8, 11, 13}}], 2];

data = {};
Do[Module[{ws, sg, A, esp},
   ws = genPt[5, fs];
   A = ampR[ws];
   If[A === Indeterminate, Continue[]];
   sg = chamberSig[ws];
   esp = plusESP[ws];
   AppendTo[data, <|"free" -> fs, "w" -> ws, "A" -> A, "sig" -> sg, "esp" -> esp|>]
   ], {fs, freqsets}];

Print["total points: ", Length[data]];

(* group by signature *)
groups = GatherBy[data, #["sig"] &];
groups = SortBy[groups, -Length[#] &];
Print["num chambers seen: ", Length[groups]];
Do[Print["  chamber size ", Length[g], "  sig=", g[[1]]["sig"]], {g, groups}];

(* Fit the largest chamber.  Basis: monomials p1^a p2^b p3^c, a+2b+3c=6 *)
mono5 = {{6, 0, 0}, {4, 1, 0}, {2, 2, 0}, {0, 3, 0}, {3, 0, 1}, {1, 1, 1}, {0, 0, 2}};
basis[esp_, monos_] := (Times @@ (esp^#)) & /@ monos;

big = groups[[1]];
Print["\nFitting largest chamber, size ", Length[big]];
Module[{mat, rhs, sol, cf},
  mat = basis[#["esp"], mono5] & /@ big;
  rhs = #["A"] & /@ big;
  (* least squares / exact solve using first 7, then check all *)
  sol = LinearSolve[mat[[1 ;; 7]], rhs[[1 ;; 7]]];
  Print["coeffs (p1^a p2^b p3^c order ", mono5, "):"];
  Print["  ", sol];
  (* verify on all points in chamber *)
  cf = Table[basis[big[[i]]["esp"], mono5].sol - big[[i]]["A"], {i, Length[big]}];
  Print["max residual over chamber: ", Max[Abs[cf]]];
];
