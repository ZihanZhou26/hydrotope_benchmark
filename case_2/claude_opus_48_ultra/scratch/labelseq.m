(* General label-sequence analyzer.
   analyzeData[n, raw]: raw = list of {ws, P}.
   Groups by sorted-magnitude positions of the two minus legs (legs 1,2).
   Fits R = P/(-16 w1 w2) as homogeneous deg (n-3) poly in sorted magnitudes mu_1..mu_n,
   with mu_n eliminated via momentum conservation. *)

monsOf[vars_, d_] := If[d == 0, {1}, DeleteDuplicates[Times @@@ Tuples[vars, d]]];

analyzeData[n_, raw_] := Module[
  {data, groups, degR, results, muS},
  muS = Array[muSym, n];
  data = Table[
    Module[{ws = e[[1]], P = e[[2]], m, minusPos, R, ord},
     m = ws^2;
     ord = Ordering[m];
     minusPos = Sort[(Position[ord, #][[1, 1]]) & /@ {1, 2}];
     R = P/(-16 ws[[1]]*ws[[2]]);
     {minusPos, Sort[m], R}
    ], {e, raw}];
  groups = GatherBy[data, First];
  degR = n - 3;
  Print["=== n=", n, " : ", Length[groups], " realized label-sequences (", Length[raw], " pts) ==="];
  results = {};
  Do[Module[{grp = groups[[gi]], minusPos, pts, rule, vars, mons, kk, M, rhs, sol, ok, Rpoly, plusPos},
     minusPos = grp[[1, 1]]; pts = grp;
     plusPos = Complement[Range[n], minusPos];
     rule = First@Solve[Total[muS[[minusPos]]] == Total[muS[[plusPos]]], muS[[n]]];
     vars = muS[[1 ;; n - 1]];
     mons = monsOf[vars, degR];
     kk = Length[mons];
     If[Length[pts] < kk + 3,
        AppendTo[results, {minusPos, "few(" <> ToString[Length[pts]] <> ")", None}]; Continue[]];
     M = Table[mons /. Thread[vars -> pts[[r, 2, 1 ;; n - 1]]], {r, Length[pts]}];
     rhs = pts[[All, 3]];
     sol = Quiet@Check[LinearSolve[M[[1 ;; kk]], rhs[[1 ;; kk]]], $Failed];
     If[sol === $Failed, AppendTo[results, {minusPos, "singular", None}]; Continue[]];
     ok = AllTrue[Range[Length[pts]], (mons . sol /. Thread[vars -> pts[[#, 2, 1 ;; n - 1]]]) == rhs[[#]] &];
     Rpoly = mons . sol;
     AppendTo[results, {minusPos, If[ok, "EXACT(" <> ToString[Length[pts]] <> ")", "INCONSIST(" <> ToString[Length[pts]] <> ")"], Rpoly}];
    ], {gi, Length[groups]}];
  results = SortBy[results, #[[1]] &];
  Do[Module[{r = results[[i]]},
     Print["  minus@", r[[1]], "  ", r[[2]]];
     If[r[[3]] =!= None, Print["     R = ", Factor[r[[3]]] /. muSym[j_] :> Symbol["mu" <> ToString[j]]]];
    ], {i, Length[results]}];
  results];
