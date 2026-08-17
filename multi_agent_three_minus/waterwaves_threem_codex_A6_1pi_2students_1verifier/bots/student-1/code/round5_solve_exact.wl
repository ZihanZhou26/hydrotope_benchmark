If[Length[$CommandLine] < 3,
  Print["usage: WolframKernel -script solve_exact.wl input.json output.json"];
  Exit[2]
];

input = Import[$CommandLine[[-2]], "RawJSON"];
matrix = Map[ToExpression, input["matrix"], {2}];
rhs = ToExpression /@ input["rhs"];
t0 = AbsoluteTime[];
solution = LinearSolve[matrix, rhs];
residual = matrix.solution - rhs;
payload = <|
  "rank" -> MatrixRank[matrix],
  "rows" -> Length[matrix],
  "cols" -> Length[First[matrix]],
  "solve_seconds" -> N[AbsoluteTime[] - t0],
  "zero_residual" -> And @@ Thread[residual == 0],
  "coefficients" -> (ToString[InputForm[#]] & /@ solution)
|>;
Export[$CommandLine[[-1]], payload, "RawJSON"];
