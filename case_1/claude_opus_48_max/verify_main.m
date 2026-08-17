(* ================================================================ *)
(*  verify_main.m                                                   *)
(*  Authoritative verification of the closed form                   *)
(*       A_n = 2^(n-1) I w1 w2^(2n-5)                                *)
(*  against the PROVIDED BGAmplitude (exact rational arithmetic),    *)
(*  in the canonical chamber (ascending-positive free frequencies). *)
(*  Run:  wolframscript -file verify_main.m                          *)
(* ================================================================ *)

Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
mk[n_, fw_] := MakeKinematics[n, fw, twoMinusSigma[n], 1];
canon[n_, ws_] := 2^(n - 1) I ws[[1]] ws[[2]]^(2 n - 5);

SeedRandom[7];
ascFree[n_] := Sort@DeleteDuplicates@
   Table[RandomInteger[{1, 9}] + RandomChoice[{0, 1/2, 1/3, 1/4}], {n - 2}];

Print["n | #pts | exact matches | w2 = min|w| | max rel.err"];
Print["--+------+---------------+-------------+------------"];
Do[Module[{npts, fws, ok, w2min, maxerr},
   npts = Switch[n, 5, 30, 6, 18, 7, 8];
   fws = Select[Table[ascFree[n], {4 npts}], Length[#] == n - 2 &];
   fws = Take[fws, Min[npts, Length[fws]]];
   ok = 0; w2min = True; maxerr = 0;
   Do[Module[{ks, ws, bg, pred, rel},
      {ks, ws} = mk[n, fw];
      bg = BGAmplitude[ks, ws, 1];
      pred = canon[n, ws];
      If[Simplify[bg - pred] === 0, ok++];
      rel = Abs[N[(bg - pred)/bg, 30]];
      maxerr = Max[maxerr, rel];
      If[Ordering[Abs[ws]][[1]] != 2, w2min = False]],
     {fw, fws}];
   Print[n, " | ", Length[fws], "   | ", ok, "/", Length[fws],
     "         | ", w2min, "        | ", N[maxerr]]],
  {n, {5, 6, 7}}]

Print[];
Print["Explicit values (ascending positive free frequencies):"];
Do[Module[{n, fw, ks, ws, bg, pred},
   n = nf[[1]]; fw = nf[[2]];
   {ks, ws} = mk[n, fw];
   bg = BGAmplitude[ks, ws, 1]; pred = canon[n, ws];
   Print["  n=", n, "  free=", fw, "  : BG = ", bg,
     " ,  formula = ", pred, " ,  match = ", Simplify[bg - pred] === 0]],
  {nf, {{5, {3/2, 2, 5/2}}, {5, {2, 3, 5}}, {6, {1, 3/2, 2, 5/2}},
        {6, {2, 3, 5, 7}}, {7, {1, 3/2, 2, 5/2, 3}}, {7, {2, 3, 5, 7, 11}}}}]

Print[];
Print["(n=4 is verified separately via the 0/0 symbolic limit: see verify_n4.m)"];
