(* Specialized BG for two-minus sector 
   Key insight: FKernel[3] = -2 if same sigma, 0 if opposite
                 EKernel[3] = -w1^2 w2^2/g^2 if same sigma, 0 if opposite
   
   For two-minus: sigma = {-1,-1,+1,...,+1}
   All intermediate sums of momenta have definite signs.
*)

(* Simplified kernels using sigma info *)

magK[k_] := Abs[k];

(* EKernel for symbolic computation - uses Abs for generality *)
simplifiedEKernel[3, p1_, p2_, p3_] := -1/2 (magK[p1]*magK[p2] + p1*p2);

simplifiedEKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp2, result},
  qp2 = magK[p2];
  result = qp2^(n - 3)*simplifiedEKernel[3, p1, p2, Total[rest]]/(n - 2)!;
  Do[result -= qp2^m/m!*
    simplifiedEKernel[n - m, Join[{p1, p2 + Total[rest[[1 ;; m]]]}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result
];

simplifiedFKernel[3, p1_, p2_, p3_] := Module[{},
  -1 - p1*p2/(magK[p1]*magK[p2])
];

simplifiedFKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp1, qp2, result, sigM},
  qp1 = magK[p1]; qp2 = magK[p2];
  result = 2*simplifiedEKernel[n, ps]/qp1;
  Do[sigM = p2 + Total[rest[[1 ;; m]]];
    result -= 2*simplifiedEKernel[m + 2, Join[{-sigM, p2}, rest[[1 ;; m]]]]*
      simplifiedFKernel[n - m, Join[{p1, sigM}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result/qp2
];

(* Now compute A5 semi-manually *)
gVal = 1;

(* For n=5 two-minus, ws from MakeKinematics *)
computeKinematics5[w2_, w3_, w4_] := Module[{S, S2, sumFree, w1, w5, ws, ks},
  S = w3 + w4;
  S2 = w3^2 + w4^2;
  sumFree = w2 + S;
  w5 = -(w2 + w3)*(w2 + w4) / sumFree;
  w1 = -(w3^2 + w3*w4 + w4^2 + w2*(w3 + w4)) / sumFree;
  ws = {w1, w2, w3, w4, w5};
  ks = {-w1^2/gVal, -w2^2/gVal, w3^2/gVal, w4^2/gVal, w5^2/gVal};
  {ws, ks}
];

(* Test with specific numbers *)
{ws, ks} = computeKinematics5[1, 2, 3];
Print["ws=", ws];
Print["ks=", ks];

(* Now let's compute the amplitude using our own faster code *)
(* For the two-minus sector, let's directly compute using the known structure *)
