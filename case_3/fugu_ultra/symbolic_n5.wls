code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
Clear[x,y,z]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{x,y,z},sig,1]; Print["ws=",InputForm[ws]];
A=BGAmplitude[ks,ws,1]/(-I);
Print["raw len ",StringLength[ToString[InputForm[A]]]];
ass1 = 0 < x < y < z && (* derived signs? *) True;
S1=TimeConstrained[FullSimplify[A, ass1], 20, $Failed]; Print["simp1=",InputForm[S1]];
Print["check vs -16 w1 x^5: ",InputForm[TimeConstrained[FullSimplify[S1 + 16*ws[[1]]*x^5, ass1], 10, $Failed]]];
ass2 = 0 < y < z < x;
S2=TimeConstrained[FullSimplify[A, ass2], 30, $Failed]; Print["simp2=",InputForm[S2]];
