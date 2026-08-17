<< bg_core.m
$MaxExtraPrecision=300;
sig5={-1,-1,1,1,1};
bg[ws_,g_]:=Block[{ks=sig5*ws^2/g,a},a=Quiet@Check[BGAmplitude[ks,ws,g],$Failed];
  If[a===Indeterminate||a===ComplexInfinity,$Failed,a]];
(* n=5 rule *)
ruleC[ws_]:=Block[{ka,ord,s1,s2,t1,t2,k1,k2,MM},
  ka=ws^2; ord=Ordering[N[ka]]; s1=ord[[1]];s2=ord[[2]];
  t1=sig5[[s1]];t2=sig5[[s2]]; k1=ka[[s1]];k2=ka[[s2]];
  MM=Which[t1==-1, k1^2, t2==1, 2 k1 k2, True, k1(2 k2-k1)];
  2^4 * ws[[1]]*ws[[2]]*MM];   (* = c = A/I *)
(* build on-shell pt: minus {m1,m2}, fixed plus fp(len 1), solve 2 plus *)
build[m1_,m2_,fp_,prec_]:=Block[{P,Q,Pp,Qp,d,x,y},
  P=-(m1+m2);Q=m1^2+m2^2;Pp=P-Total[fp];Qp=Q-Total[fp^2];d=2Qp-Pp^2;
  If[d<0,Return[$Failed]];x=(Pp+Sqrt[d])/2;y=(Pp-Sqrt[d])/2;
  N[Join[{m1,m2,fp[[1]],x,y}],prec]];
np=0;nf=0;mx=0;
chk[m1_,m2_,fp_]:=Block[{ws,a,f,rel},ws=build[m1,m2,fp,40];
  If[ws===$Failed,Return[]];a=bg[ws,1];If[a===$Failed,Return[]];
  f=I ruleC[ws];rel=N[Abs[(a-f)/a],10];
  If[rel>10^-12,nf++;Print["FAIL m=",{m1,m2}," fp=",fp," rel=",rel," BG=",N[a,8]," rule=",N[f,8]],np++;mx=Max[mx,rel]]];
(* sweep arbitrary minus legs & plus configs *)
Do[chk[m1,m2,{p}],
  {m1,{-1/2,-1,-2,-3,-5,-7,1,2,3,5,1/3,7}},
  {m2,{2,3,5,-2,-4,6,1/2,9}},
  {p,{2,3,5,-2,-3,1,7,-6}}];
Print["arbitrary-minus sweep: PASS=",np," FAIL=",nf," maxrel=",N[mx,4]];
