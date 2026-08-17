<< bg_core.m
(* Closed-form: legs 1,2 are the minus legs (sigma=-1). *)
formula[n_, ws_, g_] := I*2^(n-1)*g^(3-n)*(ws[[1]]*ws[[2]])*Min[ws[[1]]^2, ws[[2]]^2]^(n-3);
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];

bg[ws_, sig_, g_] := Block[{ks=sig*ws^2/g, a},
  a=Quiet@Check[BGAmplitude[ks,ws,g],$Failed];
  If[a===Indeterminate||a===ComplexInfinity,$Failed,a]];

npass=0; nfail=0;
check[label_, n_, ws_, g_] := Block[{sig=twoMinusSigma[n], a, f, rel},
  a = bg[ws, sig, g];
  f = formula[n, ws, g];
  If[a===$Failed, Print["  [SKIP pole] ",label]; Return[]];
  If[a-f===0,
    npass++,
    nfail++;
    rel = N[Abs[(a-f)/a], 5];
    Print["  [FAIL] ",label," n=",n," ws=",ws," BG=",a," formula=",f," rel=",rel]];
  ];

Print["=== Group A: FRESH generic points (not in fit set) ==="];
checkMK[n_, fw_, g_] := Block[{sig=twoMinusSigma[n], ks, ws},
  {ks,ws}=MakeKinematics[n,fw,sig,g];
  check["MK n="<>ToString[n]<>" fw="<>ToString[fw]<>" g="<>ToString[g], n, ws, g]];
Do[checkMK[5, fw, 1], {fw, {{3,7,13},{2,9,17},{4,11,15},{5,8,19},{1,12,13},{6,10,21}}}];
Do[checkMK[6, fw, 1], {fw, {{3,7,11,17},{2,5,13,19},{4,9,10,15},{1,8,12,20}}}];
Do[checkMK[7, fw, 1], {fw, {{3,5,11,13,17},{2,7,9,15,19},{1,4,10,14,20}}}];

Print["=== Group B: EXTREME regimes (one freq huge / tiny) ==="];
Do[checkMK[5, fw, 1], {fw, {{1000,2,3},{1,2,1000},{1/1000,2,3},{2,3,1/1000},{10^6,1,2}}}];
Do[checkMK[6, fw, 1], {fw, {{1000,2,3,5},{1,2,3,1000},{1/500,3,5,7}}}];
Do[checkMK[7, fw, 1], {fw, {{1,2,3,5,2000},{2000,2,3,5,7}}}];

Print["=== Group C: w2 large so MIN picks the OTHER minus leg ==="];
Do[checkMK[5, fw, 1], {fw, {{40,2,3},{50,1,2},{100,3,5}}}];
Do[checkMK[6, fw, 1], {fw, {{40,2,3,5},{80,1,2,3}}}];

Print["=== Group D: g != 1 ==="];
Do[checkMK[5, {3,7,13}, g], {g, {2, 7/3, 1/2, 5}}];
Do[checkMK[6, {3,7,11,17}, g], {g, {2, 7/3}}];
Do[checkMK[7, {3,5,11,13,17}, g], {g, {2, 5}}];

Print["=== Group E: directly-built configs (varied signs, walls) ==="];
(* both minus negative *)
check["both-minus-neg", 5, {-1/2,-6,3,5,-3/2}, 1];
(* smaller minus is negative *)
check["small-minus-neg", 5, {-1,4,2,-2,-3}, 1];
(* wall: |w1|=|w2| opposite signs: w1=-3,w2=3 => min picks 9. need on-shell:
   minus {-3,3} sum0 -> plus sum 0; minus sumsq 18 -> plus sumsq 18.
   plus a+b+c=0, a^2+b^2+c^2=18: a=3,b=-3,c=0 deg; a=1,b=-4,c=3? sum0 sq=1+16+9=26 no.
   a=4,b=-1,c=-3 sum0 sq16+1+9=26. a=3,b=1,c=-4 sq 26. Need 18: a=1,b=1,c=-2 sq6. 
   a=2,b=2,c=-4 sq24. a=3,b=-1,c=-2 sq14. a=1,b=-4,... 
   a=3,b=0,.. deg. try minus{-3,3}, plus {sqrt..}: use numeric below *)
(* wall equal same sign: w1=w2=-2 -> on-shell? minus{-2,-2} sum-4 plus sum4 sumsq8 plus sumsq8.
   plus a+b+c=4,sq=8: a=2,b=2,c=0 deg. a=0 deg. a=2,b=1,c=1 sq6. a=2,b=3,c=-1 sq14. 
   a=8/3.. use numeric *)
Print["=== done counting ==="];
Print["PASS=",npass,"  FAIL=",nfail];
