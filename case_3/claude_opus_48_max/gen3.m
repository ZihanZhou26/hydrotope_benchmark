<< bg_core.m
g = 1;
amp[ws_, sig_] := Block[{ks = sig*ws^2/g, a},
  a = Quiet@Check[BGAmplitude[ks, ws, g], $Failed];
  If[a===Indeterminate||a===ComplexInfinity, $Failed, a]];

Print["==== PERMUTATION SYMMETRY TESTS (n=5) ===="];
sig = {-1,-1,1,1,1};
w0 = {-13/2, 2, 3, 5, -7/2};
Print["base w=", w0, " A=", amp[w0, sig]];
(* swap plus legs 3<->4 *)
Print["swap +legs (3,4): w=", w0[[{1,2,4,3,5}]], " A=", amp[w0[[{1,2,4,3,5}]], sig]];
Print["swap +legs (3,5): w=", w0[[{1,2,5,4,3}]], " A=", amp[w0[[{1,2,5,4,3}]], sig]];
Print["swap +legs (4,5): w=", w0[[{1,2,3,5,4}]], " A=", amp[w0[[{1,2,3,5,4}]], sig]];
(* swap minus legs 1<->2 *)
Print["swap -legs (1,2): w=", w0[[{2,1,3,4,5}]], " A=", amp[w0[[{2,1,3,4,5}]], sig]];
Print[""];

Print["==== more n=5 data points (freeW -> full w, A) ===="];
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];
pts5 = {{2,3,5},{2,3,7},{3,5,7},{2,5,7},{1,2,3},{2,4,7},{3,4,5},{1,4,9},{2,3,11},{5,7,11}};
Do[Block[{s=twoMinusSigma[5],ks,ws,a},
  {ks,ws}=MakeKinematics[5,fw,s,g]; a=amp[ws,s];
  Print[" fw=",fw,"  w=",ws,"  A=",a]], {fw,pts5}];
