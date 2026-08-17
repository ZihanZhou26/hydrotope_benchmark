(* Explicit computation of FKernel[4] for two-minus sector *)
(* Goal: understand the structure of higher FKernels *)

magK[k_] := Abs[k];

EKernel[3, p1_, p2_, p3_] := -1/2 (magK[p1]*magK[p2] + p1*p2);

EKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp2, result},
  qp2 = magK[p2];
  result = qp2^(n - 3)*EKernel[3, p1, p2, Total[rest]]/(n - 2)!;
  Do[result -= qp2^m/m!*
    EKernel[n - m, Join[{p1, p2 + Total[rest[[1 ;; m]]]}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result]

FKernel[3, p1_, p2_, p3_] := -1 - p1*p2/(magK[p1]*magK[p2]);

FKernel[n_Integer /; n >= 4, ps_List] := Module[
  {p1 = ps[[1]], p2 = ps[[2]], rest = ps[[3 ;;]], qp1, qp2, result, sigM},
  qp1 = magK[p1]; qp2 = magK[p2];
  result = 2*EKernel[n, ps]/qp1;
  Do[sigM = p2 + Total[rest[[1 ;; m]]];
    result -= 2*EKernel[m + 2, Join[{-sigM, p2}, rest[[1 ;; m]]]]*
      FKernel[n - m, Join[{p1, sigM}, rest[[m + 1 ;;]]]],
    {m, 1, n - 3}];
  result/qp2]

(* For two-minus sector, sigma = {-1,-1,+1,+1} at n=4 *)
(* k_i = sigma_i * w_i^2/g *)

(* Let's use symbolic w's and g=1 *)
(* ws = {w1,w2,w3,w4} with sigma={-1,-1,+1,+1} *)
(* For n=4 two-minus: w4=-w2, w1=-w3 *)

(* FKernel[4, {k1,k2,k3,k4}] with kin order *)

(* Test numerically *)
w2 = 5; w3 = 1; w4 = 6; w1 = -w3; (* Not the two-minus kinematics, just a test *)

(* Actually, let's test FKernel[4] for a specific permutation of sigma values *)
gVal = 1;

(* Case: all legs have sigma=+1, k_i = w_i^2/g *)
k1 = 9; k2 = 16; k3 = 25; k4 = 36; (* e.g., w1=3,w2=4,w3=5,w4=6 *)
Print["FKernel[4] for all plus: ", FKernel[4, {k1, k2, k3, k4}]];

(* Case: two minus, two plus *)
k1 = -9; k2 = -16; k3 = 25; k4 = 36; (* w1=3,w2=4 with sigma=-1 *)
Print["FKernel[4] for two-minus-two-plus: ", FKernel[4, {k1, k2, k3, k4}]];

(* What does FKernel[4] evaluate to? *)
