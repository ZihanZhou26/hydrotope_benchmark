code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
amp[n_,fw_]:=Module[{sig=Join[{-1,-1},Table[1,n-2]],ks,ws,A,F},{ks,ws}=MakeKinematics[n,fw,sig,1];A=Quiet[BGAmplitude[ks,ws,1]];F=I*2^(n-1)*ws[[1]]*ws[[2]]^(2n-5);Print["fw=",fw," ws=",ws," BG=",InputForm[A]," F=",InputForm[F]," diff=",InputForm[FullSimplify[A-F]]]];
Scan[amp[5,#]&, {{10,1,1},{10,1,2},{10,2,3},{5,1/2,1},{5,1,2},{1,1/10,1/5}}]
