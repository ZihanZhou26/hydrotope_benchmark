Get["BGcore.m"];
gVal = 1;

(* n=5 symbolic free frequencies a=w2,b=w3,c=w4 *)
sigmas = {-1, -1, 1, 1, 1};
{ks, ws} = MakeKinematics[5, {a, b, c}, sigmas, gVal];
Print["ws (symbolic) = ", ws];
Print["ks (symbolic) = ", ks];
Print["--- computing A_5 symbolic ---"];
t = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal];][[1]];
Print["time = ", t];
Print["LeafCount = ", LeafCount[amp]];
absargs = DeleteDuplicates[Cases[amp, Abs[x_] :> x, Infinity]];
Print["Abs arguments appearing:"];
Do[Print["   Abs[ ", Simplify[a2], " ]"], {a2, absargs}];
(* Save raw amp to a file *)
Put[amp, "amp5_symbolic.m"];
Print["saved amp5_symbolic.m"];
