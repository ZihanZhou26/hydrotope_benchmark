Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
SeedRandom[42];
(* Agent2-style channel test: does exactly one of legs {1,2} share freq-sign
   with exactly n-3 of the plus legs 3..n? *)
channelOK[ws_]:=Module[{n=Length[ws],m,cands},
  m=n-3;
  cands=Select[{1,2},Function[a,Length[Select[Range[3,n],Sign[ws[[#]]]==Sign[ws[[a]]]&]]==m]];
  Length[cands]>=1];
Do[
  fails=0; tot=0;
  Do[
    free=Table[RandomInteger[{-6,6}]+RandomChoice[{1/2,1/3,1,3/2}],{n-2}];
    free=DeleteCases[free,0];
    If[Length[free]!=n-2,Continue[]];
    sig=Join[{-1,-1},Table[1,n-2]];
    {ks,ws}=MakeKinematics[n,free,sig,1];
    If[MemberQ[ws,0],Continue[]];
    tot++;
    If[!channelOK[ws],fails++],
    {200}];
  Print["n=",n," random signed-free points: ",tot," tested, channel-fail (Agent2 $Failed) = ",fails],
  {n,{4,5,6,7}}]
