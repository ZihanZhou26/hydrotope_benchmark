code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
amp4[w2_,w3_,g_]:=Module[{eps,ws,sig,ks,amp},sig={-1,-1,1,1};ws={-w3-eps,w2,w3,-w2+eps};ks=sig*ws^2/g;amp=Quiet[BGAmplitude[ks,ws,g]];FullSimplify[Limit[amp,eps->0,Direction->"FromAbove"]]];
Do[Print[{w2,w3,g}," -> ",InputForm[amp4[w2,w3,g]]," formula ",InputForm[I*8*(-w3)*w2^3/g]],{w2,{2,5}},{w3,{3,1/2}},{g,{1,2}}]
