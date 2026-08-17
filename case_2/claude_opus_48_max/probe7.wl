Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* family w3=4,w4=9, w2=t. Compute exact A(t)/(-I) at rational t, check
   signature constant, reconstruct as rational function. *)
ts = Table[k/10, {k, 1, 14}];
pts = {};
sigs = {};
Do[Module[{ws, A, sg},
   ws = genPt[5, {t, 4, 9}]; A = ampR[ws];
   If[A === Indeterminate, Continue[]];
   sg = chamberSig[ws];
   AppendTo[pts, {t, A}]; AppendTo[sigs, sg]],
  {t, ts}];
Print["#points: ", Length[pts], "  distinct sigs: ", Length[Union[sigs]]];
Print["signatures: ", Union[sigs]];

(* test polynomiality of A(t)*(13+t)^p *)
Do[Module[{vals, ip, ok},
   vals = {#[[1]], #[[2]]*(13 + #[[1]])^p} & /@ pts;
   ip = InterpolatingPolynomial[vals[[1 ;; 8]], t];
   ip = Expand[ip];
   ok = Table[(ip /. t -> vals[[i, 1]]) - vals[[i, 2]], {i, 9, Length[vals]}];
   Print["p=", p, "  fit-from-8 max resid on rest = ", Max[Abs[ok]],
     If[Max[Abs[ok]] == 0, StringJoin["   POLY deg ", ToString[Exponent[ip, t]], ": ", ToString[ip]], ""]];
   ],
  {p, 0, 6}];
