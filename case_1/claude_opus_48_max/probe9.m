Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];
twoMinusSigma[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
mk[n_, fw_] := MakeKinematics[n, fw, twoMinusSigma[n], 1];
canon[n_, ws_] := 2^(n - 1) I ws[[1]] ws[[2]]^(2 n - 5);

SeedRandom[2024];
(* generate ascending positive free frequencies, comparable magnitude *)
ascFree[n_] := Module[{r}, r = Sort[Table[RandomInteger[{1, 9}] + RandomChoice[{0,1/2,1/3,1/4}], {n - 2}]];
   r];

Print["n | #pts | all match? | w2=min always? | maxRelErr"];
Do[Module[{npts, fws, results, allmatch, w2min, maxerr},
   npts = Switch[n, 4, 25, 5, 25, 6, 15, 7, 6];
   fws = DeleteDuplicates@Table[ascFree[n], {3 npts}];
   fws = Select[fws, (Length[Union[#]] == Length[#]) &]; (* distinct freqs *)
   fws = Take[fws, Min[npts, Length[fws]]];
   allmatch = True; w2min = True; maxerr = 0;
   Do[Module[{ks, ws, bg, pred, rel},
      {ks, ws} = mk[n, fw];
      bg = BGAmplitude[ks, ws, 1];
      pred = canon[n, ws];
      If[Simplify[bg - pred] =!= 0, allmatch = False];
      rel = If[bg == 0, Abs[N[bg - pred]], Abs[N[(bg - pred)/bg]]];
      maxerr = Max[maxerr, rel];
      If[Ordering[Abs[ws]][[1]] != 2, w2min = False];
      ],
     {fw, fws}];
   Print[n, " | ", Length[fws], " | ", allmatch, " | ", w2min, " | ", N[maxerr]];
   ],
  {n, {4, 5, 6, 7}}]

Print[];
Print["=== Spot-check explicit values (ascending positive) ==="];
Do[Module[{n, fw, ks, ws, bg, pred},
   n = nf[[1]]; fw = nf[[2]];
   {ks, ws} = mk[n, fw];
   bg = BGAmplitude[ks, ws, 1]; pred = canon[n, ws];
   Print["n=", n, " fw=", fw, "  A=", bg, "  pred=", pred,
     "  match=", Simplify[bg - pred] === 0]],
  {nf, {{4, {3/2, 5/2}}, {5, {3/2, 2, 5/2}}, {6, {1, 3/2, 2, 5/2}},
        {7, {1, 3/2, 2, 5/2, 3}}}}]
