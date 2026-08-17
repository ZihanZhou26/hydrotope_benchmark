Get["BGcore.m"]; gVal=1;
(* combinatorial chamber = set of index-subsets of sorted plus legs with sigma_S < a *)
combChamber[ws_] := Module[{m=ws^2,a,plus,idx},
  a=Min[m[[1]],m[[2]]]; plus=Sort[m[[3;;]]]; idx=Range[Length[plus]];
  Sort[Select[Subsets[idx], Total[plus[[#]]] < a &]]];
Do[Module[{n=nn,sig,seen,cnt=0},
  sig=Join[{-1,-1},Table[1,n-2]]; seen={};
  SeedRandom[42];
  Do[Module[{fw,ks,ws},
    fw=Table[RandomChoice[{-1,-1,1,1,1}]RandomInteger[{1,40}]/RandomInteger[{1,7}],{n-2}];
    {ks,ws}=MakeKinematics[n,fw,sig,gVal];
    If[MemberQ[ws,0],Continue[]];
    AppendTo[seen, combChamber[ws]]; cnt++;
   ],{20000}];
  Print["n=",n,": realizable combinatorial chambers found = ",Length[DeleteDuplicates[seen]]," (from ",cnt," samples)"];
 ],{nn,{4,5,6,7,8}}];
