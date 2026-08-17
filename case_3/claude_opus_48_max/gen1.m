<< bg_core.m
gVal = 1;
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];

testPts = {
  {4, {3/2, 2}},
  {5, {3/2, 2, 5/2}},
  {6, {3/2, 2, 5/2, 3}}
};

Do[Block[{n, freeW, sig, ks, ws, amp},
  n = tc[[1]]; freeW = tc[[2]];
  sig = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, gVal];
  Print["===== n = ", n, " ====="];
  Print["  sigma = ", sig];
  Print["  all w = ", ws];
  Print["  all k = ", ks];
  Print["  check: sum w = ", Total[ws], "  sum sig*w^2 = ", Total[sig*ws^2]];
  amp = BGAmplitude[ks, ws, gVal];
  Print["  A", n, " (exact) = ", amp];
  Print["  A", n, " (N) = ", N[amp, 20]];
  Print[""];
 ], {tc, testPts}]
