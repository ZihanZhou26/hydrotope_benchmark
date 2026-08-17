Get["fu_defs.m"];
sig={-1,-1,1,1,1};
(* One-parameter exact family: free freqs {s, 7, 5} -> w2=s(minus), w3=7,w4=5(plus); solver gives w1(minus),w5(plus). Reconstruct A(s) exactly. *)
data={};
Do[
 fw={s,7,5};
 {ks,ws}=Quiet[Check[MakeKinematics[5,fw,sig,1],$Failed]];
 If[ws===$Failed,Continue[]];
 amp=Quiet[Check[BGAmplitude[ks,ws,1]/I,$Failed]];
 If[amp=!=$Failed&&FreeQ[amp,Indeterminate|ComplexInfinity],AppendTo[data,{s,amp}]];
,{s,Join[Range[20,80]/9, Range[-40,-10]/9]}];
Print["pts=",Length[data]];
Clear[x];
Do[
 np=dn;dq=dn;
 cP=Table[Symbol["aa"<>ToString[i]],{i,0,np}];
 cQ=Join[{1},Table[Symbol["bb"<>ToString[i]],{i,1,dq}]];
 eqs=Table[(cP.(d[[1]]^Range[0,np]))==d[[2]]*(cQ.(d[[1]]^Range[0,dq])),{d,data}];
 sol=Quiet[Solve[eqs,Join[cP,Rest[cQ]]]];
 If[sol=!={},
  s2=sol[[1]];P2=(cP.(x^Range[0,np]))/.s2;Q2=(cQ.(x^Range[0,dq]))/.s2;
  Print["min working deg=",dn];
  Print["Numerator   = ",Factor[P2]];
  Print["Denominator = ",Factor[Q2]];
  Break[]];
,{dn,Range[3,12]}];
