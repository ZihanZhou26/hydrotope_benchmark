Get["codex_work/bg_core.wl"];

Clear[x, y, z];

Compute[sample_] := Module[{w5, w1, ws, ks, amp, oldMag},
  Clear[mag];
  mag[expr_] := Module[{v = N[expr /. {x -> sample[[1]], y -> sample[[2]], z -> sample[[3]]}, 80]},
    If[TrueQ[v >= 0], expr, -expr]];
  w5 = -((x + y) (x + z))/(x + y + z);
  w1 = -(x + y + z + w5);
  ws = {w1, x, y, z, w5};
  ks = {-w1^2, -x^2, y^2, z^2, w5^2};
  amp = Factor[Simplify[BGAmplitude[ks, ws, 1]/I]];
  Print["sample=", sample, " wsSample=", Simplify[ws /. {x -> sample[[1]], y -> sample[[2]], z -> sample[[3]]}]];
  Print[InputForm[amp]];
  Print["check=", Simplify[amp /. {x -> sample[[1]], y -> sample[[2]], z -> sample[[3]]}]];
]

Do[Compute[s], {s, {
  {2, 5/2, 3},
  {5, 1, 2},
  {-1, 2, 5},
  {1, -2, 5},
  {1, 2, -5},
  {-5, 1, 2},
  {5, -1, 2},
  {5, 1, -2},
  {3, 4, -10},
  {3, -4, -10}
}}]
