Get["/home/zihanz/waterhedron_benchmark_blind/case_1/codex_54_xhigh/bg_core.wl"];

Clear[PosPart, TwoMinusClosedForm];

PosPart[x_] := Max[0, x]

TwoMinusClosedForm[ws_List] := Module[
  {n = Length[ws], x, us},
  x = ws[[2]]^2;
  us = ws[[3 ;; n - 1]]^2;
  I*2^(n - 1)*ws[[1]]*ws[[2]]*
    Sum[
      (-1)^Length[S]*PosPart[x - Total[us[[S]]]]^(n - 3),
      {S, Subsets[Range[Length[us]]]}
    ]
]

gVal = 1;

Print["n >= 5 exact checks"];
Print["=================="];

testCases = {
  {5, {{1, 2, 3}, {2, 1, 3}, {5, 4, 1}, {3/2, 5/2, 7/2}, {5/2, 7/2, 3/2}}},
  {6, {{1, 3/2, 2, 5/2}, {5/2, 2, 3, 7/2}, {4, 3, 2, 1}, {7/2, 5/2, 3/2, 1}}},
  {7, {{1, 3/2, 2, 5/2, 3}, {4, 3, 5/2, 2, 1}, {7/2, 5/2, 2, 3/2, 1}, {5/2, 7/2, 3/2, 9/4, 3}}}
};

Do[
  n = tc[[1]];
  sig = TwoMinusSigmas[n];
  Print["-- n = ", n, " --"];
  Do[
    {ks, ws} = MakeKinematics[n, fw, sig, gVal];
    amp = Together[BGAmplitude[ks, ws, gVal]];
    cf = Together[TwoMinusClosedForm[ws]];
    diff = Together[amp - cf];
    rel = If[amp === 0, 0, N[Abs[diff/amp], 30]];
    Print["freeW = ", fw];
    Print["  ws   = ", ws];
    Print["  BG   = ", amp];
    Print["  CF   = ", cf];
    Print["  diff = ", diff];
    Print["  rel  = ", rel];
    ,
    {fw, tc[[2]]}
  ];
  Print[""];
  ,
  {tc, testCases}
];

Print["n = 4 finite limit from the same formula"];
Print["======================================="];
Do[
  n = 4;
  sig = TwoMinusSigmas[n];
  {ks, ws} = MakeKinematics[n, fw, sig, gVal];
  cf = Together[TwoMinusClosedForm[ws]];
  Print["freeW = ", fw];
  Print["  ws      = ", ws];
  Print["  BG code = Indeterminate (exact zero-momentum channels)"];
  Print["  CF      = ", cf];
  ,
  {fw, {{2, 3}, {3, 2}, {5/2, 7/2}}}
]
