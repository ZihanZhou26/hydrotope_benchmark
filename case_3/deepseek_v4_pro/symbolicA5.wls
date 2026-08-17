(* Derive A5 symbolically *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

(* For n=5 two-minus, compute kinematics explicitly *)
n = 5;
sigmas = twoMinusSigma[n];

(* Let w2, w3, w4 be free. Compute ws and ks symbolically *)
Block[{w2, w3, w4, S, S2, sumFree, delta, w1, w5, ws, ks},
  S = w3 + w4;
  S2 = w3^2 + w4^2;
  sumFree = w2 + S;
  delta = (S^2 - S2)/(2*sumFree);
  w5 = -w2 - delta;
  w1 = -S + delta;
  
  ws = {w1, w2, w3, w4, w5};
  ks = sigmas * ws^2 / gVal;
  
  Print["ws = ", Simplify[ws]];
  Print["ks = ", Simplify[ks]];
  
  (* Try to compute amplitude *)
  amp = BGAmplitude[ks, ws, gVal];
  Print["A5 = ", Simplify[amp]];
  Print["A5 factorized = ", Factor[amp]];
]
