(* Symbolic A5 with fixed ordering: w2 < w3 < w4, all positive *)
(* This allows us to drop Abs[] and sign considerations *)

(* For this ordering, p2 = -w2^2, p3 = w3^2, p4 = w4^2 *)
(* And |p_i| = w_i^2 always *)

(* Define simplified kernels for symbolic computation *)
Clear[w1, w2, w3, w4, w5, gVal];

(* We'll use the explicit expressions for the kinematics *)
(* From MakeKinematics with sigma = {-1,-1,+1,+1,+1}: *)
(* w1 = -(w3^2 + w3w4 + w4^2 + w2(w3+w4))/(w2+w3+w4) *)
(* w5 = -(w2+w3)(w2+w4)/(w2+w3+w4) *)

(* Instead of using the full BG, let's compute directly using the simplified FKernel *)

(* Define EKernel and FKernel symbolically, assuming arguments can have signs *)

Clear[EK, FK, mag];

mag[x_] := Sqrt[x^2];  (* Abs for symbolic *)

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

(* Test with specific numeric kinematics *)
gVal = 1;

(* fw = {1, 2, 3}: w2=1, w3=2, w4=3 *)
w2val = 1; w3val = 2; w4val = 3;
Dval = w2val + w3val + w4val;
w5val = -(w2val + w3val)*(w2val + w4val) / Dval;
w1val = -(w3val^2 + w3val*w4val + w4val^2 + w2val*(w3val + w4val)) / Dval;

Print["ws = ", {w1val, w2val, w3val, w4val, w5val}];

k1 = -w1val^2; k2 = -w2val^2; k3 = w3val^2; k4 = w4val^2; k5 = w5val^2;

Print["ks = ", {k1, k2, k3, k4, k5}];

(* Test FKernel values *)
Print["FK[3, {k1,k2,k3}] = ", FK[3, {k1, k2, k3}]];
Print["FK[3, {k3,k4,k5}] = ", FK[3, {k3, k4, k5}]];
Print["FK[4, {k2,k3,k4,k5}] = ", FK[4, {k2, k3, k4, k5}]];
