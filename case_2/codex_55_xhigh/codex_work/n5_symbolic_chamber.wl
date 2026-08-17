Get["codex_work/bg_core.wl"];

Clear[x, y, z, mag];
sampleRules = {x -> 2, y -> 5/2, z -> 3};
mag[expr_] := Module[{v = N[expr /. sampleRules, 80]},
  If[TrueQ[v >= 0], expr, -expr]]

w5 = -((x + y) (x + z))/(x + y + z);
w1 = -(x + y + z + w5);
ws = {w1, x, y, z, w5};
ks = {-w1^2, -x^2, y^2, z^2, w5^2};

amp = Simplify[BGAmplitude[ks, ws, 1]/I];
Print["ws=", InputForm[ws]];
Print["amp=", InputForm[Factor[amp]]];
Print["ampExpanded=", InputForm[Expand[amp]]];
Print["check=", Simplify[amp /. sampleRules]];
