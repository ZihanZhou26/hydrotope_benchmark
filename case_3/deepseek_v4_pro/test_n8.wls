(* Test n=8 with simple kinematics *)
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

formula[n_, ws_] := I * 2^(n-1) * ws[[1]] * ws[[2]]^(2n-5);

(* For n=8, use integers to keep it rational and relatively fast *)
n = 8;
fw = {1, 2, 3, 4, 5, 6}; (* w2=1, w3..w7 = 2..6 *)

sigmas = twoMinusSigma[n];
{ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
Print["ws = ", N[ws, 8]];
Print["Computing BG amplitude..."];
amp = BGAmplitude[ks, ws, gVal];
pred = formula[n, ws];
Print["A8 = ", N[amp, 16]];
Print["predicted = ", N[pred, 16]];
Print["match = ", FullSimplify[amp - pred] === 0];
