code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
sigmas={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{2,5/2,3},sigmas,1];
amp=BGAmplitude[ks,ws,1]/(-I);
ks2=ks[[{2,1,3,4,5}]]; ws2=ws[[{2,1,3,4,5}]];
amp2=BGAmplitude[ks2,ws2,1]/(-I);
Print["ws=",ws," B=",amp]; Print["swap12 ws=",ws2," B=",FullSimplify[amp2]];
Print["-16 w1 w2^5=", FullSimplify[-16 ws[[1]] ws[[2]]^5]];
Print["-16 w2 w1^5=", FullSimplify[-16 ws[[2]] ws[[1]]^5]];
