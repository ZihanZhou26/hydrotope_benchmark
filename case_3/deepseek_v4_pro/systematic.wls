(* Systematic computation of A5 for all integer triples up to some bound *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeA[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  amp
];

(* Compute A5 for many integer triples (w2,w3,w4) with 1 <= w_i <= 6 *)
(* Also compute what my formula predicts and the ratio *)

formulaPred[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

(* For n=5, formula: 16i * w1 * w2^5 *)

Print["w2,w3,w4  |  w1,w2,w3,w4,w5  |  A5  |  A5/(16i*w1*w2^5)  |  cond(w2<all)"];

maxVal = 6;
Do[
  Do[
    Do[
      fw = {w2, w3, w4};
      {ks, ws} = MakeKinematics[5, {w2, w3, w4}, twoMinusSigma[5], gVal];
      If[ks === $Failed, Continue[]];
      
      amp = BGAmplitude[ks, ws, gVal];
      ampOverI = amp/I;
      
      w1 = ws[[1]];
      w5 = ws[[5]];
      
      formulaVal = 16 * w1 * w2^5;
      ratio = ampOverI / formulaVal;  (* this removes the I factor *)
      
      cond = (w2 < w3) && (w2 < w4);
      
      Print[w2, ",", w3, ",", w4, "  |  ", 
            N[w1,4], ",", N[w2,4], ",", N[w3,4], ",", N[w4,4], ",", N[w5,4],
            "  |  ", N[ampOverI, 8],
            "  |  ", N[ratio, 8],
            "  |  ", cond];
      ,
      {w4, 1, maxVal}
    ],
    {w3, 1, maxVal}
  ],
  {w2, 1, maxVal}
]
