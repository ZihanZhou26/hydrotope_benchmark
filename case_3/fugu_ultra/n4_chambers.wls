Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
Clear[x,y];
sig={-1,-1,1,1};
{ks,ws}=MakeKinematics[4,{x,y},sig,1];
Print["ws=",InputForm[ws]];
A=BGAmplitude[ks,ws,1];
ChamberSimplify[expr_, sr_] := Module[{absArgs, rules},
  absArgs = DeleteDuplicates[Cases[Unevaluated[expr], Abs[u_] :> u, Infinity]];
  rules = Table[With[{val=N[arg /. sr,50]}, Abs[arg] -> If[val >= 0, arg, -arg]], {arg, absArgs}];
  FullSimplify[expr /. rules]];
cases={
 {"x>0,y>0,x<y",{x->1,y->3}},
 {"x>0,y>0,x>y",{x->3,y->1}},
 {"x<0,y>0",{x->-1,y->3}},
 {"x>0,y<0",{x->2,y->-3}},
 {"x<0,y<0",{x->-2,y->-3}}
};
Scan[(nm=#[[1]]; rl=#[[2]];
  {ks2,ws2}=MakeKinematics[4,{x,y}/.rl,sig,1];
  bgnum=Quiet[BGAmplitude[ks2,ws2,1]];
  S=TimeConstrained[ChamberSimplify[A,rl],25,$Failed];
  Print["=== ",nm," ws=",InputForm[ws2]," bg=",InputForm[bgnum]];
  Print["    A=",InputForm[S]];
)&, cases]
