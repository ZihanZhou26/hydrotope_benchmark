Get["BGcore.m"];
gVal = 1;
amp = Get["amp5_symbolic.m"];
{sortedGroups, monsR} = Get["n5_chambers.m"];
sigmas = {-1,-1,1,1,1};
{ksym, wsym} = MakeKinematics[5, {a,b,c}, sigmas, gVal];
w1f = wsym[[1]]; w5f = wsym[[5]];

resolveAt[fw_] := Module[{refpt, r},
  refpt = {a -> fw[[1]], b -> fw[[2]], c -> fw[[3]]};
  r = amp /. Abs[x_] :> Sign[N[x /. refpt, 60]]*x;
  Factor[Together[r]/(-I)]];

results = {};
Do[Module[{grp = sortedGroups[[gi]], ws0, fw, P5, m, ord},
   ws0 = grp[[1, 2]];
   fw = ws0[[2 ;; 4]]; (* w2,w3,w4 free *)
   P5 = Quiet@Check[resolveAt[fw], $Failed];
   m = ws0^2; ord = Ordering[m];
   AppendTo[results, {P5, ws0, ord}];
  ], {gi, Length[sortedGroups]}];

(* dedupe by P5 *)
distinct = GatherBy[results, Expand[#[[1]]] &];
Print["distinct P5 polynomials across signatures: ", Length[distinct]];
Do[Module[{d = distinct[[i]], P5, reps},
   P5 = d[[1, 1]]; reps = d[[All, 2]];
   Print["==== poly ", i, "  (", Length[d], " signatures) ===="];
   Print["   P5 = ", Factor[P5]];
   Do[Print["     rep w=", N[reps[[j]], 5], "  m-order=", d[[j, 3]]], {j, Length[reps]}];
  ], {i, Length[distinct]}];
Export["n5_polys.m", distinct];
