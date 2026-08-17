Get["BGcore.m"];
gVal = 1;
pw[x_, d_] := If[x > 0, x^d, 0];
Aformula[ws_List] := Module[{n = Length[ws], m, a, plus, d, subs},
  n = Length[ws]; m = ws^2; a = Min[m[[1]], m[[2]]]; plus = m[[3 ;;]]; d = n - 3;
  subs = Subsets[plus];
  I*2^(n - 1)*ws[[1]]*ws[[2]]*Total[((-1)^Length[#]) pw[a - Total[#], d] & /@ subs]];
n = 8; sig = Join[{-1, -1}, Table[1, n - 2]];
tests = {{1, 2, 3, 4, 5, 6}, {3/2, 5/2, 1, 4, 2, 7/2}, {-2, 3, 5, 1, 6, 2}};
Do[Module[{fw = tc, ks, ws, amp, af},
   {ks, ws} = MakeKinematics[n, fw, sig, gVal];
   amp = BGAmplitude[ks, ws, gVal];
   af = Aformula[ws];
   Print["fw=", fw];
   Print["  BG       = ", amp];
   Print["  formula  = ", af];
   Print["  equal?     ", Simplify[amp - af] === 0, "   rel.err = ", If[amp==0,Abs@N[af],N[Abs[(amp - af)/amp], 20]]];
  ], {tc, tests}];
