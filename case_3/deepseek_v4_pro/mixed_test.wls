(* Compute ratio R for mixed regime: w3 < w2 < w4 *)
(* Fix w3=1, w4=large, vary w2 *)

Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

Do[
  w2 = w2val;
  w3 = 1;
  w4 = 100; (* large, so w3 < w2 < w4 *)
  
  fw = {w2, w3, w4};
  sigmas = twoMinusSigma[5];
  {ks, ws} = MakeKinematics[5, Map[Rationalize, fw], sigmas, gVal];
  If[ks === $Failed, Continue[]];
  amp = BGAmplitude[ks, ws, gVal];
  
  formulaVal = 16 * ws[[1]] * ws[[2]]^5; (* A5/i for formula *)
  actualVal = amp/I;
  ratio = actualVal / formulaVal;
  
  Print["w2=", w2, " w3=1 w4=100:"];
  Print["  ws=", N[ws, 6]];
  Print["  A5/i actual=", N[actualVal, 10], " formula=", N[formulaVal, 10]];
  Print["  ratio=", N[ratio, 10]];
  ,
  {w2val, 2, 10}
]
