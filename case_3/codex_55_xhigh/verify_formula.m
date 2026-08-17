(* Verification harness for the two-minus closed form.  Run from this
   directory with:

     wolframscript -file verify_formula.m

   It imports only the definition part of ../OnShellBG.m and then compares
   the closed form below against BGAmplitude on exact rational kinematics. *)

here = DirectoryName[$InputFileName];
source = FileNameJoin[{here, "..", "OnShellBG.m"}];

defs = First @ StringSplit[
    Import[source, "Text"],
    "(* ================================================================ *)\n(*  VI. TESTS"
];
ToExpression[defs];

Clear[FiniteDifferenceG, ClosedTwoMinusA];

FiniteDifferenceG[U_, xs_List] := Module[{m, below, r},
  m = Length[xs] - 1;
  below = Select[Sort[xs], # < U &];
  r = Min[m, Length[below]];
  Total[
    Table[
      (-1)^Length[S] (U - Total[S])^m,
      {S, Subsets[below[[1 ;; r]]]}
    ]
  ]
]

ClosedTwoMinusA[ws_List, sigmas_List, g_] := Module[
  {n, neg, pos, soft, hard},
  n = Length[ws];
  neg = Pick[ws, sigmas, -1];
  pos = Pick[ws, sigmas, 1];

  If[neg[[1]]^2 <= neg[[2]]^2,
    soft = neg[[1]]; hard = neg[[2]],
    soft = neg[[2]]; hard = neg[[1]]
  ];

  Simplify[
    I 2^(n - 1) hard soft
      FiniteDifferenceG[soft^2, pos^2] / g^(n - 3)
  ]
]

cases = {
  {5, {2, 3, 5}},
  {5, {-3, 1, 12}},
  {5, {2, -3, 10}},
  {5, {4, 1, 8}},
  {5, {8, 1, 4}},
  {5, {1/3, 2, 9}},
  {5, {2, 7, 11}},

  {6, {2, 3, 5, 7}},
  {6, {1, 4, 9, 16}},
  {6, {-3, 1, 5, 20}},
  {6, {-3, 1, 12, 20}},
  {6, {4, 1, 8, 10}},
  {6, {8, 1, 4, 10}},
  {6, {20, 1, 4, 8}},
  {6, {2, -3, 10, 11}},
  {6, {-10, 1, 2, 30}},
  {6, {-5, 1, 2, 20}},

  {7, {2, 3, 5, 7, 11}},
  {7, {1, 4, 9, 16, 25}},
  {7, {-3, 1, 5, 20, 21}}
};

Do[
  n = tc[[1]];
  free = tc[[2]];
  sigmas = Join[{-1, -1}, Table[1, n - 2]];
  {ks, ws} = MakeKinematics[n, free, sigmas, 1];
  bg = Simplify[BGAmplitude[ks, ws, 1]];
  closed = ClosedTwoMinusA[ws, sigmas, 1];
  diff = Simplify[bg - closed];

  Print[
    "n=", n,
    " free=", free,
    " ws=", ws,
    " BG=", bg,
    " closed=", closed,
    " diff=", diff
  ],
  {tc, cases}
]

Print["n=4 note: exact two-minus kinematics force a zero subcurrent in the",
  " supplied BG recursion, so raw BGAmplitude returns Indeterminate there.",
  " The formula gives the finite chamber continuation; e.g. ",
  "ws={-3,2,3,-2} gives A4=", 8 I (-3) 2 (2^2), "."];
