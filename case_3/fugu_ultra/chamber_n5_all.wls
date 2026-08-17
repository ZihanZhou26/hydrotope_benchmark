Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
Clear[x,y,z];
sig={-1,-1,1,1,1};
{ks,ws}=MakeKinematics[5,{x,y,z},sig,1];
A=BGAmplitude[ks,ws,1];
B=A/(-I); (* B should be polynomial-ish over (x+y+z) *)
ChamberSimplify[expr_, sampleRules_] := Module[{absArgs, rules},
  absArgs = DeleteDuplicates[Cases[Unevaluated[expr], Abs[u_] :> u, Infinity]];
  rules = Table[With[{val=N[arg /. sampleRules,50]}, Abs[arg] -> If[val >= 0, arg, -arg]], {arg, absArgs}];
  FullSimplify[expr /. rules]
];
(* sample points covering different sign chambers of the free freqs x(leg2),y(leg3),z(leg4) *)
cases={
 {"all pos, x small",{x->1,y->3,z->7}},
 {"x neg",{x->-1,y->3,z->7}},
 {"y neg",{x->2,y->-3,z->7}},
 {"x neg y neg",{x->-1,y->-3,z->7}},
 {"x neg z neg",{x->-2,y->5,z->-3}},
 {"all neg",{x->-2,y->-3,z->-7}}
};
Scan[(nm=#[[1]]; rl=#[[2]];
  {ks2,ws2}=MakeKinematics[5,{x,y,z}/.rl,sig,1];
  S=TimeConstrained[ChamberSimplify[B, rl],25,$Failed];
  Print["=== ",nm," ws=",InputForm[ws2]];
  Print["    B=",InputForm[S]];
)&, cases]
