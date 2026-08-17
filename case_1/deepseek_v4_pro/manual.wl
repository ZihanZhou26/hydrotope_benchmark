(* Manual step-by-step computation of A4 in two-minus sector *)
(* Assuming w3 > w2 so that w3^2 - w2^2 > 0 *)

(* With w3 > w2, we have:
   ws = {-w3, w2, w3, -w2}
   ks = {-w3^2, -w2^2, w3^2, w2^2}
   k_{23} = w3^2 - w2^2 > 0, so |k_{23}| = w3^2 - w2^2
   k_{34} = w3^2 + w2^2 > 0, so |k_{34}| = w3^2 + w2^2
   k_{24} = 0, BGCurrent = 0
*)

(* We need to compute:
   A4 = Vertex[4, {k1,k2,k3,k4}, {w1,w2,w3,w4}] * 1 * 1 * 1
      + Vertex[3, {k1,k2,k3+k4}, {w1,w2,w3+w4}] * 1 * BGCurrent[{3,4}]
      + Vertex[3, {k1,k3,k2+k4}, {w1,w3,w2+w4}] * 1 * BGCurrent[{2,4}]  (=0)
      + Vertex[3, {k1,k4,k2+k3}, {w1,w4,w2+w3}] * 1 * BGCurrent[{2,3}]
*)

(* Let me compute key quantities first *)

(* Signs:
   sign(k1) = sign(-w3^2) = -1
   sign(k2) = sign(-w2^2) = -1
   sign(k3) = sign(w3^2) = +1
   sign(k4) = sign(w2^2) = +1
   sign(k3+k4) = sign(w3^2+w2^2) = +1
   sign(k2+k3) = sign(w3^2-w2^2) = +1 (since w3 > w2)
*)

(* FKernel[3, {p1,p2,p3}] = -1 - sign(p1)*sign(p2) = -2 if same sign, 0 if opposite *)

(* EKernel[3, {p1,p2,p3}] = -1/2 (|p1||p2| + p1*p2) = -|p1||p2| if same sign, 0 if opposite *)

(* ===== PART 1: Vertex[4] for the contact term ===== *)
(* Vertex[4, {k1,k2,k3,k4}, {w1,w2,w3,w4}]
   Sum over permutations of w_{p1} w_{p2} FKernel[4, {k_{p1},k_{p2},k_{p3},k_{p4}}]
*)

(* First compute FKernel[4, {k1,k2,k3,k4}] *)
(* FKernel[4] for momenta {k1,k2,k3,k4} where k1,k2<0, k3,k4>0 *)
(* 
  FKernel[4] = (2*EKernel[4]/|k1|)/|k2|
  
  EKernel[4] = |k2| * EKernel[3, {k1, k2, k3+k4}] / 2 
             - |k2| * EKernel[3, {k1, k2+k3, k4}]
             
  EKernel[3, {k1, k2, k3+k4}]: k1<0, k2<0 (same sign) 
    -> -|k1||k2| = -w3^2 * w2^2
    
  EKernel[3, {k1, k2+k3, k4}]: k1<0, sign(k2+k3)=sign(w3^2-w2^2)=+1 (opposite)
    -> 0
    
  So EKernel[4] = w2^2 * (-w3^2*w2^2) / 2 - w2^2 * 0 = -w2^4 * w3^2 / 2

  FKernel[4] = 2*(-w2^4*w3^2/2) / w3^2 / w2^2 = -w2^4 / w2^2 = -w2^2
*)

(* Wait, let me recheck. The arguments to FKernel[4] are {k1,k2,k3,k4}.
   qp1 = |k1| = w3^2, qp2 = |k2| = w2^2
   result = 2*EKernel[4, {k1,k2,k3,k4}] / w3^2
   
   Let me compute EKernel[4, {k1,k2,k3,k4}] more carefully:
   p1=k1=-w3^2, p2=k2=-w2^2, rest={k3,k4}={w3^2,w2^2}
   qp2 = |k2| = w2^2
   
   result = qp2 * EKernel[3, {k1, k2, k3+k4}] / 2!   (n-3=1: just one term)
            - sum over m=1 to 1 of qp2^m/m! * EKernel[4-m, ...]
   
   m=1:
   qp2^1/1! * EKernel[3, {k1, k2+k3, k4}]  (4-1=3)
   
   So EKernel[4] = w2^2 * EKernel[3, {k1,k2,k3+k4}]/2 
                  - w2^2 * EKernel[3, {k1,k2+k3,k4}]
   
   EKernel[3, {k1,k2,k3+k4}]: k1=-w3^2, k2=-w2^2, same sign (-)
     = -1/2 (|k1||k2| + k1*k2) = -1/2 (w3^2*w2^2 + w3^2*w2^2) = -w3^2*w2^2
   
   EKernel[3, {k1,k2+k3,k4}]: k1=-w3^2(<0), k2+k3=-w2^2+w3^2(>0), opposite
     = 0 (since 1+sign(k1)sign(k2+k3)=1+(-1)(+1)=0)
   
   So EKernel[4] = w2^2 * (-w3^2*w2^2)/2 - w2^2 * 0 = -w2^4*w3^2/2
   
   Then FKernel[4] = 2*EKernel[4]/(w3^2) / w2^2
   Wait, the code says: result = 2*EKernel[n,ps]/qp1 then result/qp2
   So: result = 2*EKernel[4]/(w3^2) = 2*(-w2^4*w3^2/2)/(w3^2) = -w2^4
   Then result/qp2 = -w2^4 / w2^2 = -w2^2
   
   So FKernel[4, {k1,k2,k3,k4}] = -w2^2
*)

(* But FKernel[4] depends on the ORDER of arguments! The vertex sums over permutations.
   For different permutations, the first two arguments change, so FKernel[4] will differ.
*)

(* Let me think about this differently. The vertex sum is:
   Vertex[4] = (-I/2) * Σ_{p} w_{p1} w_{p2} FKernel[4, {k_{p1}, k_{p2}, k_{p3}, k_{p4}}]
   
   The FKernel[4] picks out the first two momenta for the base FKernel[3] coupling.
   In the recursion, FKernel[4] eventually reduces to FKernel[3] combinations.
   
   Actually, FKernel[n] is the n-point off-shell current for the "+" polarization 
   (or specific leg). It's a complicated object.
*)

(* Let me take a shortcut. The FKernel[n] in the vertex gets its first two arguments 
   from the permutation. The FKernel base case (FKernel[3]) picks out the first two.
   
   For the two-minus sector, recall:
   - FKernel[3] = -1 - sign(p1)*sign(p2)
   - This is nonzero only when p1 and p2 have the same sign
   
   In Vertex[4] with args {k1,k2,k3,k4} where k1,k2<0 and k3,k4>0:
   - The sum over permutations pairs up legs
   - Pairs (1,2): both negative → FKernel[3] = -2
   - Pairs (3,4): both positive → FKernel[3] = -2
   - Mixed pairs (1,3),(1,4),(2,3),(2,4): opposite → FKernel[3] = 0
   
   But FKernel[4] is not just FKernel[3]! FKernel[4] has a recursive structure that 
   also involves FKernel[3] at lower points. However, EKernel[3] vanishes for opposite 
   signs, and FKernel[3] vanishes for opposite signs. This means many terms in the 
   recursion vanish.
   
   I think the key simplification is that FKernel[n] factorizes into products of 
   FKernel[3] factors for same-sign subsets.
*)

(* OK, I'm going to take a completely different approach. Let me just write down the 
   general form of A_n based on structural considerations, and then fix coefficients 
   by matching numeric data.

   For general n, let me define:
   - ω_i: frequencies (with ω_1, ω_2 corresponding to minus legs)
   - α_i = ω_i^2 (squared frequencies, proportional to |k_i|)
   - σ_i: signs (-1 for legs 1,2; +1 for legs 3,...,n)
   - k_i = σ_i α_i / g
   
   The conservation laws:
   Σ ω_i = 0
   Σ σ_i α_i = 0  (i.e., α_3+...+α_n = α_1+α_2)
   
   The amplitude A_n should be a rational function in ω_i that is:
   - Homogeneous of degree 2n-4 in ω
   - Symmetric under exchange of legs 1↔2 (both minus)
   - Symmetric under permutations of legs 3,...,n (all plus)
   - Has poles at factorization channels
   
   The denominator: product over all partitions (L,R) with |L|,|R|≥2 of (ω_L^2 - g|k_L|)
   
   Since legs 1,2 are minus and 3,...,n are plus, let me denote:
   ω_- = {ω_1, ω_2} (minus legs)
   ω_+ = {ω_3, ..., ω_n} (plus legs)
   
   For a partition (L,R):
   - If L contains both minus legs: k_L < 0, |k_L| = -k_L
   - If L contains one minus leg: k_L sign depends on magnitudes
   - If L contains no minus legs: k_L > 0, |k_L| = k_L
   
   The product of all channel factors is symmetric under exchanging L↔R.
   
   Hmm, I wonder if there's a known closed form for this. Let me think about what 
   the amplitude looks like in terms of the actual ω_i.
*)

Print["=== Let me try to directly compute FKernel for key configurations ==="]

(* For n=4 two-minus with w3>w2, let's compute all the vertices manually *)
w1 = -w3; w2v = w2; w3v = w3; w4v = -w2;
k1 = -w3^2; k2v = -w2^2; k3v = w3^2; k4v = w2^2;

(* Compute FKernel[4, {k1,k2,k3,k4}] using simplified rules *)
(* We'll use the recursive definition with the knowledge that:
   EKernel[3] = -|p1||p2| if sign(p1)=sign(p2), 0 otherwise
   FKernel[3] = -2 if sign(p1)=sign(p2), 0 otherwise
*)

(* So EKernel[3,{p1,p2,p3}] = -|p1||p2| for same sign, 0 for opposite *)
(* And FKernel[3,{p1,p2,p3}] = -2 for same sign, 0 for opposite *)

(* Now FKernel[4,{p1,p2,p3,p4}] = (2*EKernel[4]/qp1)/qp2
   where EKernel[4] = qp2*EKernel[3,{p1,p2,p3+p4}]/2! - qp2^1*EKernel[3,{p1,p2+p3,p4}]/1!
   
   For {k1,k2,k3,k4}:
   qp1 = w3^2, qp2 = w2^2
   
   EKernel[3,{k1,k2,k3+k4}]: k1,k2 both negative → same sign → -w3^2*w2^2
   EKernel[3,{k1,k2+k3,k4}]: k1<0, k2+k3 = w3^2-w2^2 > 0 → opposite → 0
   
   EKernel[4] = w2^2*(-w3^2*w2^2)/2 - w2^2*0 = -w2^4*w3^2/2
   
   FKernel[4] = 2*(-w2^4*w3^2/2)/(w3^2) / w2^2 = -w2^4/w2^2 = -w2^2
*)

Print["FKernel[4,{k1,k2,k3,k4}] = -w2^2"]

(* Similarly, FKernel[4,{k1,k2,k4,k3}] would involve {k1,k2,k4,k3}
   EKernel[3,{k1,k2,k4+k3}]: k1,k2 same → -w3^2*w2^2
   EKernel[3,{k1,k2+k4,k3}]: k1<0, k2+k4 = -w2^2+w2^2 = 0 → |k2+k4|=0, but EKernel[3] 
     with mag[0]=0 gives -1/2(0*... + 0*...) = 0. So it's 0.
   
   Same result: FKernel[4,{k1,k2,k4,k3}] = -w2^2
*)

Print["FKernel[4,{k1,k2,k4,k3}] = -w2^2"]

(* For permutations where the first two are NOT (k1,k2):
   {k1,k3,k2,k4}: p1=k1<0, p2=k3>0 → opposite sign → EKernel[3] terms vanish
   Let's check EKernel[3,{k1,k3,k2+k4}]: opposite → 0
   EKernel[3,{k1,k3+k2,k4}]: k1<0, k3+k2 = w3^2-w2^2 >0 → opposite → 0
   So EKernel[4] = 0, FKernel[4] = 0
*)

Print["For permutations with first two having opposite signs, FKernel[4] = 0"]

(* So FKernel[4] is nonzero ONLY when the first two legs have the same sign.
   And when they do, FKernel[4] = -(mass of second leg)^2 = -|k_{p2}|
   
   For {k1,k2,...}: FKernel[4] = -|k2| = -w2^2
   For {k2,k1,...}: FKernel[4] = -|k1| = -w3^2
   For {k3,k4,...}: FKernel[4] = -|k4| = -w2^2
   For {k4,k3,...}: FKernel[4] = -|k3| = -w3^2
*)

(* Let me verify for {k3,k4,k1,k2}:
   p1=k3=w3^2, p2=k4=w2^2
   EKernel[3,{k3,k4,k1+k2}]: both positive → same sign → -w3^2*w2^2
   EKernel[3,{k3,k4+k1,k2}]: k3>0, k4+k1 = w2^2-w3^2 <0 → opposite → 0
   EKernel[4] = |k4|*EKernel[3,{k3,k4,k1+k2}]/2 = w2^2*(-w3^2*w2^2)/2 = -w2^4*w3^2/2
   FKernel[4] = 2*EKernel[4]/|k3| / |k4| = 2*(-w2^4*w3^2/2)/(w3^2)/w2^2 = -w2^2
   Yes! FKernel[4] = -|k_{p2}| = -|k4| = -w2^2
*)

Print["Conjecture: FKernel[n]({p1,p2,...}) = -|p2| when sign(p1)=sign(p2), 0 otherwise"]
Print["(This would be a huge simplification!)"]

(* Let me verify for FKernel[5] with same-sign p1,p2 *)
(* If this conjecture holds, the vertex 4-point becomes very simple *)
(* Vertex[4,{k1,k2,k3,k4},{w1,w2,w3,w4}] = 
   (-I/2) * Σ_p w_{p1} w_{p2} * (-|k_{p2}| if sign match else 0)
*)

Print[""]
Print["Based on this conjecture, let me compute A4..."]
Print["Vertex[4] terms with nonzero FKernel:"]
Print["  (1,2): w1*w2*(-|k2|) + w2*w1*(-|k1|) = (-w3)*(w2)*(-w2^2) + (w2)*(-w3)*(-w3^2)"]
Print["         = w3*w2^3 + w2*w3^3 = w2*w3*(w2^2+w3^2)"]
Print["  (3,4): w3*w4*(-|k4|) + w4*w3*(-|k3|) = w3*(-w2)*(-w2^2) + (-w2)*w3*(-w3^2)"]
Print["         = w3*w2^3 + w2*w3^3 = w2*w3*(w2^2+w3^2)"]
Print["  Total: 2*w2*w3*(w2^2+w3^2)"]
Print["  Vertex[4] = (-I/2) * 2*w2*w3*(w2^2+w3^2) = -I * w2*w3*(w2^2+w3^2)"]
