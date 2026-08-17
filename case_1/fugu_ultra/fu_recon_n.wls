(* Reconstruct A_n along a 1-parameter exact-rational slice and factor to expose poles. *)
Get["fu_defs.m"];
n=ToExpression[Environment["NN"]];
sig=Join[{-1,-1},Table[1,n-2]];
solveAll[ind_]:=Module[{w1,wm,a,b,w2,wlast,ws},
 (* ind = {w1,w3,w4,...,w_{n-1}} length n-2; solve w2(minus),wn(plus) *)
 w1=ind[[1]]; wm=ind[[2;;]]; (* w3..w_{n-1} plus legs, length n-3 *)
 a=-(w1+Total[wm]);
 b=-(-w1^2+Total[wm^2]);
 wlast=(a+b/a)/2; w2=(a-b/a)/2;
 Join[{w1,w2},wm,{wlast}]];
(* slice: w1=t, others fixed rational *)
fixed=Table[Prime[i+2],{i,1,n-3}]/3;  (* w3..w_{n-1} *)
data={};
Do[
 ind=Join[{t},fixed];
 ws=solveAll[ind];
 If[!FreeQ[ws,ComplexInfinity]||MemberQ[ws,0],Continue[]];
 ks=sig*ws^2;
 amp=Quiet[Check[BGAmplitude[ks,ws,1]/I,$Failed]];
 If[amp=!=$Failed&&FreeQ[amp,Indeterminate|ComplexInfinity],AppendTo[data,{t,amp}]];
,{t,Join[Range[10,80]/7,Range[-60,-10]/7]}];
Print["n=",n," pts=",Length[data]];
Clear[x];
Do[
 np=dn;dq=dn;
 cP=Table[Symbol["aa"<>ToString[i]],{i,0,np}];cQ=Join[{1},Table[Symbol["bb"<>ToString[i]],{i,1,dq}]];
 eqs=Table[(cP.(d[[1]]^Range[0,np]))==d[[2]]*(cQ.(d[[1]]^Range[0,dq])),{d,data}];
 sol=Quiet[Solve[eqs,Join[cP,Rest[cQ]]]];
 If[sol=!={},s2=sol[[1]];P2=(cP.(x^Range[0,np]))/.s2;Q2=(cQ.(x^Range[0,dq]))/.s2;
  Print["min deg=",dn];Print["DENOM=",Factor[Q2]];Print["NUMER=",Factor[P2]];Break[]];
,{dn,Range[2,16]}];
