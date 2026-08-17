Get["fu_defs.m"];
sig={-1,-1,1,1,1};
(* plus legs p1,p2 fixed rational, p3=t varies. minus legs = roots of x^2+e1 x+e2. *)
p1=7;p2=5;
mk[t_]:=Module[{e1,e2,disc,r,m1,m2},
 e1=p1+p2+t; e2=p1 p2+p1 t+p2 t;
 disc=e1^2-4 e2; r=Sqrt[disc];
 m1=(-e1+r)/2; m2=(-e1-r)/2;
 {{-m1^2,-m2^2,p1^2,p2^2,t^2}, {m1,m2,p1,p2,t}}];
data={};
Do[
 {ks,ws}=mk[t];
 amp=Quiet[Check[Simplify[BGAmplitude[ks,ws,1]/I],$Failed]];
 If[amp=!=$Failed&&FreeQ[amp,Indeterminate|ComplexInfinity|Root]&&Element[amp,Rationals],
   AppendTo[data,{t,amp}]];
,{t,Range[20,75]/9}];
Print["rational pts=",Length[data]];
If[Length[data]>=8, Print["sample ",Take[data,3]]];
Clear[x];
Do[
 np=dn;dq=dn;
 cP=Table[Symbol["aa"<>ToString[i]],{i,0,np}];
 cQ=Join[{1},Table[Symbol["bb"<>ToString[i]],{i,1,dq}]];
 eqs=Table[(cP.(d[[1]]^Range[0,np]))==d[[2]]*(cQ.(d[[1]]^Range[0,dq])),{d,data}];
 sol=Quiet[Solve[eqs,Join[cP,Rest[cQ]]]];
 If[sol=!={},
  s2=sol[[1]];P2=(cP.(x^Range[0,np]))/.s2;Q2=(cQ.(x^Range[0,dq]))/.s2;
  Print["min deg=",dn];
  Print["Numerator(t)=",Factor[P2]];
  Print["Denominator(t)=",Factor[Q2]];
  Print["A(t)=",Factor[P2/Q2]];
  Break[]];
,{dn,Range[2,10]}];
