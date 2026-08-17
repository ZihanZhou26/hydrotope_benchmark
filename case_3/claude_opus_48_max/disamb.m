<< bg_core.m
g=1;
amp[ws_,sig_]:=Block[{ks=sig*ws^2/g,a},a=Quiet@Check[BGAmplitude[ks,ws,g],$Failed];
  If[a===Indeterminate||a===ComplexInfinity,$Failed,a]];
test[ws_]:=Block[{sig={-1,-1,1,1,1},a,c},a=amp[ws,sig];c=If[a===$Failed,$Failed,a/I];
  Print["w=",ws,"  c=A/I=",c,
    "   sumw=",Total[ws]," sumSw2=",Total[sig*ws^2]]];
(* both minus legs negative: w1=-1/2,w2=-6, plus 3,5,-3/2 *)
test[{-1/2,-6,3,5,-3/2}];
(* swap them *)
test[{-6,-1/2,3,5,-3/2}];
(* minus legs: one pos one neg, but NEGATIVE one is smaller magnitude:
   w1=-1, w2=4 ? need on-shell. construct: minus {-1,4} sum=3 -> plus sum=-3; 
   minus sumsq=1+16=17 -> plus sumsq=17. plus: a+b+c=-3, a^2+b^2+c^2=17.
   pick a=-5: b+c=2,b^2+c^2=-8 no. a=2:b+c=-5,b^2+c^2=13,bc=6,roots x^2+5x+6=(x+2)(x+3)->-2,-3.
   plus={2,-2,-3} sum=-3 sumsq=4+4+9=17 ok *)
test[{-1,4,2,-2,-3}];
test[{4,-1,2,-2,-3}];
(* both minus positive: w1=1,w2=2 sum=3 plus sum=-3; minus sumsq=5 plus sumsq=5.
   plus a+b+c=-3, sumsq=5: a=-1:b+c=-2,b^2+c^2=4,bc=0 ->0 deg. 
   a=1:b+c=-4,b^2+c^2=4 -> bc=6 complex. a=-2:b+c=-1,b^2+c^2=1,bc=0 deg.
   hard; use a=0? deg. skip; try minus {1,3}: sum4 plus sum -4 sumsq 10 plus sumsq10.
   a=-1:b+c=-3,b^2+c^2=9,bc=0 deg. a=-3:b+c=-1,sq=1,bc=0 deg. a=1:b+c=-5,sq=9 ->bc=8 complex.
   try minus {2,3} sum5 plus -5 sumsq13. a=-1:b+c=-4 sq12 bc2 roots x^2+4x+2 irr.
   use irrational numeric *)
