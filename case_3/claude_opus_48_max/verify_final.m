<< bg_core.m
$MaxExtraPrecision=400;
twoMinusSigma[n_]:=Join[{-1,-1},Table[1,n-2]];
formula[n_,ws_,g_]:=I*2^(n-1)*g^(3-n)*(ws[[1]]*ws[[2]])*Min[ws[[1]]^2,ws[[2]]^2]^(n-3);
bg[ws_,sig_,g_]:=Block[{a},a=Quiet@Check[BGAmplitude[sig*ws^2/g,ws,g],$Failed];
  If[a===Indeterminate||a===ComplexInfinity,$Failed,a]];
inReg[ws_]:=Module[{mn=Min[ws[[1]]^2,ws[[2]]^2],pl=ws[[3;;]]^2},mn<=Min[pl]];
np=0;nf=0;nsk=0;mx=0;
chk[lab_,n_,ws_,g_]:=Block[{sig=twoMinusSigma[n],a,f,rel},
  If[!inReg[ws],nsk++;Return[]];
  a=bg[ws,sig,g];If[a===$Failed,nsk++;Return[]];f=formula[n,ws,g];
  rel=If[a===0,Abs[f],N[Abs[(a-f)/a],12]];
  If[rel===0||rel<10^-12,np++;mx=Max[mx,If[rel===0,0,rel]],
     nf++;Print["FAIL ",lab," n=",n," rel=",N[rel,5]," BG=",N[a,10]," F=",N[f,10]]]];
mkChk[lab_,n_,fw_,g_]:=Block[{sig=twoMinusSigma[n],ks,ws},
  {ks,ws}=MakeKinematics[n,fw,sig,g];chk[lab,n,ws,g]];
build[m1_,m2_,fp_,prec_]:=Block[{P,Q,Pp,Qp,d,x,y},
  P=-(m1+m2);Q=m1^2+m2^2;Pp=P-Total[fp];Qp=Q-Total[fp^2];d=2Qp-Pp^2;
  If[d<0,Return[$Failed]];x=(Pp+Sqrt[d])/2;y=(Pp-Sqrt[d])/2;
  N[Join[{m1,m2},fp,{x,y}],prec]];

Print["== A) MakeKinematics 'standard' (ordered free freqs, like benchmark tests) =="];
mkChk["std5a",5,{3/2,2,5/2},1];mkChk["std5b",5,{1,3,5},1];mkChk["std5c",5,{2,7,11},1];
mkChk["std6a",6,{3/2,2,5/2,3},1];mkChk["std6b",6,{1,3,5,7},1];mkChk["std6c",6,{2,3,7,11},1];
mkChk["std7a",7,{3/2,2,5/2,3,7/2},1];mkChk["std7b",7,{1,2,3,5,7},1];
mkChk["std8a",8,{1,2,3,4,5,6},1];

Print["== B) non-generic: one MINUS freq huge/tiny (in-regime) via buildPoint =="];
Do[chk["minusTiny5",5,build[1/1000,m2,{2,3},60],1],{m2,{2,3,5,-4}}];
Do[chk["minusHugeOK5",5,build[m1,3,{50,60},60],1],{m1,{1,2,-1}}];(* plus legs huge -> minus soft *)
chk["minusTiny6",6,build[1/500,4,{2,3,5},60],1];
chk["minusTiny7",7,build[1/200,5,{2,3,4,6},60],1];

Print["== C) non-generic: one PLUS freq HUGE (minus still softest, in-regime) =="];
mkChk["plusHuge5",5,{2,3,1000},1];      (* w2=2 soft minus; plus 1000 huge *)
mkChk["plusHuge6",6,{3/2,2,5/2,5000},1];
mkChk["plusHuge7",7,{1,2,5/2,3,10000},1];

Print["== D) smaller minus leg via buildPoint, both signs, in-regime only =="];
Do[chk["mixed",5,build[m1,m2,{7,8},60],1],
  {m1,{-1,-2,1,2,-3}},{m2,{3,-4,5,-6}}];
Do[chk["mixed6",6,build[m1,m2,{6,7,8},60],1],{m1,{-1,2,-3}},{m2,{4,-5}}];

Print["== E) g != 1 =="];
mkChk["g2_n5",5,{1,3,5},2];mkChk["g_73_n5",5,{2,3,5},7/3];
mkChk["g2_n6",6,{1,3,5,7},2];mkChk["g5_n7",7,{1,2,3,5,7},5];
chk["g3build",5,build[-1,4,{6,7},60],3];

Print["RESULT: PASS=",np," FAIL=",nf," skipped(out-of-regime/pole)=",nsk," maxRelErr=",N[mx,4]];
