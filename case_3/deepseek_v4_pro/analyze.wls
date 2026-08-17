(* Manual computation of A5 for two-minus sector *)

(* Given kinematics for two-minus sector:
   w1 = -(w3+w4) + (S^2-S2)/(2(w2+S))  where S=w3+w4, S2=w3^2+w4^2
   w5 = -w2 - (S^2-S2)/(2(w2+S))
   k1 = -w1^2, k2 = -w2^2, k3 = w3^2, k4 = w4^2, k5 = w5^2
*)

(* For water waves, FKernel[3, {ki, kj, kr}] = -1 - ki*kj/(|ki||kj|) 
   Since ki = sigma_i * wi^2/g and |ki| = wi^2/g:
   ki*kj/(|ki||kj|) = sigma_i * sigma_j
   So FKernel[3] = -1 - sigma_i*sigma_j = 
     -2 when sigma_i = sigma_j
      0 when sigma_i = -sigma_j
*)

(* For n=5 two-minus: sigma = {-1,-1,+1,+1,+1}
   FKernel[3] nonzero only when both sigmas are same
*)

(* First, let me understand FKernel[4] and FKernel[5] *)

(* EKernel[3, {p1,p2,p3}] = -1/2 (|p1||p2| + p1 p2) *)
(* EKernel[n≥4, ps] = ... *)

(* Let me compute everything numerically first and see patterns *)

(* I'll compute A5 for several cases and look at A/(w1 w2 w3 w4 w5) *)

Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

computeCase[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, Map[Rationalize, fw], sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  {ws, amp}
];

(* Let's try to see if A_n has a simple formula in terms of w_i *)
(* For n=5, try A5 / (w3*w4) = ? *)

cases = {{1,2,3}, {2,3,5}, {3,5,7}, {1,3,4}, {2,4,6}};
Do[
  {ws, amp} = computeCase[5, c];
  w1=ws[[1]]; w2=ws[[2]]; w3=ws[[3]]; w4=ws[[4]]; w5=ws[[5]];
  
  A = amp/I; (* strip I *)
  
  (* Try various formulas *)
  f1 = -A/(w1*w2); 
  f2 = -A/(w3*w4);
  f3 = -A/(w3*w4*w5);
  f4 = -A/(w1*w2*w3*w4*w5);
  f5 = -A/((w1+w3)*(w2+w4));
  f6 = -A/(w3*w4*(w1+w5));
  f7 = -A/(w3*w4*(w2+w5));
  
  Print["fw=", c];
  Print["  ws=", N[ws, 8]];
  Print["  A=", N[amp, 10]];
  Print["  -A/(w1*w2)=", N[f1, 8], " -A/(w3*w4)=", N[f2, 8]];
  Print["  -A/(w1*w5)=", N[-A/(w1*w5), 8]];
  Print["  w1+w3=", w1+w3, " w2+w4=", w2+w4, " w1+w5=", w1+w5, " w2+w5=", w2+w5];
  ,
  {c, cases}
]
