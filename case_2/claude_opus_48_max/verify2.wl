Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

qS[ws_, S_] := Total[ws[[#]]^2 & /@ S];
Aconj[ws_, active_] := Module[{n = Length[ws], plus, x, terms},
  plus = Range[3, n]; x = ws[[active]]^2; terms = 0;
  Do[If[x > qS[ws, S],
     terms += (-1)^(Length[S] + 1) (x - qS[ws, S])^(n - 3)],
   {S, Subsets[plus]}];
  2^(n - 1) ws[[1]] ws[[2]] terms];

MakeKinAB[n_, a_, b_, vals_] := Module[{s = sig[n], others, A, B, wa, wb, w},
  others = Complement[Range[n], {a, b}];
  A = Total[vals /@ others]; B = -Total[(s[[#]]*vals[#]^2) & /@ others];
  wb = -(A + B/A)/2; wa = -(A - B/A)/2;
  Table[Which[i == a, wa, i == b, wb, True, vals[i]], {i, n}]];

SeedRandom[7];
checkN[n_, npts_] := Module[{res = {}, nbad1 = 0, nbad2 = 0, nbadm = 0, sigs = {}},
  Do[Module[{fw, ws, A, c1, c2, am},
    fw = Table[RandomInteger[{1, 14}] + RandomChoice[{0, 1/2, 1/3}], {n - 2}];
    ws = genPt[n, fw]; A = ampR[ws];
    If[A === Indeterminate, Continue[]];
    c1 = Aconj[ws, 1]; c2 = Aconj[ws, 2];
    am = Aconj[ws, If[ws[[1]]^2 <= ws[[2]]^2, 1, 2]];
    If[c1 =!= A, nbad1++]; If[c2 =!= A, nbad2++]; If[am =!= A, nbadm++];
    AppendTo[sigs, chamberSig[ws]];
    ], {npts}];
  Print["n=", n, ": tested ", Length[sigs], " pts, ", Length[Union[sigs]],
    " distinct chambers"];
  Print["   #mismatch  useLeg1=", nbad1, "  useLeg2=", nbad2, "  useMin=", nbadm];
  ];

checkN[6, 40];
checkN[7, 30];

(* leg-1-small points for n=6,7 *)
Print["\n--- leg-1 small (n=6,7) ---"];
Do[Module[{ws, A, c1, c2},
   ws = MakeKinAB[6, 2, 6, <|1 -> 1, 3 -> w3, 4 -> w4, 5 -> w5|>];
   A = ampR[ws]; If[A === Indeterminate, Continue[]];
   c1 = Aconj[ws, 1]; c2 = Aconj[ws, 2];
   Print["n6 w1^2=", N[ws[[1]]^2], " w2^2=", N[ws[[2]]^2],
     " resid l1=", c1 - A, " l2=", c2 - A]],
  {w3, {5, 9}}, {w4, {7, 11}}, {w5, {13}}];
Do[Module[{ws, A, c1, c2},
   ws = MakeKinAB[7, 2, 7, <|1 -> 1, 3 -> w3, 4 -> 5, 5 -> 8, 6 -> w6|>];
   A = ampR[ws]; If[A === Indeterminate, Continue[]];
   c1 = Aconj[ws, 1]; c2 = Aconj[ws, 2];
   Print["n7 w1^2=", N[ws[[1]]^2], " w2^2=", N[ws[[2]]^2],
     " resid l1=", c1 - A, " l2=", c2 - A]],
  {w3, {9, 11}}, {w6, {13, 17}}];
