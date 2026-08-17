Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* 1. confirm degree via scaling on a concrete point *)
ws0 = genPt[5, {1, 4, 8}];
Print["A(w)=", ampR[ws0], "  A(3w)/A(w)=", ampR[3 ws0]/ampR[ws0], " (=3^deg)"];

(* 2. collect same-chamber points, print (P1,P2,P3,A) *)
freqsets = {{1,4,8},{1,4,11},{1,5,8},{1,5,13},{2,5,11},{1,7,13},{2,7,11},
            {3,7,13},{1,4,9},{2,9,13},{1,6,10},{3,8,11}};
data = {};
Do[Module[{ws, A, sg, esp},
   ws = genPt[5, fs]; A = ampR[ws];
   If[A === Indeterminate, Continue[]];
   sg = chamberSig[ws]; esp = plusESP[ws];
   AppendTo[data, <|"free"->fs,"w"->ws,"A"->A,"sig"->sg,"esp"->esp|>]],
  {fs, freqsets}];
Print["sigs distinct: ", Length[Union[#["sig"]&/@data]]];
Print["P1,P2,P3 , A:"];
Do[Print["  ", d["esp"], "  -> ", d["A"]], {d, data}];

(* 3. fit degree-6 in (P1,P2,P3): 7 monomials *)
mono5 = {{6,0,0},{4,1,0},{2,2,0},{0,3,0},{3,0,1},{1,1,1},{0,0,2}};
basis[esp_] := (Times @@ (esp^#)) & /@ mono5;
mat = basis[#["esp"]] & /@ data;
rhs = #["A"] & /@ data;
Print["\nmatrix rank: ", MatrixRank[mat], " (of ", Length[mono5], " cols, ", Length[mat], " rows)"];
Module[{sol, res},
  sol = LeastSquares[N[mat], N[rhs]];
  Print["LS coeffs (numeric): ", sol];
  res = N[mat].sol - N[rhs];
  Print["LS max resid: ", Max[Abs[res]]];
];

(* 4. Maybe NOT symmetric-reducible: fit a general degree-6 homogeneous
      polynomial in the raw plus-leg freqs x=w3,y=w4,z=w5 (symmetric assumed).
      Already done via ESP. Try instead direct monomials in all 5 w's? *)
