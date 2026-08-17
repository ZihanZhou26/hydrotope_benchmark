(* Analyze individual terms in BG recursion for n=5, two-minus sector *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

n = 5;
sigmas = twoMinusSigma[n];

fw = {1, 2, 3}; (* w2 < all plus *)
{ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];

Print["ws = ", ws];
Print["ks = ", ks];

$kList = ks; $wList = ws; $gVal = gVal;
DownValues[BGCurrent] = Select[DownValues[BGCurrent], !FreeQ[#, Pattern | Blank] &];
rest = Range[2, n];

(* Compute each term individually *)
totalResult = 0;
Do[
  Do[
    Module[{sMoms, sOmegas, vMoms, vOmegas, term, currents},
    sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
    sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
    vMoms = Prepend[sMoms, $kList[[1]]];
    vOmegas = Prepend[sOmegas, $wList[[1]]];
    currents = Table[BGCurrent[part[[j]]], {j, m}];
    term = Vertex[m + 1, vMoms, vOmegas] * Product[currents[[j]], {j, m}];
    totalResult += term;
    Print["m=", m, " part=", part, " vM=", vMoms, " vW=", vOmegas];
    Print["  BGCurrents=", currents];
    Print["  term=", N[term, 10]];
    ];
    ,
    {part, SetPartitions[rest, m]}
  ],
  {m, 2, n - 1}
];

Print["\nTotal amplitude = ", N[totalResult, 20]];
Print["Expected = ", N[BGAmplitude[ks, ws, gVal], 20]];
