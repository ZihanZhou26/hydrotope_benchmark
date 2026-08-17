(* Compare BG terms for two different kinematic orderings *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 1]];

analyzeCase[fw_] := Module[{n, sigmas, ks, ws, totalResult},
  n = Length[fw] + 2;
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  
  $kList = ks; $wList = ws; $gVal = gVal;
  DownValues[BGCurrent] = Select[DownValues[BGCurrent], !FreeQ[#, Pattern | Blank] &];
  rest = Range[2, n];
  
  totalResult = 0;
  Do[
    Do[
      Module[{sMoms, sOmegas, vMoms, vOmegas, term},
      sMoms = Table[Total[$kList[[part[[j]]]]], {j, m}];
      sOmegas = Table[Total[$wList[[part[[j]]]]], {j, m}];
      vMoms = Prepend[sMoms, $kList[[1]]];
      vOmegas = Prepend[sOmegas, $wList[[1]]];
      term = Vertex[m + 1, vMoms, vOmegas] * 
             Product[BGCurrent[part[[j]]], {j, m}];
      totalResult += term;
      ];
      ,
      {part, SetPartitions[rest, m]}
    ],
    {m, 2, n - 1}
  ];
  
  Print["fw=", fw, " ws=", ws, " A=", N[totalResult, 10]];
  Print["Formula prediction (16i w1 w2^5)=", N[16 I * ws[[1]] * ws[[2]]^5, 10]];
  Print["Match=", Simplify[totalResult - 16 I * ws[[1]] * ws[[2]]^5] === 0];
];

(* Case where w2 < all plus-sigma *)
analyzeCase[{1, 2, 3}];
(* Case where w2 > all plus-sigma *)
analyzeCase[{5, 1, 2}];
(* Mixed case *)
analyzeCase[{3, 2, 5}];
(* Degenerate case *)
analyzeCase[{2, 1, 1}];
