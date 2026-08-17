Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
(* For positive free freqs, check signs of solved w1 (minus leg) and wn (plus leg). *)
SeedRandom[5];
Do[
 cnt=0; w1pos=0; wnpos=0; canonicalChannel=0;
 Do[
   free=N[Table[RandomReal[{0.05,8}],{n-2}],30];
   sig=Join[{-1,-1},Table[1,n-2]];
   {ks,ws}=MakeKinematics[n,free,sig,1];
   cnt++;
   If[ws[[1]]>0,w1pos++];
   If[ws[[n]]>0,wnpos++];
   (* canonical channel: leg2 positive, R={3..n-1} are positive plus legs of size n-3 *)
   Rpos=Select[Range[3,n],ws[[#]]>0&];
   If[ws[[2]]>0 && Sort[Rpos]==Range[3,n-1], canonicalChannel++],
   {500}];
 Print["n=",n,": pts=",cnt,", w1>0 count=",w1pos,", wn>0 count=",wnpos,", canonical-channel count=",canonicalChannel],
 {n,{4,5,6,7,8}}]
