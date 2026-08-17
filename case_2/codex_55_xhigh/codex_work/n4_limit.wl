Get["codex_work/bg_core.wl"];

N4Formula[ws_] := Module[{r = Min[ws[[1]]^2, ws[[2]]^2]},
  I*8*ws[[1]]*ws[[2]]*r]

CheckLimit[ws_, deltaOn3_: True] := Module[{d, ks, amp, lim},
  Clear[d, mag];
  mag[expr_] := Module[{v = N[expr /. d -> 1/100, 80]},
    If[TrueQ[v >= 0], expr, -expr]];
  If[deltaOn3,
    ks = {-ws[[1]]^2, -ws[[2]]^2, ws[[3]]^2 + d, ws[[4]]^2 - d},
    ks = {-ws[[1]]^2, -ws[[2]]^2, ws[[3]]^2 - d, ws[[4]]^2 + d}
  ];
  amp = Simplify[BGAmplitude[ks, ws, 1]/I];
  lim = Limit[amp, d -> 0, Direction -> "FromAbove"];
  Print[InputForm[{ws, amp, lim, Simplify[N4Formula[ws]/I]}]]
]

CheckLimit[{-3, 2, 3, -2}, True];
CheckLimit[{-5, 1, 5, -1}, True];
CheckLimit[{3, -2, -3, 2}, True];
CheckLimit[{-3, 2, -2, 3}, True];
