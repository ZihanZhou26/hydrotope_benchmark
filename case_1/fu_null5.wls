Get["fu_defs.m"];
(* exact A5 at rational points via MakeKinematics; minus legs = w1,w2 *)
sig={-1,-1,1,1,1};
pts={{2,5/2,3},{3,4,5},{1,2,4},{3,5,7},{2,3,7},{4,5,9},{1,3,8},{2,5,11},{3,4,8},{2,7,9},
     {5,6,7},{1,4,6},{3,6,10},{2,4,11},{5,7,8},{1,2,9},{4,6,11},{3,7,8},{2,6,13},{5,8,9},
     {1,5,7},{4,9,10},{3,8,11},{2,9,13},{6,7,9},{1,3,10},{4,5,12},{7,8,11},{2,3,11},{5,9,13}};
data={};
Do[
 {ks,ws}=MakeKinematics[5,fw,sig,1];
 amp=Quiet[Check[BGAmplitude[ks,ws,1]/I,$Failed]];
 If[amp=!=$Failed&&FreeQ[amp,Indeterminate|ComplexInfinity],
   plus=ws[[3;;]]; e1=Total[plus]; e2=Total[Times@@@Subsets[plus,{2}]]; e3=Times@@plus;
   AppendTo[data,{e1,e2,e3,amp}]];
,{fw,pts}];
Print["data pts=",Length[data]];
(* homogeneous monomials in (e1,e2,e3) with weighted degree D for N (deg 6+w) and Dden (deg w) *)
mons[deg_]:=Select[Flatten[Table[{a,b,c},{a,0,deg},{b,0,Floor[deg/2]},{c,0,Floor[deg/3]}],2],#[[1]]+2#[[2]]+3#[[3]]==deg&];
(* try denominator weighted-degree w = 2,4,6 ; N degree 6+w *)
Do[
 wden=wd;
 monN=mons[6+wden]; monD=mons[wden];
 nN=Length[monN]; nD=Length[monD];
 (* unknowns: coeffs of N (nN) and D (nD). Equation per point: amp*D - N = 0 *)
 Clear[cn,cd];
 vars=Join[Table[cn[i],{i,nN}],Table[cd[j],{j,nD}]];
 rows=Table[
   Join[-(((d[[1]]^#[[1]] d[[2]]^#[[2]] d[[3]]^#[[3]])&/@monN)),
        d[[4]]*(((d[[1]]^#[[1]] d[[2]]^#[[2]] d[[3]]^#[[3]])&/@monD))]
 ,{d,data}];
 ns=NullSpace[rows];
 Print["wden=",wden," nN=",nN," nD=",nD," nulldim=",Length[ns]];
 If[Length[ns]>=1,
   sol=ns[[1]];
   cN=sol[[1;;nN]]; cD=sol[[nN+1;;]];
   Clear[E1,E2,E3];
   Npoly=Sum[cN[[i]] E1^monN[[i,1]] E2^monN[[i,2]] E3^monN[[i,3]],{i,nN}];
   Dpoly=Sum[cD[[j]] E1^monD[[j,1]] E2^monD[[j,2]] E3^monD[[j,3]],{j,nD}];
   Print["  N=",Factor[Npoly]];
   Print["  D=",Factor[Dpoly]];
   Print["  N/D=",Factor[Npoly/Dpoly]];
 ];
,{wd,{2,4}}];
