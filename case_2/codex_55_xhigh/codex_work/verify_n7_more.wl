Get["codex_work/bg_core.wl"];

TruncPower[x_, p_] := If[x > 0, x^p, 0]
TwoMinusFormula[ws_List] := Module[{n = Length[ws], r, qs, p},
  r = Min[ws[[1]]^2, ws[[2]]^2];
  qs = ws[[3 ;;]]^2;
  p = n - 3;
  I*2^(n - 1)*ws[[1]]*ws[[2]]*
    Total[(-1)^Length[#] TruncPower[r - Total[qs[[#]]], p] & /@
      Subsets[Range[Length[qs]]]]
]

cases = {
  {7, {5, 1, 2, 3, 9/2}},
  {7, {4, 1, 3/2, 5/2, 7/2}},
  {7, {-2, 1, 5/2, 4, 6}}
};

Do[
  {ks, ws} = TwoMinusKinematics[tc[[2]]];
  bg = Simplify[BGAmplitude[ks, ws, 1]];
  ff = Simplify[TwoMinusFormula[ws]];
  Print[InputForm[{tc[[1]], tc[[2]], ws, Simplify[bg/I], Simplify[ff/I], Simplify[(bg - ff)/I]}]],
  {tc, cases}]
