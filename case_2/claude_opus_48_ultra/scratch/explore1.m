(* Explore the two-minus sector A_n *)
Get["BGcore.m"];

gVal = 1;

twoMinus[n_] := Join[{-1, -1}, Table[1, n - 2]];

Print["=== two-minus sector A_n at simple rational points ==="];
cases = {
  {4, {2, 5/2}},
  {5, {2, 5/2, 3}},
  {6, {2, 5/2, 3, 7/2}},
  {7, {2, 5/2, 3, 7/2, 4}}
};
Do[
  Block[{n, freeW, sigmas, ks, ws, amp, t},
    n = c[[1]]; freeW = c[[2]];
    sigmas = twoMinus[n];
    {ks, ws} = MakeKinematics[n, freeW, sigmas, gVal];
    t = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal]][[1]];
    Print["n=", n];
    Print["  freeW = ", freeW];
    Print["  all w = ", ws];
    Print["  all k = ", ks, "  (k_i = sigma_i w_i^2)"];
    Print["  sumW = ", Total[ws], "  sumK = ", Total[ks]];
    Print["  A_", n, " = ", Simplify[amp], "  = ", N[amp]];
    Print["  time = ", t, " s\n"];
  ],
  {c, cases}
];
