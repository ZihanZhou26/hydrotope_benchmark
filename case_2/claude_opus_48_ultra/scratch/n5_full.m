Get["BGcore.m"];
gVal = 1;
n = 5;
sigmas = {-1, -1, 1, 1, 1};
subsetsList = Select[Subsets[Range[n], {1, n - 1}], MemberQ[#, 1] &];
chamberSig[ks_] := Sign[Map[Total[ks[[#]]] &, subsetsList]];

(* free magnitudes A,B,C = w2^2,w3^2,w4^2 ; R is deg-2 homog poly in A,B,C *)
monsR = Flatten[Table[A^i*B^j*CC^(2 - i - j), {i, 0, 2}, {j, 0, 2 - i}]];

SeedRandom[31415];
data = {};
cnt = 0; tries = 0;
While[cnt < 2000 && tries < 30000,
  tries++;
  Module[{fw, ks, ws, sig, amp, P5, w1, w2, R},
   fw = Table[RandomChoice[{-1, 1}]*RandomInteger[{1, 25}]/RandomInteger[{1, 5}], {n - 2}];
   {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
   sig = chamberSig[ks];
   If[MemberQ[sig, 0], Continue[]];
   amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
   If[amp === $Failed || ! FreeQ[amp, Indeterminate] || ! FreeQ[amp, ComplexInfinity] || ! FreeQ[amp, DirectedInfinity], Continue[]];
   P5 = amp/(-I);
   w1 = ws[[1]]; w2 = ws[[2]];
   If[w1 == 0 || w2 == 0, Continue[]];
   R = P5/(-16*w1*w2);
   AppendTo[data, {sig, ws, R}];
   cnt++;
  ]];
Print["collected ", Length[data]];
groups = GatherBy[data, First];
Print["distinct chamber signatures: ", Length[groups]];

fitR[grp_] := Module[{pts, M, rhs, k = Length[monsR], sol, ok},
  pts = grp;
  If[Length[pts] < k + 3, Return[{"few", Length[pts], None}]];
  M = Table[monsR /. {A -> pts[[r, 2, 2]]^2, B -> pts[[r, 2, 3]]^2, CC -> pts[[r, 2, 4]]^2}, {r, Length[pts]}];
  rhs = pts[[All, 3]];
  sol = Quiet@Check[LinearSolve[M[[1 ;; k]], rhs[[1 ;; k]]], $Failed];
  If[sol === $Failed, Return[{"sing", Length[pts], None}]];
  ok = AllTrue[Range[Length[pts]], (monsR . sol /. {A -> pts[[#, 2, 2]]^2, B -> pts[[#, 2, 3]]^2, CC -> pts[[#, 2, 4]]^2}) == rhs[[#]] &];
  {If[ok, "EXACT", "INCONSIST"], Length[pts], monsR . sol}];

sorted = SortBy[groups, -Length[#] &];
Print["===== chambers (R = P5/(-16 w1 w2), in A=w2^2,B=w3^2,CC=w4^2) ====="];
Do[Module[{grp = sorted[[gi]], res, ws0, m, ord},
   res = fitR[grp];
   ws0 = grp[[1, 2]]; m = ws0^2; ord = Ordering[m];
   Print["chamber ", gi, "  (", res[[2]], " pts)  status=", res[[1]]];
   Print["   R = ", res[[3]] // Factor];
   Print["   rep all w  = ", N[ws0, 6]];
   Print["   rep m=w^2  = ", N[m, 6]];
   Print["   ascending-m leg order = ", ord, "   (legs 1,2 minus; 3,4,5 plus)"];
  ], {gi, Length[sorted]}];
Export["n5_chambers.m", {sorted, monsR}];
