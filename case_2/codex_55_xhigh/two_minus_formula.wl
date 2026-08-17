ClearAll[TruncatedPower, TwoMinusClosedForm];

TruncatedPower[x_, p_Integer] := If[x > 0, x^p, 0]

TwoMinusClosedForm[omegas_List] := Module[
  {n = Length[omegas], r, qs, p},
  r = Min[omegas[[1]]^2, omegas[[2]]^2];
  qs = omegas[[3 ;;]]^2;
  p = n - 3;
  I*2^(n - 1)*omegas[[1]]*omegas[[2]]*
    Total[
      (-1)^Length[#] TruncatedPower[r - Total[qs[[#]]], p] & /@
        Subsets[Range[Length[qs]]]
    ]
]
