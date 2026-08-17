SetDirectory[DirectoryName[$InputFileName]];
Get["bg_core.wl"];
Get["two_minus_formula.wl"];

PrintCheck[label_, ws_, bgOverI_, formulaOverI_] := Module[{diff},
  diff = Simplify[bgOverI - formulaOverI];
  Print[InputForm[{label, ws, bgOverI, formulaOverI, diff}]]
]

cases = {
  {"n5-a", {2, 5/2, 3}},
  {"n5-b", {5, 1, 2}},
  {"n5-c", {-1, 2, 5}},
  {"n6-a", {3/2, 2, 5/2, 3}},
  {"n6-b", {1, -2, 3, 4}},
  {"n6-c", {5, 1, 2, 3}},
  {"n7-a", {3/2, 2, 5/2, 3, 7/2}},
  {"n7-b", {1, -2, 3, 4, 5}},
  {"n7-c", {5, 1, 2, 3, 9/2}}
};

Do[
  {ks, ws} = TwoMinusKinematics[case[[2]]];
  bg = Simplify[BGAmplitude[ks, ws, 1]/I];
  formula = Simplify[TwoMinusClosedForm[ws]/I];
  PrintCheck[case[[1]], ws, bg, formula],
  {case, cases}
]

(* n = 4 is a boundary of the real resonant manifold.  The raw BG recursion
   has 0/0 internal zero-momentum currents there, so check the conserved
   momentum split k3 -> k3 + d, k4 -> k4 - d and take d -> 0+. *)
Clear[d, mag];
mag[expr_] := Module[{v = N[expr /. d -> 1/100, 80]},
  If[TrueQ[v >= 0], expr, -expr]]

Do[
  ws = pair;
  ks = {-ws[[1]]^2, -ws[[2]]^2, ws[[3]]^2 + d, ws[[4]]^2 - d};
  bgLimit = Limit[Simplify[BGAmplitude[ks, ws, 1]/I], d -> 0,
    Direction -> "FromAbove"];
  formula = Simplify[TwoMinusClosedForm[ws]/I];
  PrintCheck["n4-limit", ws, bgLimit, formula],
  {pair, {{-3, 2, 3, -2}, {-5, 1, 5, -1}}}
]
