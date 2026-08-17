(* Derive A_n formula for two-minus sector using FKernel simplification *)

(* Key results:
   FKernel[3,{p1,p2,p3}] = -2 if sign(p1)=sign(p2), 0 otherwise
   FKernel[n,{p1,p2,...,pn}] = -2*|p2|^{n-3}/(n-2)! if sign(p1)=sign(p2) 
                                and p2+any_partial_sum has opposite sign to p1
   
   EKernel[3,{p1,p2,p3}] = -|p1||p2| if sign(p1)=sign(p2), 0 otherwise
   EKernel[n,{p1,p2,...,pn}] = -|p1||p2|^{n-2}/(n-2)! under same conditions

   In the two-minus sector with g=1:
   - Minus legs: k1 < 0, k2 < 0. |k1| = w1^2/g, |k2| = w2^2/g
   - Plus legs: ki > 0 for i>=3. |ki| = wi^2/g
   - Cons: sum w = 0, -w1^2 - w2^2 + sum_{i=3}^n w_i^2 = 0
*)

(* For the vertex:
   Vertex[m+1, {k1, k_P1, ..., k_Pm}, {w1, w_P1, ..., w_Pm}]
   = (-I/2) * sum_{perm p} w_{p1} w_{p2} FKernel[m+1, {k_{p1}, k_{p2}, ..., k_{p_{m+1}}}]
   
   The FKernel picks the first two momenta for the base coupling.
   In the two-minus sector, k1 < 0 always. 
   
   Among {k_P1, ..., k_Pm}, exactly one part contains leg 2. Let's call it P_minus.
   k_{P_minus} could be positive or negative depending on the plus legs in P_minus.
   
   For the amplitude to be nonzero in the two-minus sector, we need k_{P_minus} < 0 
   (so that it can pair with k1 in the FKernel[3] base pairing).
   
   When k_{P_minus} < 0:
   - Pair (k1, k_{P_minus}) gives FKernel[m+1] = -2*|k_{P_minus}|^{m-1}/(m-1)!
   - Pair (k_{P_minus}, k1) gives FKernel[m+1] = -2*|k1|^{m-1}/(m-1)!
   
   All plus currents (k_Pj > 0) pair with each other.
   For a pair of plus currents (k_{Pj}, k_{Pk}): FKernel[m+1] = -2*|k_{Pk}|^{m-1}/(m-1)!
   
   But wait - FKernel[m+1] depends on the full set of m+1 momenta, not just the first two.
   The recursion picks out subsequent momenta via EKernel evaluations.
   
   Let me be more careful. FKernel[n] is computed recursively, and the full formula 
   depends on ALL the momenta in the list, not just the first two.
   
   The simplified formula FKernel[n] = -2|p2|^{n-3}/(n-2)! only holds when:
   1. sign(p1) = sign(p2)
   2. sign(p1) ≠ sign(p2 + sum of first m later p's) for m=1,...,n-3
   
   Condition 2 means: for p1 < 0, we need p2 + any partial sum of later p's > 0.
   
   If condition 2 fails (e.g., p2 is very negative, making p2+some_positive_sum < 0),
   then the intermediate EKernel terms don't vanish and FKernel is more complicated.
*)

(* Let me analyze the two-minus sector amplitude more carefully.
   
   The amplitude is:
   A_n = sum_{partitions P of {2..n}} Vertex[m+1, {k1, k_P1,...,k_Pm}, ...] * ∏ BGCurrent[P_j]
   
   For a given partition P:
   - Let P_minus be the part containing leg 2
   - All other parts P_j contain only plus legs, so k_{P_j} > 0
   - k_{P_minus} = -w2^2 + sum_{i in P_minus\{2}} w_i^2
   
   For the vertex FKernel contributions:
   - The vertex arguments are {k1 (minus), k_P1, ..., k_Pm}
   - In the permutation sum, FKernel is nonzero only when the first two arguments 
     have the same sign
   - k1 pairs with k_{P_minus} (if k_{P_minus} < 0): both negative
   - k_{P_j} pairs with k_{P_k} (both positive)
   
   Now, when does k_{P_minus} < 0? When w2^2 > sum_{i in P_minus\{2}} w_i^2.
   This condition selects a subset of configurations.
   
   But the hint says the final formula is a SINGLE rational function valid for ALL 
   kinematics in the sector. This means the formula should automatically handle 
   the case where k_{P_minus} > 0 (by giving zero contribution from those terms 
   in the sum).
*)

Print["=== Let me verify the FKernel[n] formula numerically ==="]

mag[k_]:=Abs[k];
EKernel[3,ps_]:=-1/2(mag[ps[[1]]]*mag[ps[[2]]]+ps[[1]]*ps[[2]]);
EKernel[n_/;n>=4,ps_]:=Module[{p1=ps[[1]],p2=ps[[2]],r=ps[[3;;]],q2,rst},q2=mag[p2];rst=q2^(n-3)*EKernel[3,{p1,p2,Total[r]}]/(n-2)!;Do[rst-=q2^m/m!*EKernel[n-m,Join[{p1,p2+Total[r[[1;;m]]]},r[[m+1;;]]]],{m,1,n-3}];rst];
FKernelSafe[3,ps_]:=Module[{a,b},a=mag[ps[[1]]];b=mag[ps[[2]]];If[a==0||b==0,-1,-1-ps[[1]]*ps[[2]]/(a*b)]];
FKernelSafe[n_/;n>=4,ps_]:=Module[{p1=ps[[1]],p2=ps[[2]],r=ps[[3;;]],q1,q2,rst,sM},q1=mag[p1];q2=mag[p2];If[q1==0||q2==0,Return[0]];rst=2*EKernel[n,ps]/q1;Do[sM=p2+Total[r[[1;;m]]];rst-=2*EKernel[m+2,Join[{-sM,p2},r[[1;;m]]]]*FKernelSafe[n-m,Join[{p1,sM},r[[m+1;;]]]],{m,1,n-3}];rst/q2];

(* Check FKernel[n] formula for a case where p1<0, p2<0, and all later p's > p2 *)
(* This ensures sign(p2+any_partial_sum) > 0, opposite to sign(p1) *)
Do[
  p1 = -100;
  p2 = -16;
  rest = Table[RandomInteger[{10,50}], {n-2}];
  ps = Join[{p1,p2}, rest];
  Print["n=", n, ": FKernel = ", N[FKernelSafe[n, ps]], 
    "  formula: -2*|p2|^(n-3)/(n-2)! = ", N[-2*mag[p2]^(n-3)/(n-2)!]];
  , {n, 3, 7}]

Print[""];
Print["=== Now check when condition fails (p2 is very negative) ==="];
p1 = -100; p2 = -90; rest = {10, 20};  (* p2+10 = -80 < 0, same sign as p1 *)
ps = {p1, p2, rest[[1]], rest[[2]]};
Print["n=4: FKernel = ", N[FKernelSafe[4, ps]], 
  "  simple formula: -2*|p2|^1/2! = ", N[-2*mag[p2]^1/2!]];
