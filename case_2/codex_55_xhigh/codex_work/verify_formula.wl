Get["codex_work/bg_core.wl"];

Clear[TruncPower, TwoMinusFormula];
TruncPower[x_, p_] := If[x > 0, x^p, 0]
TwoMinusFormula[ws_List] := Module[
  {n = Length[ws], r, qs, p},
  r = Min[ws[[1]]^2, ws[[2]]^2];
  qs = ws[[3 ;;]]^2;
  p = n - 3;
  I*2^(n - 1)*ws[[1]]*ws[[2]]*
    Total[(-1)^Length[#] TruncPower[r - Total[qs[[#]]], p] & /@
      Subsets[Range[Length[qs]]]]
]

cases = {
  {5, {2, 5/2, 3}},
  {5, {5, 1, 2}},
  {5, {-1, 2, 5}},
  {5, {1, -2, 5}},
  {5, {5, 1, -2}},
  {6, {3/2, 2, 5/2, 3}},
  {6, {1, -2, 3, 4}},
  {6, {5, 1, 2, 3}},
  {6, {-1, 2, 5, 7}},
  {7, {3/2, 2, 5/2, 3, 7/2}},
  {7, {1, -2, 3, 4, 5}},
  {7, {5, 1, 2, 3, 4}}
};

Do[
  {ks, ws} = TwoMinusKinematics[tc[[2]]];
  bg = Simplify[BGAmplitude[ks, ws, 1]];
  ff = Simplify[TwoMinusFormula[ws]];
  Print[InputForm[{tc[[1]], tc[[2]], ws, Simplify[bg/I], Simplify[ff/I], Simplify[(bg - ff)/I]}]],
  {tc, cases}]
