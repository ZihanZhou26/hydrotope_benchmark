(* Test FKernel[4] for different argument orders *)
Clear[EK, FK, mag];

mag[x_] := Sqrt[x^2];

EK[3, {p1_, p2_, p3_}] := -1/2 (mag[p1]*mag[p2] + p1*p2);

EK[n_ /; n >= 4, {p1_, p2_, rest__}] := Module[
  {qp2, result, restList = {rest}, m},
  qp2 = mag[p2];
  result = qp2^(n - 3) * EK[3, {p1, p2, Total[restList]}] / (n - 2)!;
  For[m = 1, m <= n - 3, m++,
    result -= qp2^m / m! * 
      EK[n - m, Join[{p1, p2 + Total[restList[[1 ;; m]]]}, restList[[m + 1 ;;]]]];
  ];
  result
];

FK[3, {p1_, p2_, p3_}] := -1 - p1*p2/(mag[p1]*mag[p2]);

FK[n_ /; n >= 4, {p1_, p2_, rest__}] := Module[
  {qp1, qp2, result, sigM, restList = {rest}, m},
  qp1 = mag[p1]; qp2 = mag[p2];
  result = 2 * EK[n, {p1, p2, rest}] / qp1;
  For[m = 1, m <= n - 3, m++,
    sigM = p2 + Total[restList[[1 ;; m]]];
    result -= 2 * EK[m + 2, Join[{-sigM, p2}, restList[[1 ;; m]]]] *
      FK[n - m, Join[{p1, sigM}, restList[[m + 1 ;;]]]];
  ];
  result / qp2
];

(* Test different 4-momentum configurations *)
Print["FK[4, {-1, 4, 9, 4}] (p2,p3,p4,p5) = ", FK[4, {-1, 4, 9, 4}]];
Print["FK[4, {-16, -1, 4, 13}] (k1,k2,k3,k4+k5) = ", FK[4, {-16, -1, 4, 13}]];
Print["FK[4, {-1, -16, 4, 13}] (k2,k1,k3,k4+k5) = ", FK[4, {-1, -16, 4, 13}]];
Print["FK[4, {4, 13, -16, -1}] (k3,k4+k5,k1,k2) = ", FK[4, {4, 13, -16, -1}]];
Print["FK[4, {4, 9, -1, -16}] = ", FK[4, {4, 9, -1, -16}]];

(* The vertex sums over all permutations! *)
(* So we need FKernel[4, perm] for all 24 permutations *)
(* But most will be zero or equal by symmetry *)

(* Actually, FKernel is NOT symmetric in all arguments. It treats the first two specially through the recursion. *)

(* Let's understand: what does FKernel[4, args] depend on? *)
(* It uses p1, p2 as the first two args. The recursion splits on p2 + rest[[1;;m]]. *)
Print["\nAnalysis of FK[4, {-16, -1, 4, 13}]:"];
Print["  p1=-16 (k1, sigma=-1), p2=-1 (k2, sigma=-1), rest={4,13} (k3, k4+k5, both sigma=+1)"];
Print["  qp1=16, qp2=1"];
Print["  EK[4, {-16,-1,4,13}] first term: qp2^1 * EK[3,{-16,-1,17}]/2!"];
Print["    EK[3,{-16,-1,17}]: sigma1=-1, sigma2=-1 -> same -> non-zero"];
Print["  Second term (m=1): qp2^1/1! * EK[3,{-16, -1+4, 13}]"];
Print["    -1+4=3 (sigma=+1). EK[3,{-16, 3, 13}]: sigma1=-1, sigma2=+1 -> opposite -> ZERO"];
Print["  So EK[4,{-16,-1,4,13}] = 1 * EK[3,{-16,-1,17}]/2"];
Print["  Then FK[4] = (2*EK[4]/16 - 2*EK[3,{-sigM, -1, 4}]*FK[3,{-16, sigM, 13}]) / 1"];
Print["    sigM = -1+4 = 3"];
Print["    EK[3,{-3, -1, 4}]: sigma1=-1, sigma2=-1 -> non-zero"];
Print["    FK[3,{-16, 3, 13}]: sigma1=-1, sigma2=+1 -> FK=-1-(-1)(+1)=0 -> ZERO"];
Print["  So FK[4] = 2*EK[4]/16 = 2*EK[4]/16"];
