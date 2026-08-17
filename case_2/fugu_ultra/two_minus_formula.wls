(* Formula for the two-minus sector sigma = {-1,-1,+1,...,+1}. *)
Clear[TwoMinusClosedForm];
TwoMinusClosedForm[omegas_List, g_:1] := Module[
  {n = Length[omegas], pos, q, ppow, spline},
  pos = Range[3, n];
  q[i_] := omegas[[i]]^2;
  ppow[x_, m_] := If[x > 0, x^m, 0];
  spline = Total[
    ((-1)^Length[#]) * ppow[q[1] - Total[q /@ #], n - 3] & /@ Subsets[pos]
  ];
  I * 2^(n - 1) * omegas[[1]] * omegas[[2]] * spline / g^(n - 3)
]
