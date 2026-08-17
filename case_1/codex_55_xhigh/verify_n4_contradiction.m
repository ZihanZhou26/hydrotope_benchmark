Catch[Block[{Print = (Throw[Null] &)}, Get["../OnShellBG.m"]]];

sig = {-1, -1, 1, 1};

{ks, ws} = MakeKinematics[4, {-x, y}, sig, 1];
amp = BGAmplitude[ks, ws, 1];
pw = FullSimplify[amp, Assumptions -> {x > 0, y > 0}];

Print["symbolic ws = ", FullSimplify[ws, Assumptions -> {x > 0, y > 0}]];
Print["symbolic A4 = ", pw];
Print["difference between open-branch formulas = ", Simplify[8 I x^3 y - 8 I x y^3]];
Print["branch value from symbolic expression at x=1,y=2 = ", pw /. {x -> 1, y -> 2}];
Print["branch value from symbolic expression at x=2,y=1 = ", pw /. {x -> 2, y -> 1}];

{ks12, ws12} = MakeKinematics[4, {-1, 2}, sig, 1];
{ks21, ws21} = MakeKinematics[4, {-2, 1}, sig, 1];

Print["sample x=1,y=2 ws = ", ws12];
Print["direct exact numeric BG at x=1,y=2 = ", Quiet[Simplify[BGAmplitude[ks12, ws12, 1]]]];
Print["sample x=2,y=1 ws = ", ws21];
Print["direct exact numeric BG at x=2,y=1 = ", Quiet[Simplify[BGAmplitude[ks21, ws21, 1]]]];
