Get["fu_defs.m"];
n=ToExpression[Environment["NN"]];
sig=Join[{-1,-1},Table[1,n-2]];
solveAll[ind_]:=Module[{w1,wm,a,b,w2,wlast},
 w1=ind[[1]];wm=ind[[2;;]];a=-(w1+Total[wm]);b=-(-w1^2+Total[wm^2]);
 wlast=(a+b/a)/2;w2=(a-b/a)/2;Join[{w1,w2},wm,{wlast}]];
(* chamber label = signs of k_S = sum sigma_i w_i^2 over subsets; but Abs only applied in kernels/propagator to k of subsets that appear. Use ALL proper-subset sums. *)
subs=Select[Subsets[Range[n]],1<=Length[#]<=n-1&];
kc[ws_]:=Sign[Total[(sig*ws^2)[[#]]]]&/@subs;
fixed=Table[Prime[i+2],{i,1,n-3}]/3;
ref=solveAll[Join[{-9/2},fixed]];
refc=kc[ref];
data={};
Do[
 ind=Join[{t},fixed];ws=solveAll[ind];
 If[!FreeQ[ws,ComplexInfinity]||MemberQ[ws,0],Continue[]];
 If[kc[ws]=!=refc,Continue[]];
 ks=sig*ws^2;amp=Quiet[Check[BGAmplitude[ks,ws,1]/I,$Failed]];
 If[amp=!=$Failed&&FreeQ[amp,Indeterminate|ComplexInfinity],AppendTo[data,{t,amp}]];
,{t,Join[Range[10,120]/7,Range[-120,-10]/7]}];
Print["n=",n," one-chamber pts=",Length[data]];
Clear[x];
Do[np=dn;dq=dn;
 cP=Table[Symbol["aa"<>ToString[i]],{i,0,np}];cQ=Join[{1},Table[Symbol["bb"<>ToString[i]],{i,1,dq}]];
 eqs=Table[(cP.(d[[1]]^Range[0,np]))==d[[2]]*(cQ.(d[[1]]^Range[0,dq])),{d,data}];
 sol=Quiet[Solve[eqs,Join[cP,Rest[cQ]]]];
 If[sol=!={},s2=sol[[1]];P2=(cP.(x^Range[0,np]))/.s2;Q2=(cQ.(x^Range[0,dq]))/.s2;
  Print["min deg=",dn];Print["DENOM=",Factor[Q2]];Print["NUMER=",Factor[P2]];Break[]];
,{dn,Range[2,16]}];
