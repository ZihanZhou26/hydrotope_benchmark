<< bg_core.m
Unprotect[mag]; ClearAll[mag];
doN[n_, syms_, refpt_] := Block[{ref, sig, fw, ks, ws, amp, R},
  ref = Thread[syms -> refpt];
  mag[x_] := x * Sign[x /. ref];
  sig = Join[{-1,-1}, Table[1, n-2]];
  fw = syms;
  {ks, ws} = MakeKinematics[n, fw, sig, 1];
  amp = BGAmplitude[ks, ws, 1];
  R = Together[Simplify[amp/(-I)]];
  Print["===== n = ", n, " ====="];
  Print["ws = ", Simplify[ws]];
  Print["R", n, " = ", R];
  Print["  Numerator   = ", Factor[Numerator[R]]];
  Print["  Denominator = ", Factor[Denominator[R]]];
  Print["  check at ref: ", R /. ref];
  Clear[mag]; ];

doN[6, {a,b,c,d}, {2,3,5,7}];
