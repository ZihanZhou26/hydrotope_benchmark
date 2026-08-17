Get["BGcore.m"];
gVal = 1;
n = 6;
sigmas = {-1, -1, 1, 1, 1, 1};
subsetsList = Select[Subsets[Range[n], {1, n - 1}], MemberQ[#, 1] &];
chamberSig[ks_] := Sign[Map[Total[ks[[#]]] &, subsetsList]];

SeedRandom[7777];
data = {};
cnt = 0; tries = 0;
While[cnt < 700 && tries < 6000,
  tries++;
  Module[{fw, ks, ws, sig, amp, P6, w1, w2},
   fw = Table[RandomInteger[{1, 30}]/RandomInteger[{1, 5}], {n - 2}];
   {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
   sig = chamberSig[ks];
   If[MemberQ[sig, 0], Continue[]];
   amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
   If[amp === $Failed || ! FreeQ[amp, Indeterminate] || ! FreeQ[amp, ComplexInfinity] || ! FreeQ[amp, DirectedInfinity], Continue[]];
   P6 = amp/(-I);
   w1 = ws[[1]]; w2 = ws[[2]];
   AppendTo[data, {sig, fw, w1, w2, ws, P6}];
   cnt++;
  ]];
Print["collected ", Length[data], " pts in ", tries, " tries"];
Export["n6_data.m", data];
Print["saved n6_data.m"];
groups = GatherBy[data, First];
Print["distinct chambers: ", Length[groups], "  sizes: ", Sort[Length /@ groups, Greater]];
