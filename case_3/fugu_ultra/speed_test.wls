Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
(* try high-precision numeric *)
sig=Join[{-1,-1},Table[1,5]];
free=N[{3/2,2,5/2,3,7/2},40];
{ks,ws}=MakeKinematics[7,free,sig,1];
t=AbsoluteTiming[a=BGAmplitude[ks,ws,1];][[1]];
Print["n=7 numeric(40dig) time=",t," A=",a];
free=N[{3/2,2,5/2,3,7/2,4,9/2},40];
{ks,ws}=MakeKinematics[9,free,sig=Join[{-1,-1},Table[1,7]],1];
t=AbsoluteTiming[a=BGAmplitude[ks,ws,1];][[1]];
Print["n=9 numeric(40dig) time=",t," A=",a];
