code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
Clear[amp4eps];
amp4eps[eps_] := Module[{ws, sig, ks}, sig={-1,-1,1,1}; ws={-3-eps, 2, 3, -2+eps}; ks=sig*ws^2; Quiet[BGAmplitude[ks,ws,1]]];
Do[A=amp4eps[eps]; Print["eps=",eps," A=",N[A,30]," B=",N[A/(-I),30]];,{eps,{1/10,1/100,1/1000,-1/100,-1/1000}}]
(* Try exact series? *)
eps=Symbol["e"];
ws={-3-eps,2,3,-2+eps}; sig={-1,-1,1,1}; ks=sig*ws^2;
A=Quiet[BGAmplitude[ks,ws,1]];
Print["limit=",InputForm[FullSimplify[Limit[A, eps->0]]]];
