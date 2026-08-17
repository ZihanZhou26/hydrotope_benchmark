Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* diverse free freqs, ensure a (=w2) is the smallest so we stay in chamber
   {-1,1,...,1}. Use varied rationals. *)
SeedRandom[42];
raw = {};
Do[Module[{a, b, c},
   a = RandomInteger[{1, 6}] + RandomChoice[{0, 1/2, 1/3, 2/3}];
   b = a + RandomInteger[{2, 8}];
   c = b + RandomInteger[{1, 9}];
   AppendTo[raw, {a, b, c}]], {40}];
raw = DeleteDuplicates[raw];

data = {};
Do[Module[{ws, A, sg, esp},
   ws = genPt[5, fs]; A = ampR[ws];
   If[A === Indeterminate, Continue[]];
   sg = chamberSig[ws]; esp = plusESP[ws];
   AppendTo[data, <|"free"->fs,"w"->ws,"A"->A,"sig"->sg,"esp"->esp|>]],
  {fs, raw}];

groups = GatherBy[data, #["sig"] &];
groups = SortBy[groups, -Length[#] &];
Print["chambers: ", Length[groups], "  sizes: ", Length /@ groups];
big = groups[[1]];
Print["fitting chamber sig=", big[[1]]["sig"], " size ", Length[big]];

mono5 = {{6,0,0},{4,1,0},{2,2,0},{0,3,0},{3,0,1},{1,1,1},{0,0,2}};
basis[esp_] := (Times @@ (esp^#)) & /@ mono5;
mat = basis[#["esp"]] & /@ big;
rhs = #["A"] & /@ big;
Print["matrix rank (exact): ", MatrixRank[mat]];

(* find 7 rows forming a rank-7 submatrix, exact solve *)
Module[{rows, sub, sol, resid},
  rows = {};
  Do[If[MatrixRank[mat[[Append[rows, i]]]] == Length[rows] + 1,
       AppendTo[rows, i]; If[Length[rows] == 7, Break[]]], {i, Length[mat]}];
  Print["solve rows: ", rows];
  sub = mat[[rows]];
  sol = LinearSolve[sub, rhs[[rows]]];
  Print["coeffs (order ", mono5, "):"];
  Print["  ", sol];
  resid = Table[mat[[i]].sol - rhs[[i]], {i, Length[mat]}];
  Print["EXACT max residual over all chamber pts: ", Max[Abs[resid]]];
];
