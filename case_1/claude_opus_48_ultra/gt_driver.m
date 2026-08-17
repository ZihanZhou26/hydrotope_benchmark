(* ground-truth driver: two-minus sector A_n at rational points *)
Get["bg_defs.m"];
gVal = 1;

(* two-minus: sigma = {-1,-1,+1,...,+1} *)
twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

cases = {
  {4, {2, 3}},
  {4, {5/2, 7/3}},
  {5, {2, 5/2, 3}},
  {5, {3/2, 11/5, 7/3}},
  {6, {3/2, 2, 5/2, 3}},
  {6, {2, 3, 7/2, 11/3}}
};

Do[Block[{n, fw, sig, ks, ws, amp, t},
  n = c[[1]]; fw = c[[2]];
  sig = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, fw, sig, gVal];
  t = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal];][[1]];
  Print["n=", n, " free=", fw];
  Print["  ws = ", ws];
  Print["  ks = ", ks];
  Print["  sum w = ", Total[ws], "  sum k = ", Total[ks]];
  Print["  A = ", amp];
  Print["  A(N) = ", N[amp, 25]];
  Print["  time ", t, "s"];
  Print[""];
  ], {c, cases}]
