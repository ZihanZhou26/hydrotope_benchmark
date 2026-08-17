Get["codex_work/bg_core.wl"];

Clear[BGCubicCurrent];
BGCubicCurrent[{i_Integer}] := 1
BGCubicCurrent[S_List] := BGCubicCurrent[S] = Module[
  {\[Omega]S, kS, result = 0, m = 2},
  \[Omega]S = Total[$wList[[S]]];
  kS = Total[$kList[[S]]];
  Do[Module[{sMoms, sOmegas, vMoms, vOmegas},
    sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, -kS];
    vOmegas = Prepend[sOmegas, -\[Omega]S];
    result += Vertex[m + 1, vMoms, vOmegas]*
      Product[BGCubicCurrent[part[[j]]], {j, m}]],
    {part, SetPartitions[S, m]}];
  result*Propagator[\[Omega]S, kS, $gVal]]

BGCubicAmplitude[momenta_List, omegas_List, g_] := Module[
  {n = Length[momenta], rest, result = 0, m = 2},
  $kList = momenta; $wList = omegas; $gVal = g;
  DownValues[BGCubicCurrent] =
    Select[DownValues[BGCubicCurrent], !FreeQ[#, Pattern | Blank] &];
  rest = Range[2, n];
  Do[Module[{sMoms, sOmegas, vMoms, vOmegas},
    sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, $kList[[1]]];
    vOmegas = Prepend[sOmegas, $wList[[1]]];
    result += Vertex[m + 1, vMoms, vOmegas]*
      Product[BGCubicCurrent[part[[j]]], {j, m}]],
    {part, SetPartitions[rest, m]}];
  result]

Do[
  {ks, ws} = TwoMinusKinematics[free];
  full = Simplify[BGAmplitude[ks, ws, 1]];
  cubic = Simplify[BGCubicAmplitude[ks, ws, 1]];
  Print["free=", free, " full/I=", Simplify[full/I], " cubic/I=", Simplify[cubic/I], " diff=", Simplify[(full - cubic)/I]],
  {free, {{2, 5/2, 3}, {1, 2, 5}, {5, 1, 2}, {3/2, 2, 5/2, 3}}}]
