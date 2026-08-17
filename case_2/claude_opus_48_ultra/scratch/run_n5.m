Get["BGcore.m"];
Get["labelseq.m"];
gVal = 1; n = 5; sigmas = {-1, -1, 1, 1, 1};

(* Wide sampling incl. negative & large freqs to catch all chambers (e.g. minus@{4,5}) *)
SeedRandom[999];
raw = {};
cnt = 0; tries = 0;
While[cnt < 4000 && tries < 60000,
  tries++;
  Module[{fw, ks, ws, amp},
   fw = Table[RandomChoice[{-1, -1, 1, 1, 1}]*RandomInteger[{1, 40}]/RandomInteger[{1, 6}], {n - 2}];
   {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
   If[MemberQ[ws, 0], Continue[]];
   amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
   If[amp === $Failed || ! FreeQ[amp, Indeterminate] || ! FreeQ[amp, ComplexInfinity] || ! FreeQ[amp, DirectedInfinity], Continue[]];
   AppendTo[raw, {ws, amp/(-I)}];
   cnt++;
  ]];
Print["collected ", Length[raw], " pts"];
res = analyzeData[n, raw];
