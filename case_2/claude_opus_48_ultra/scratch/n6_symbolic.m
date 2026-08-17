Get["BGcore.m"];
gVal = 1;
sigmas = {-1, -1, 1, 1, 1, 1};
(* free legs 2..5 = a,b,c,d ; leg1 minus & leg6 plus are dependent *)
{ks, ws} = MakeKinematics[6, {a, b, c, d}, sigmas, gVal];
Print["ws = ", ws // Simplify];
t = AbsoluteTiming[amp = BGAmplitude[ks, ws, gVal];][[1]];
Print["time = ", t];
Print["LeafCount amp6 = ", LeafCount[amp]];
Put[amp, "amp6_symbolic.m"];
Print["saved amp6_symbolic.m"];
