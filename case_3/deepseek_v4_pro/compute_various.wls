Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeNumeric[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  fwRat = Map[Rationalize, fw];
  {ks, ws} = MakeKinematics[n, fwRat, sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  {ws, amp}
];

(* Careful test cases *)
cases = {
  {5, {1, 1, 1}},
  {5, {1, 2, 1}},
  {5, {2, 1, 1}},
  {5, {1, 1, 2}},
  {5, {1, 2, 3}},
  {5, {2, 3, 5}},
  {6, {1, 1, 1, 1}},
  {6, {1, 2, 3, 4}}
};

Do[
  {n, fw} = c;
  res = computeNumeric[n, fw];
  If[res === $Failed, Continue[]];
  {ws, amp} = res;
  Print["n=", n, " fw=", fw];
  Print["  ws=", N[ws, 20]];
  Print["  A=", N[amp, 20]];
  Print["  |A|=", N[Abs[amp], 20]];
  Print["  prod=", N[Product[ws[[i]], {i, 1, n}], 20]];
  ,
  {c, cases}
]
