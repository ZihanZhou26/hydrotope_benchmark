code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
amp[fw_]:=Module[{sig={-1,-1,1,1,1},ks,ws,A},{ks,ws}=MakeKinematics[5,fw,sig,1];A=BGAmplitude[ks,ws,1]/(-I);{ws,FullSimplify[A]}];
Do[res=amp[{-a,3,7}]; Print["a=",a," ws=",InputForm[res[[1]]]," B=",InputForm[res[[2]]]," ratios: B/a? ",InputForm[FullSimplify[res[[2]]/a]]," B/a^5=",InputForm[FullSimplify[res[[2]]/a^5]]];,{a,{1/5,1/2,1,2,5}}]
