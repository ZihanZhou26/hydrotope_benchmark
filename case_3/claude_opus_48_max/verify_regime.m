<< bg_core.m
$MaxExtraPrecision=400;
twoMinusSigma[n_]:=Join[{-1,-1},Table[1,n-2]];
formula[n_,ws_,g_]:=I*2^(n-1)*g^(3-n)*(ws[[1]]*ws[[2]])*Min[ws[[1]]^2,ws[[2]]^2]^(n-3);
bg[ws_,sig_,g_]:=Block[{a},a=Quiet@Check[BGAmplitude[sig*ws^2/g,ws,g],$Failed];
  If[a===Indeterminate||a===ComplexInfinity,$Failed,a]];
inReg[ws_]:=Min[ws[[1]]^2,ws[[2]]^2]<=Min[ws[[3;;]]^2];
(* build on-shell two-minus pt: minus {m1,m2}, fixed plus legs fp (len n-4), solve 2 plus *)
build[m1_,m2_,fp_,prec_]:=Block[{P,Q,Pp,Qp,d,x,y},
  P=-(m1+m2);Q=m1^2+m2^2;Pp=P-Total[fp];Qp=Q-Total[fp^2];d=2 Qp-Pp^2;
  If[d<0,Return[$Failed]];x=(Pp+Sqrt[d])/2;y=(Pp-Sqrt[d])/2;
  N[Join[{m1,m2},fp,{x,y}],prec]];
np=0;nf=0;ntest=0;mx=0;nsmaller=0;
chk[n_,m1_,m2_,fp_]:=Block[{ws,sig=twoMinusSigma[n],a,f,rel},
  ws=build[m1,m2,fp,50]; If[ws===$Failed,Return[]];
  If[!inReg[ws],Return[]];
  a=bg[ws,sig,1]; If[a===$Failed,Return[]];
  f=formula[n,ws,1]; rel=If[a==0,Abs[f-a],N[Abs[(a-f)/a],12]];
  ntest++; If[m1^2<m2^2, nsmaller++];   (* count cases where minus leg 1 is the smaller *)
  If[rel<10^-12, np++; mx=Max[mx,rel],
    nf++; If[nf<=12,Print["FAIL n=",n," m=",{m1,m2}," fp=",fp," ws=",N[ws,6]," rel=",N[rel,4]]]];
  ];
(* n=5: fp length 1.  Scan minus legs (both signs/magnitudes) & one plus leg *)
Do[chk[5,m1,m2,{p}],
  {m1,{1/10,1/2,1,2,-1,-2,-1/2,5,-7}},{m2,{2,3,5,-3,-6,8,1/3}},{p,{1,2,3,-2,-4,6,-1}}];
(* n=6: fp length 2 *)
Do[chk[6,m1,m2,{p,q}],
  {m1,{1/4,1,-1,3,-5}},{m2,{2,4,-3,7}},{p,{1,2,-2,5}},{q,{3,-4,6}}];
(* n=7: fp length 3 *)
Do[chk[7,m1,m2,{p,q,r}],
  {m1,{1/2,2,-3}},{m2,{3,5,-6}},{p,{1,-2}},{q,{4,-3}},{r,{6,-5,2}}];
Print["IN-REGIME domain scan: tested=",ntest," (",nsmaller," with |w1|<|w2|, i.e. min-branch on leg1)"];
Print["  PASS=",np," FAIL=",nf," maxRelErr=",N[mx,4]];
