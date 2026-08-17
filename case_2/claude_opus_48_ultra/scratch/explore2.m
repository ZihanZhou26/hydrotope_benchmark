Get["BGcore.m"];
gVal = 1;
twoMinus[n_] := Join[{-1, -1}, Table[1, n - 2]];

(* Homogeneity test: scale free freqs by lambda, see how A scales *)
Print["=== Homogeneity degree test ==="];
Do[
  Block[{n, base, sigmas, vals, ratios},
    n = nn;
    base = Table[i + 3/2, {i, n - 2}]; (* generic free freqs *)
    sigmas = twoMinus[n];
    vals = Table[
       Module[{fw, ks, ws, amp},
         fw = lam*base;
         {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
         amp = BGAmplitude[ks, ws, gVal];
         {lam, amp}],
       {lam, {1, 2, 3}}];
    Print["n=", n, ":  A(lam) = ", vals];
    (* degree = log2(A(2)/A(1)) *)
    Print["   A(2)/A(1) = ", vals[[2,2]]/vals[[1,2]], "   A(3)/A(1) = ", vals[[3,2]]/vals[[1,2]]];
  ],
  {nn, {5, 6, 7}}
];
