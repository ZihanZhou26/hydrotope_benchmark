<< bg_core.m
g = 1;
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];
amp[ws_, sig_] := Block[{ks = sig*ws^2/g, a},
  a = Quiet@Check[BGAmplitude[ks, ws, g], $Failed];
  If[a===Indeterminate||a===ComplexInfinity, $Failed, a]];

stream = OpenWrite["data.txt"];
emit[n_, ws_, a_] := If[a =!= $Failed,
  WriteString[stream, ToString[n], " | ",
    StringReplace[ToString[InputForm[ws]], {" "->""}], " | ",
    StringReplace[ToString[InputForm[a]], {" "->""}], "\n"]];

(* free-frequency lists per n: deterministic, generic-ish *)
free5 = {{2,3,5},{2,3,7},{3,5,7},{2,5,7},{1,2,3},{2,4,7},{3,4,5},{1,4,9},
  {2,3,11},{5,7,11},{1,3,8},{2,7,9},{3,8,13},{4,5,11},{1,6,10},{2,9,13},
  {3,7,8},{5,6,13},{1,2,8},{4,7,12},{2,3,5/2},{3/2,5,7},{1,5/2,4},{7/2,4,9},
  {2,11/3,5},{3,4,17},{1,7,15},{2,5,19},{6,7,8},{1,2,17}};
free6 = {{2,3,5,7},{1,2,3,5},{3,5,7,11},{2,3,5,11},{1,3,7,9},{2,4,6,9},
  {1,2,4,8},{3,4,5,7},{2,5,7,11},{1,4,6,13},{2,3,7,8},{5,6,7,11},
  {1,2,3,17},{3,5,8,9},{2,7,11,13},{1,3,5/2,4},{2,3,5,19},{4,5,6,7},
  {1,2,9,10},{3,7,8,15}};
free7 = {{2,3,5,7,11},{1,2,3,5,7},{2,3,5,7,13},{1,3,5,9,11},{2,4,6,8,11},
  {3,5,7,11,13},{1,2,4,7,9},{2,3,5,8,12},{1,4,6,9,15},{3,4,5,7,11},
  {2,5,7,11,17},{1,2,3,4,19},{3,6,7,9,13},{2,3,7,8,15}};

Do[Block[{s=twoMinusSigma[5],ks,ws,a},{ks,ws}=MakeKinematics[5,fw,s,g];emit[5,ws,amp[ws,s]]],{fw,free5}];
Do[Block[{s=twoMinusSigma[6],ks,ws,a},{ks,ws}=MakeKinematics[6,fw,s,g];emit[6,ws,amp[ws,s]]],{fw,free6}];
Do[Block[{s=twoMinusSigma[7],ks,ws,a},{ks,ws}=MakeKinematics[7,fw,s,g];emit[7,ws,amp[ws,s]]],{fw,free7}];
Close[stream];
Print["done. line count:"];
Print[Length[ReadList["data.txt","String"]]];
