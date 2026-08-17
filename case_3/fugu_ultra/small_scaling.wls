code = Import[FileNameJoin[{DirectoryName[$InputFileName], "..", "OnShellBG.m"}], "Text"];
defs = StringSplit[code, "(* ================================================================ *)\n(*  VI. TESTS"][[1]];
ToExpression[defs];
TwoMinusAmp[n_, freeW_] := Module[{sigmas, ks, ws, amp}, sigmas=Join[{-1,-1},Table[1,n-2]]; {ks,ws}=MakeKinematics[n, freeW, sigmas, 1]; amp=BGAmplitude[ks,ws,1]; {ws,FullSimplify[amp]}];
Do[res=TwoMinusAmp[5,{a,3,7}]; Print["a=",a," ws=",N[res[[1]],20]," amp=",N[res[[2]]/(-I),30]];, {a,{1,1/2,1/5,1/10,1/20,1/50}}]
