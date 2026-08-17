(* Decisive test: does R = (n-4)! Sum_{S subset Plus} (-1)^|S| (a - sigma_S)_+^(n-3) match ALL data?
   a = min(minus magnitudes); Plus = plus-leg magnitudes. *)
pw[x_, d_] := If[x > 0, x^d, 0];

Rcand[n_, ws_] := Module[{m, a, plus, d = n - 3, subs},
  m = ws^2; a = Min[m[[1]], m[[2]]]; plus = m[[3 ;;]];
  subs = Subsets[plus];
  2^(n - 5) * Total[((-1)^Length[#]) * pw[a - Total[#], d] & /@ subs]];

testAll[n_, raw_] := Module[{errs, bad},
  errs = Table[
     Module[{ws = e[[1]], P = e[[2]], Ract, Rc},
      Ract = P/(-16 ws[[1]]*ws[[2]]);
      Rc = Rcand[n, ws];
      {Ract - Rc, ws, Ract, Rc}], {e, raw}];
  bad = Select[errs, #[[1]] != 0 &];
  Print["n=", n, ": ", Length[raw], " pts; mismatches = ", Length[bad]];
  If[Length[bad] > 0,
    Print["  first few mismatches (Ract, Rcand):"];
    Do[Print["   ", N[bad[[i, 3]]], " vs ", N[bad[[i, 4]]], "  diff=", N[bad[[i,1]]],
             "  m=", N[Sort[bad[[i,2]]^2],4]], {i, Min[5, Length[bad]]}]];
  Length[bad]];
