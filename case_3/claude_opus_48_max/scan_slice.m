<< bg_core.m
g=1; sig={-1,-1,1,1,1};
row[a_] := Block[{ks,ws,amp,cc,MM,ka,ord},
  {ks,ws}=MakeKinematics[5,{a,3,5},sig,g];
  amp=Quiet@Check[BGAmplitude[ks,ws,g],$Failed];
  If[amp===Indeterminate||amp===ComplexInfinity,amp=$Failed];
  If[amp===$Failed, Print["a=",a," POLE"]; Return[]];
  cc=amp/I; MM=Simplify[cc/(16 ws[[1]] ws[[2]])];
  ka=ws^2; ord=Ordering[N[ka]];
  Print["a=",PaddedForm[N[a],{6,2}]," ord=",ord,
        " |k|=",N[ka,4]," | M=",MM," =",N[MM,5]];
  ];
Do[row[a], {a, {1/2,1,3/2,2,5/2,3,7/2,4,9/2,5,6,7,8,10,12,15,20}}];
Print["--- negatives ---"];
Do[row[a], {a, {-1,-2,-3,-4,-5,-7,-10,-15}}];
