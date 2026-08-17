Get["fu_defs.m"];
sig={-1,-1,1,1,1};
SeedRandom[42];
data={};
trials=0;
While[Length[data]<90 && trials<400,
 trials++;
 fw=Table[RandomInteger[{1,15}],{3}];  (* w2(minus free),w3,w4 plus *)
 {ks,ws}=Quiet[Check[MakeKinematics[5,fw,sig,1],$Failed]];
 If[ws===$Failed,Continue[]];
 amp=Quiet[Check[BGAmplitude[ks,ws,1]/I,$Failed]];
 If[amp=!=$Failed&&FreeQ[amp,Indeterminate|ComplexInfinity]&&FreeQ[ws,Complex],
   plus=ws[[3;;]]; e1=Total[plus]; e2=Total[Times@@@Subsets[plus,{2}]]; e3=Times@@plus;
   If[FreeQ[{e1,e2,e3},0], AppendTo[data,{e1,e2,e3,amp}]]];
];
Print["data pts=",Length[data]];
mons[deg_]:=Select[Flatten[Table[{a,b,c},{a,0,deg},{b,0,Floor[deg/2]},{c,0,Floor[deg/3]}],2],#[[1]]+2#[[2]]+3#[[3]]==deg&];
Do[
 wden=wd; monN=mons[6+wden]; monD=mons[wden]; nN=Length[monN]; nD=Length[monD];
 If[Length[data]<nN+nD+3, Print["wden=",wden," need more data ",nN+nD]; Continue[]];
 rows=Table[Join[-(((d[[1]]^#[[1]] d[[2]]^#[[2]] d[[3]]^#[[3]])&/@monN)),
        d[[4]]*(((d[[1]]^#[[1]] d[[2]]^#[[2]] d[[3]]^#[[3]])&/@monD))],{d,data}];
 ns=NullSpace[rows];
 Print["wden=",wden," nN=",nN," nD=",nD," nulldim=",Length[ns]];
 If[Length[ns]==1,
   sol=ns[[1]]; cN=sol[[1;;nN]]; cD=sol[[nN+1;;]];
   Clear[E1,E2,E3];
   Npoly=Sum[cN[[i]] E1^monN[[i,1]] E2^monN[[i,2]] E3^monN[[i,3]],{i,nN}];
   Dpoly=Sum[cD[[j]] E1^monD[[j,1]] E2^monD[[j,2]] E3^monD[[j,3]],{j,nD}];
   Print["  N/D=",Factor[Npoly/Dpoly]];
 ];
,{wd,{6,8,10}}];
