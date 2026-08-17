(* Fit R as symmetric truncated-power spline.
   a = min(minus magnitudes) [legs 1,2]; plus = magnitudes of legs 3..n.
   basis: bp[k] = Sum_{S subset plus,|S|=k} (a - sum_S)_+^(n-3)
          bm[k] = Sum_{|S|=k} (sum_S - a)_+^(n-3)
   R = Sum_k ap[k] bp[k] + am[k] bm[k]. *)
pw[x_, d_] := If[x > 0, x^d, 0];

fitSpline[n_, raw_] := Module[{deg = n - 3, npl = n - 2, rows, mons, M, rhs, sol, basisLabels, ok, pred},
  basisLabels = Join[Table[{"p", k}, {k, 0, npl}], Table[{"m", k}, {k, 1, npl}]];
  rows = Table[
    Module[{ws = e[[1]], P = e[[2]], m, a, plus, sums, bp, bm, R, vec},
     m = ws^2; a = Min[m[[1]], m[[2]]]; plus = Sort[m[[3 ;;]]];
     sums = Table[Total /@ Subsets[plus, {k}], {k, 0, npl}]; (* sums[[k+1]] = list of subset-sums of size k *)
     bp = Table[Total[pw[a - #, deg] & /@ sums[[k + 1]]], {k, 0, npl}];
     bm = Table[Total[pw[# - a, deg] & /@ sums[[k + 1]]], {k, 1, npl}];
     vec = Join[bp, bm];
     R = P/(-16 ws[[1]]*ws[[2]]);
     {vec, R}], {e, raw}];
  M = rows[[All, 1]]; rhs = rows[[All, 2]];
  Print["basis size = ", Length[basisLabels], "  data pts = ", Length[M]];
  (* exact solve on a well-conditioned subset, then verify on all *)
  Module[{k = Length[basisLabels], idx, Msub, rsub},
   idx = Range[Length[M]];
   sol = Quiet@Check[LeastSquares[M, rhs], $Failed];
   If[sol === $Failed, Print["LeastSquares failed"]; Return[]];
   pred = M . sol;
   Print["max |pred-R| over all pts = ", N@Max[Abs[pred - rhs]]];
   Print["solution coeffs:"];
   Do[Print["  ", basisLabels[[i]], " : ", sol[[i]], "  (", N[sol[[i]]], ")"], {i, Length[sol]}];
  ];
  {basisLabels, sol}];
