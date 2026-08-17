Get["BGcore.m"]; gVal=1;
combChamber[ws_] := Module[{m=ws^2,a,plus,idx},
  a=Min[m[[1]],m[[2]]]; plus=Sort[m[[3;;]]]; idx=Range[Length[plus]];
  Sort[Select[Subsets[idx], Total[plus[[#]]] < a &]]];
Do[Module[{n=nn,sig,seen,cnt=0},
  sig=Join[{-1,-1},Table[1,n-2]]; seen={}; SeedRandom[7];
  Do[Module[{fw,ks,ws},
    fw=Table[RandomChoice[{-1,-1,1,1,1}]RandomInteger[{1,40}]/RandomInteger[{1,7}],{n-2}];
    If[Total[fw]==0, Continue[]];
    {ks,ws}=MakeKinematics[n,fw,sig,gVal];
    If[!FreeQ[ws,ComplexInfinity]||MemberQ[ws,0]||!VectorQ[ws,NumberQ], Continue[]];
    AppendTo[seen, combChamber[ws]]; cnt++;
   ],{30000}];
  Print["n=",n,": chambers = ",Length[DeleteDuplicates[seen]]," (clean samples=",cnt,")"];
 ],{nn,{4,5,6,7}}];
