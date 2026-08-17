code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
ampcase[n_,fw_]:=Module[{sigmas,ks,ws,amp},sigmas=Join[{-1,-1},Table[1,n-2]];{ks,ws}=MakeKinematics[n,fw,sigmas,1];amp=Quiet[BGAmplitude[ks,ws,1]];Print["n=",n," fw=",fw," ws=",ws," B=",InputForm[FullSimplify[amp/(-I)]]];];
Scan[ampcase@@#&, {{5,{2,-3,-7}}, {5,{1,-3,-7}}, {5,{5,-3,-7}}, {5,{-2,-5/2,-3}}, {6,{3/2,-2,-5/2,-3}}, {6,{1,-3,-5,-7}}}]
