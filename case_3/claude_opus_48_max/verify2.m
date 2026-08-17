<< bg_core.m
$MaxExtraPrecision=200;
formula[n_, ws_, g_] := I*2^(n-1)*g^(3-n)*(ws[[1]]*ws[[2]])*Min[ws[[1]]^2, ws[[2]]^2]^(n-3);
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];
bg[ws_, sig_, g_] := Block[{ks=sig*ws^2/g, a}, a=Quiet@Check[BGAmplitude[ks,ws,g],$Failed];
  If[a===Indeterminate||a===ComplexInfinity,$Failed,a]];

(* Build on-shell two-minus point with chosen minus legs {m1,m2} and fixed plus legs fp (length n-4);
   solve the last two plus legs from sum & sumsq. Uses precision prec. *)
buildPoint[n_, m1_, m2_, fp_, prec_] := Block[{P,Q,Pp,Qp,disc,x,y,ws,plus},
  P = -(m1+m2); Q = m1^2+m2^2;
  Pp = P - Total[fp]; Qp = Q - Total[fp^2];
  disc = 2 Qp - Pp^2;
  If[disc < 0, Return[$Failed]];
  x = (Pp + Sqrt[disc])/2; y = (Pp - Sqrt[disc])/2;
  plus = Join[fp, {x, y}];
  ws = N[Join[{m1, m2}, plus], prec];
  ws];

prec=40;
npass=0; nfail=0; maxrel=0;
chk[label_, n_, m1_, m2_, fp_, g_] := Block[{ws, sig=twoMinusSigma[n], a, f, rel},
  ws = buildPoint[n, m1, m2, fp, prec];
  If[ws===$Failed, Print["  [skip disc<0] ",label]; Return[]];
  a = bg[ws, sig, g]; f = formula[n, ws, g];
  If[a===$Failed, Print["  [skip pole] ",label]; Return[]];
  rel = N[Abs[(a-f)/a], 10];
  If[rel > 10^-12, nfail++; Print["  [FAIL] ",label," rel=",rel," BG=",N[a,12]," F=",N[f,12]],
     npass++; maxrel=Max[maxrel, rel]];
  ];

Print["=== n=5, ARBITRARY minus legs (plus solved), g=1 ==="];
chk["m=(-13/2,2)",5,-13/2,2,{3},1];
chk["m=(2,-13/2) swap",5,2,-13/2,{3},1];
chk["wall |m1|=|m2| opp sign (-3,3)",5,-3,3,{1},1];
chk["wall equal same sign (-2,-2)",5,-2,-2,{5},1];
chk["both minus positive (2,5)",5,2,5,{-3},1];
chk["both minus negative (-2,-5)",5,-2,-5,{3},1];
chk["smaller is negative (-1,7)",5,-1,7,{2},1];
chk["extreme ratio (1/1000, 30)",5,1/1000,30,{2},1];
chk["extreme ratio (1000, 2)",5,1000,2,{3},1];
chk["irrational-ish (Sqrt2, Pi)",5,Sqrt[2],Pi,{1},1];

Print["=== n=6, arbitrary minus legs ==="];
chk["(-7,3)",6,-7,3,{2,5},1];
chk["wall (-4,4)",6,-4,4,{1,2},1];
chk["both pos (3,8)",6,3,8,{-2,-1},1];
chk["extreme (1/100,20)",6,1/100,20,{2,3},1];
chk["equal (-3,-3)",6,-3,-3,{4,5},1];

Print["=== n=7, arbitrary minus legs ==="];
chk["(-9,4)",7,-9,4,{2,3,5},1];
chk["wall (-5,5)",7,-5,5,{1,2,3},1];
chk["extreme (1/50,40)",7,1/50,40,{2,3,5},1];

Print["=== g != 1 with arbitrary minus legs ==="];
chk["n5 g=3 (-6,2)",5,-6,2,{3},3];
chk["n6 g=7/3 (-7,3)",6,-7,3,{2,5},7/3];
chk["n7 g=5 (-9,4)",7,-9,4,{2,3,5},5];

Print["PASS=",npass," FAIL=",nfail," maxRelErr=",N[maxrel,5]];
