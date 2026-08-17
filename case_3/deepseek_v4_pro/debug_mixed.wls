(* Debug individual BG terms for mixed ordering *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

n = 5;
sigmas = twoMinusSigma[n];

fw = {2, 1, 3}; (* w3 < w2 < w4 - mixed *)
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
    Print["m=", m, " part=", part, " term=", N[term/I, 10]]; (* strip I *)
    ];
    ,
    {part, SetPartitions[rest, m]}
  ],
  {m, 2, n - 1}
];

Print["\nTotal/I = ", N[totalResult/I, 20]];
Print["16*w1*w2^5 = ", N[16 * ws[[1]] * ws[[2]]^5, 20]];
Print["16*w1*w2*(2*w2^2-1) = ", N[16 * ws[[1]] * ws[[2]] * (2*ws[[2]]^2-1), 20]];
