code=Import[FileNameJoin[{DirectoryName[$InputFileName],"..","OnShellBG.m"}],"Text"]; defs=StringSplit[code,"(* ================================================================ *)\n(*  VI. TESTS"][[1]]; ToExpression[defs];
Clear[x,y,z,ChamberSimplify]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{x,y,z},sig,1]; A=BGAmplitude[ks,ws,1]/(-I);
ChamberSimplify[expr_, sampleRules_] := Module[{absArgs, rules},
  absArgs = DeleteDuplicates[Cases[Unevaluated[expr], Abs[u_] :> u, Infinity]];
  rules = Table[With[{val=N[arg /. sampleRules,50]}, Abs[arg] -> If[val >= 0, arg, -arg]], {arg, absArgs}];
  FullSimplify[expr /. rules]
];
cases={{"x-small",{x->1,y->3,z->7}}, {"x-large-yz",{x->10,y->1,z->1}}, {"mid",{x->2,y->1,z->5}}, {"mid2",{x->2,y->5,z->1}}};
Scan[(name=#[[1]]; rules=#[[2]];
  Print["--- sample ", name, " ", rules, " ---"];
  S=TimeConstrained[ChamberSimplify[A, rules], 20, $Failed];
  Print["S=",InputForm[S]];
  If[S =!= $Failed, Print["diff simple=",InputForm[FullSimplify[S + 16*ws[[1]]*x^5]]]];
)&, cases]
