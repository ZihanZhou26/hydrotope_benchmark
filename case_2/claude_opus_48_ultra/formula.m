(* ============================================================
   Closed-form tree amplitude A_n in the TWO-MINUS sector
   sigma = (-1,-1,+1,...,+1), deep-water 1D surface waves, g=1.

     A_n = I * 2^(n-1) * w1*w2 * Sum_{S subset Plus} (-1)^|S| (a - sigma_S)_+^(n-3)

   where legs 1,2 are the minus-legs, Plus = {w3^2,...,wn^2},
   a = min(w1^2, w2^2), sigma_S = Sum_{i in S} wi^2, (x)_+ = Max(x,0).
   ============================================================ *)

ClearAll[Aformula];
(* omegas: the n signed frequencies, with the two minus-legs FIRST (legs 1,2). *)
Aformula[omegas_List] := Module[
  {n = Length[omegas], m, a, plus, d, subs, pw},
  pw[x_, e_] := If[x > 0, x^e, 0];
  m = omegas^2;
  a = Min[m[[1]], m[[2]]];          (* smaller minus-leg magnitude *)
  plus = m[[3 ;;]];                 (* plus-leg magnitudes         *)
  d = n - 3;
  subs = Subsets[plus];
  I*2^(n - 1)*omegas[[1]]*omegas[[2]]*
    Total[((-1)^Length[#]) pw[a - Total[#], d] & /@ subs]
];

(* If the minus-legs are not in positions 1,2, permute them there first.
   General entry point given a sign vector sigma (exactly two -1's): *)
AformulaGeneral[omegas_List, sigma_List] := Module[{mi, pl, ord},
  mi = Flatten[Position[sigma, -1]];
  pl = Flatten[Position[sigma, 1]];
  ord = Join[mi, pl];
  Aformula[omegas[[ord]]]
];
