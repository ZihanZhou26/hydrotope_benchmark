(* args: n seed count outfile *)
Get["BGcore.m"];
args = Rest[$ScriptCommandLine];
n = ToExpression[args[[1]]];
seed = ToExpression[args[[2]]];
count = ToExpression[args[[3]]];
outfile = args[[4]];
gVal = 1;
sigmas = Join[{-1, -1}, Table[1, n - 2]];
SeedRandom[seed];
raw = {};
cnt = 0; tries = 0;
While[cnt < count && tries < count*40,
  tries++;
  Module[{fw, ks, ws, amp},
   fw = Table[RandomChoice[{-1, -1, 1, 1, 1}]*RandomInteger[{1, 60}]/RandomInteger[{1, 7}], {n - 2}];
   {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
   If[MemberQ[ws, 0], Continue[]];
   amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
   If[amp === $Failed || ! FreeQ[amp, Indeterminate] || ! FreeQ[amp, ComplexInfinity] || ! FreeQ[amp, DirectedInfinity], Continue[]];
   AppendTo[raw, {ws, amp/(-I)}];
   cnt++;
  ]];
Export[outfile, raw];
Print["seed ", seed, ": ", Length[raw], " pts -> ", outfile];
