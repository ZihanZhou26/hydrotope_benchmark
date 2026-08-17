Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* candidate formula. active = index of minus leg whose square is used. *)
qS[ws_, S_] := Total[ws[[#]]^2 & /@ S];   (* sum of squares over set S *)

(* sum over subsets S of plus legs {3..n} with omega_active^2 > q_S *)
Aconj[ws_, active_] := Module[{n = Length[ws], plus, x, terms},
  plus = Range[3, n];
  x = ws[[active]]^2;
  terms = 0;
  Do[If[x > qS[ws, S],
     terms += (-1)^(Length[S] + 1) (x - qS[ws, S])^(n - 3)],
   {S, Subsets[plus]}];
  2^(n - 1) ws[[1]] ws[[2]] terms];

(* use the minus leg with the SMALLER square as active *)
activeMin[ws_] := If[ws[[1]]^2 <= ws[[2]]^2, 1, 2];

test[n_, freeW_] := Module[{ws, A, c1, c2, cm},
  ws = genPt[n, freeW]; A = ampR[ws];
  If[A === Indeterminate, Return[Nothing]];
  c1 = Aconj[ws, 1]; c2 = Aconj[ws, 2]; cm = Aconj[ws, activeMin[ws]];
  <|"w" -> ws, "A" -> A, "useLeg1" -> (c1 - A), "useLeg2" -> (c2 - A),
    "useMin" -> (cm - A), "w1sq" -> ws[[1]]^2, "w2sq" -> ws[[2]]^2|>];

(* ---- n=5 sweep via MakeKinematics (w2 free, w1 solved) ---- *)
Print["=== n=5, MakeKinematics points (w2 free) ==="];
res5 = {};
Do[Module[{r}, r = test[5, fw]; If[r =!= Nothing, AppendTo[res5, r]]],
  {fw, {{1,4,9},{3,4,9},{5,4,9},{7,4,9},{10,4,9},{12,4,9},{2,5,11},{6,5,11},
        {1,2,3},{4,2,3},{8,3,5},{1,7,13},{20,3,4},{2,2,2}}}];
Print["count: ", Length[res5]];
Print["max |useLeg2 residual|: ", Max[Abs[#["useLeg2"]] & /@ res5]];
Print["max |useMin  residual|: ", Max[Abs[#["useMin"]] & /@ res5]];

(* ---- n=5 with leg 1 SMALL: solve legs (2,5), free w1,w3,w4 ---- *)
Print["\n=== n=5, leg-1 SMALL (MakeKinAB solve legs 2,5) ==="];
MakeKinAB[n_, a_, b_, vals_] := Module[{s = sig[n], others, A, B, wa, wb, w},
  others = Complement[Range[n], {a, b}];
  A = Total[vals /@ others];
  B = -Total[(s[[#]]*vals[#]^2) & /@ others];
  wb = -(A + B/A)/2; wa = -(A - B/A)/2;
  w = Table[Which[i == a, wa, i == b, wb, True, vals[i]], {i, n}]; w];
Do[Module[{ws, A, c1, c2, cm},
   ws = MakeKinAB[5, 2, 5, <|1 -> w1v, 3 -> w3v, 4 -> w4v|>];
   A = ampR[ws]; If[A === Indeterminate, Continue[]];
   c1 = Aconj[ws, 1]; c2 = Aconj[ws, 2]; cm = Aconj[ws, activeMin[ws]];
   Print["w=", ws, " w1^2=", N[ws[[1]]^2], " w2^2=", N[ws[[2]]^2],
     " | resid leg1=", c1 - A, " leg2=", c2 - A, " min=", cm - A]],
  {w1v, {1, 2}}, {w3v, {5, 9}}, {w4v, {11, 13}}];
