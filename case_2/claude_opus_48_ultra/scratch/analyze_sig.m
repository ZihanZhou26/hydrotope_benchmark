(* analyzeBySig[n, raw]: raw = list of {ws, P}. Group by FULL subset-sum signature.
   Fit R = P/(-16 w1 w2) as homog deg (n-3) poly in sorted magnitudes (mu_n eliminated). *)
monsOf[vars_, d_] := If[d == 0, {1}, DeleteDuplicates[Times @@@ Tuples[vars, d]]];

analyzeBySig[n_, raw_] := Module[{sigmas, subs, data, groups, degR, muS, results},
  sigmas = Join[{-1, -1}, Table[1, n - 2]];
  subs = Select[Subsets[Range[n], {1, n - 1}], MemberQ[#, 1] &];
  muS = Array[muSym, n];
  data = Table[
    Module[{ws = e[[1]], P = e[[2]], ks, m, ord, minusPos, sig, R},
     m = ws^2; ks = sigmas*m;
     ord = Ordering[m];
     minusPos = Sort[(Position[ord, #][[1, 1]]) & /@ {1, 2}];
     sig = Sign[Map[Total[ks[[#]]] &, subs]];
     R = P/(-16 ws[[1]]*ws[[2]]);
     {sig, minusPos, Sort[m], R}
    ], {e, raw}];
  groups = GatherBy[data, First];
  degR = n - 3;
  Print["=== n=", n, " : ", Length[groups], " signatures (", Length[raw], " pts) ==="];
  results = {};
  Do[Module[{grp = groups[[gi]], minusPos, pts, plusPos, rule, vars, mons, kk, M, rhs, sol, ok},
     minusPos = grp[[1, 2]]; pts = grp;
     plusPos = Complement[Range[n], minusPos];
     rule = First@Solve[Total[muS[[minusPos]]] == Total[muS[[plusPos]]], muS[[n]]];
     vars = muS[[1 ;; n - 1]];
     mons = monsOf[vars, degR]; kk = Length[mons];
     If[Length[pts] < kk + 2,
        AppendTo[results, {minusPos, Length[pts], "few", None}]; Continue[]];
     M = Table[mons /. Thread[vars -> pts[[r, 3, 1 ;; n - 1]]], {r, Length[pts]}];
     rhs = pts[[All, 4]];
     sol = Quiet@Check[LinearSolve[M[[1 ;; kk]], rhs[[1 ;; kk]]], $Failed];
     If[sol === $Failed, AppendTo[results, {minusPos, Length[pts], "sing", None}]; Continue[]];
     ok = AllTrue[Range[Length[pts]], (mons . sol /. Thread[vars -> pts[[#, 3, 1 ;; n - 1]]]) == rhs[[#]] &];
     AppendTo[results, {minusPos, Length[pts], If[ok, "EXACT", "INCON"], mons . sol}];
    ], {gi, Length[groups]}];
  results = SortBy[results, {#[[1]] &, #[[2]] &}];
  Do[Module[{r = results[[i]]},
     Print["  minus@", r[[1]], " n=", r[[2]], " ", r[[3]],
        If[r[[4]] =!= None, "  R = " <> ToString[Factor[r[[4]]] /. muSym[j_] :> Symbol["mu" <> ToString[j]], InputForm], ""]];
    ], {i, Length[results]}];
  results];
