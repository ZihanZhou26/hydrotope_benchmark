(* ============================================================ *)
(*  FINAL VERIFICATION: closed-form A_n vs Berends-Giele         *)
(*  two-minus sector  sigma = (-1,-1,+1,...,+1),  g = 1          *)
(*  (BGAmplitude is the slow part, so it is called only on one    *)
(*   representative per distinct chamber, plus a random stress.)  *)
(* ============================================================ *)
Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

qS[ws_, S_] := Total[ws[[#]]^2 & /@ S];
activeSet[ws_] := Module[{x = ws[[2]]^2}, Select[Subsets[Range[3, Length[ws]]], x > qS[ws, #] &]];
Aformula[ws_] := Module[{n = Length[ws], x = ws[[2]]^2},
  -I*2^(n - 1)*ws[[1]]*ws[[2]]*Total[(-1)^(Length[#] + 1) (x - qS[ws, #])^(n - 3) & /@ activeSet[ws]]];
ampBG[ws_] := BGAmplitude[kvec[ws], ws, gVal];

(* ===== n = 4 : exact symbolic d->0 limit of BG ===== *)
Print["===============  n = 4  (exact symbolic limit of BG = formula)  ==============="];
Do[Module[{a, b, ws, d, w4, w1, lim, form},
   {a, b} = ab; ws = {-b, a, b, -a}; form = Aformula[ws];
   w4 = -a + d; w1 = -(a + b + w4);
   lim = Limit[BGAmplitude[sig[4]*{w1, a, b, w4}^2, {w1, a, b, w4}, gVal], d -> 0];
   Print["  w=", ws, "  A_formula=", form, "  lim BG=", lim, "  match=", Simplify[lim - form] == 0]],
  {ab, {{1, 3}, {2, 5}, {3, 7}, {5, 2}, {7, 3}}}];

(* ===== n = 5,6,7 : one representative per distinct chamber ===== *)
Do[Module[{plus, cand, byCham, reps, ok},
  Print["\n===============  n = ", n, "  : distinct chambers  ==============="];
  plus = Table[2 j + 3, {j, 1, n - 3}];
  cand = Table[genPt[n, Join[{w2}, plus]], {w2, Range[1, 80]}];
  cand = Select[cand, (kvec[#] // Total) == 0 &];        (* on-shell guard *)
  byCham = GatherBy[cand, activeSet];                    (* group by chamber (cheap) *)
  reps = First /@ byCham;                                (* one per chamber *)
  ok = True;
  Print["  distinct chambers on this 1-parameter family: ", Length[reps]];
  Do[Module[{A}, A = ampBG[ws];
     If[! NumericQ[A], Continue[]];
     If[Aformula[ws] =!= A, ok = False;
        Print["   MISMATCH at ", ws]]], {ws, reps}];
  Print["  active-set sizes covered: ", Sort[Length /@ (activeSet /@ reps)]];
  Print["  >>> all representatives match BGAmplitude exactly: ", ok];
  ], {n, {5, 6, 7}}];

(* ===== random stress (modest, sizes tuned so n=7 finishes) ===== *)
Print["\n===============  RANDOM STRESS TEST  ==============="];
SeedRandom[2024];
Do[Module[{n = pair[[1]], npts = pair[[2]], bad = 0, tot = 0, ch = {}},
  Do[Module[{fw, ws, A},
    fw = Table[RandomInteger[{1, 18}] + RandomChoice[{0, 1/2, 1/3}], {n - 2}];
    ws = genPt[n, fw]; A = ampBG[ws];
    If[! NumericQ[A], Continue[]]; tot++; AppendTo[ch, activeSet[ws]];
    If[Aformula[ws] =!= A, bad++]], {npts}];
  Print["  n=", n, ":  ", tot, " on-shell pts,  ", Length[Union[ch]],
    " distinct chambers,  mismatches = ", bad]],
 {pair, {{5, 80}, {6, 40}, {7, 8}}}];
Print["\nDONE."];
