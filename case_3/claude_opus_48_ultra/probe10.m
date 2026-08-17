Get["/home/zihanz/waterhedron_benchmark_blind/case_3/claude_opus_48_ultra/BGcore.m"];
Clear[mag];
mag[k_] := Module[{v = k /. $signRules},
  If[NumericQ[v] && v != 0, Sign[v]*k, Print["WARN sign ", InputForm@k]; Abs[k]]];
twoMinus[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* For a numeric n=5 free pt, compute sign-frozen symbolic A_5(v1,v2,v3),
   then read off the omega-monomial by dividing out building blocks:
     v1<->w2, v2<->w3, v3<->w4, Q<->-w1*S, (v1+v2)(v1+v3)<->-w5*S, S
   Returns {freePt, sortedSignPattern, exponents (b,c,d,a,e), coeff, check} *)
Qpoly = v1 v2 + v2^2 + v1 v3 + v2 v3 + v3^2;
Spoly = v1 + v2 + v3;
W5num = (v1 + v2)(v1 + v3);  (* = -w5*S *)

reduceChamber[freePt_] := Module[
  {sig, ks, ws, amp, num, den, expo, residual, w1n, w5n},
  sig = twoMinus[5];
  {ks, ws} = MakeKinematics[5, {v1, v2, v3}, sig, 1];
  $signRules = Thread[{v1, v2, v3} -> freePt];
  amp = Together[BGAmplitude[ks, ws, 1]];
  (* try: amp = coeff * I * v1^b v2^c v3^d Q^a W5num^e / S^(a+e) *)
  (* Determine exponents via polynomial valuation. *)
  num = Numerator[amp / I]; den = Denominator[amp / I];
  expo = <|
    "b(w2,v1)" -> Exponent[num, v1] - Exponent[num /. v1 -> 1, v1] (*placeholder*)
  |>;
  (* Robust: divide out factors greedily *)
  Module[{f = amp/I, a = 0, e = 0, b = 0, c = 0, d = 0, sPow = 0, g0},
    (* count S power in denominator *)
    sPow = Exponent[Denominator[Factor[f]], Spoly];
    (* Use PolynomialReduce-free approach: factor fully *)
    g0 = Factor[f];
    {g0, freePt, ws /. $signRules,
     "Avalue" -> (amp /. $signRules)}
  ]
];

pts = {
  {3/2, 2, 5/2}, {1, 5, 2}, {2, 3, 7}, {1/1000, 1, 1},
  {1000, 1, 1}, {3, 1, 1}, {7/3, 11/5, 13/7}, {-3/2, 2, 5/2},
  {12/5, 11/5, 2}, {5, 4, 1}, {1, 1, 5}, {2, 1, 10},
  {1, 10, 1}, {10, 1, 1}, {4, 5, 1}, {1, 2, 3}, {3, 2, 1},
  {-1, 2, 3}, {2, -1, 3}, {2, 3, -1}, {-5, 2, 3}, {1/2, 3, 1/3}
};

Do[
  Module[{r = reduceChamber[p]},
    Print["free=", p];
    Print["   w = ", r[[3]] // N];
    Print["   A/I factored = ", r[[1]]];
    Print["   A = ", r[[4, 2]], "\n"];
  ], {p, pts}];

Print["DONE probe10"];
