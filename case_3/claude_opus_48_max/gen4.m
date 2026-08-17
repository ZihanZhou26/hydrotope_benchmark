<< bg_core.m
g = 1;
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];
amp[ws_, sig_] := Block[{ks = sig*ws^2/g, a},
  a = Quiet@Check[BGAmplitude[ks, ws, g], $Failed];
  If[a===Indeterminate||a===ComplexInfinity, $Failed, a]];
mk[n_, fw_] := Block[{s=twoMinusSigma[n], ks, ws},
  {ks,ws}=MakeKinematics[n,fw,s,g]; {ws, amp[ws,s]}];

Print["==== n=4 data (w ; A) ===="];
pts4 = {{1,2},{1,3},{2,3},{1,4},{3,4},{2,5},{1,5},{4,5},{2,7},{3,7},{1,6},{5,6},{2,9},{4,9},{3,8}};
Do[Block[{ws,a}, {ws,a}=mk[4,fw];
  Print["  w=",ws,"  A=",a]], {fw,pts4}];
