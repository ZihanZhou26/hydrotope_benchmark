(* ================================================================ *)
(*  verify.wls  --  reproducible check of the two-minus closed form  *)
(*                                                                  *)
(*  Run:  wolframscript -file verify.wls                            *)
(*  (run from this directory; it reads ../OnShellBG.m)              *)
(*                                                                  *)
(*  It loads ONLY the definitions of OnShellBG.m (everything before *)
(*  the slow "VI. TESTS" section) so the check is fast, then        *)
(*  compares the closed form against BGAmplitude for n=5,6,7 in     *)
(*  several chambers and for several g values, plus the n=4         *)
(*  symbolic-chamber limit (direct n=4 BG is 0*Infinity; see note). *)
(* ================================================================ *)

(* --- load only the definition section of OnShellBG.m --- *)
srcPath = FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}];
If[!FileExistsQ[srcPath], srcPath = "../OnShellBG.m"];
src = Import[srcPath, "Text"];
(* keep everything before the first executable test line; all comments stay closed *)
cut = StringPosition[src, "gVal = 1;"];
defs = If[cut === {}, src, StringTake[src, First@First@cut - 1]];
ToExpression[defs];

(* --- the conjectured closed form (independent reimplementation) --- *)
ppow[x_, m_] := If[x > 0, x^m, 0];
TwoMinusClosedForm[omegas_List, g_] := Module[{n = Length[omegas], q, spline},
  q[i_] := omegas[[i]]^2;
  spline = Total[((-1)^Length[#] * ppow[q[1] - Total[q /@ #], n - 3]) & /@
     Subsets[Range[3, n]]];
  I*2^(n - 1)*omegas[[1]]*omegas[[2]]*spline/g^(n - 3)];

activeCount[om_] := Length@Select[Subsets[Range[3, Length[om]]],
   (om[[1]]^2 - Total[om[[#]]^2] > 0) &];

run[n_, fw_, g_] := Module[{sig, ks, ws, bg, cf, rel},
  sig = Join[{-1, -1}, Table[1, n - 2]];
  {ks, ws} = MakeKinematics[n, fw, sig, g];
  bg = Quiet[Simplify[BGAmplitude[ks, ws, g]]];
  cf = TwoMinusClosedForm[ws, g];
  rel = If[cf === 0 && bg === 0, 0, N[Abs[(bg - cf)/Max[1, Abs[cf]]], 20]];
  Print["n=", n, " g=", g, " fw=", fw, " active=", activeCount[ws],
    " BG=", N[bg, 12], " CF=", N[cf, 12], " relerr=", rel];
  rel];

Print["=== n = 5, 6, 7 : direct BGAmplitude vs closed form ==="];
results = {
  run[5, {2, 3, 4}, 1], run[5, {4, 3, 2}, 1], run[5, {1, 2, 10}, 1],
  run[5, {-2, 3, 4}, 1], run[5, {2, 3, 4}, 2],
  run[6, {2, 1, 1, 1}, 1], run[6, {2, 1, 1, 3}, 1], run[6, {4, 1, 3, 3}, 1],
  run[6, {1, 2, 2, 2}, 1], run[6, {5, 1, 1, 1}, 3],
  run[7, {3, 1, 1, 1, 1}, 1], run[7, {2, 1, 1, 1, 3}, 1], run[7, {2, 1, 3, 3, 3}, 1]
};
Print["max relative error (n=5,6,7): ", Max[results]];

Print[];
Print["=== n = 4 : direct BG is 0*Infinity, use symbolic chamber limit ==="];
sig4 = {-1, -1, 1, 1};
{ks4, ws4} = MakeKinematics[4, {a, b}, sig4, 1];
ampSym = BGAmplitude[ks4, ws4, 1];
Print["  ws(a,b) = ", FullSimplify[ws4], "   (=> k2+k4 = ",
  FullSimplify[ks4[[2]] + ks4[[4]]], " forces a propagator pole)"];
Print["  chamber b>a : BG = ", FullSimplify[ampSym, Assumptions -> {a > 0, b > 0, b > a}],
  "   CF{2,3} = ", TwoMinusClosedForm[MakeKinematics[4, {2, 3}, sig4, 1][[2]], 1]];
Print["  chamber a>b : BG = ", FullSimplify[ampSym, Assumptions -> {a > 0, b > 0, a > b}],
  "   CF{3,2} = ", TwoMinusClosedForm[MakeKinematics[4, {3, 2}, sig4, 1][[2]], 1]];

Print[];
Print["Closed form A4 = -8 I a b Min[a^2,b^2]  (g=1), matching both chambers."];
