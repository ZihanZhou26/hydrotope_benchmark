<< bg_core.m
Unprotect[mag]; ClearAll[mag];
scan[refpt_,label_] := Block[{ref,sig,fw,ks,ws,amp,cc,MM,ka,ord,sm},
  ref=Thread[{x1,x2,x3}->refpt]; mag[z_]:=z*Sign[z/.ref];
  sig={-1,-1,1,1,1}; fw={x1,x2,x3};
  {ks,ws}=MakeKinematics[5,fw,sig,1];
  amp=BGAmplitude[ks,ws,1]; cc=Together[Simplify[amp/I]];
  MM=Simplify[cc/(16 ws[[1]] ws[[2]])];
  ka=N[ws^2/.ref]; ord=Ordering[ka]; Clear[mag];
  Print["=== ",label," ref=",refpt];
  Print["   ws=",Simplify[ws/.ref]];
  Print["   |k|=",N[ka,4]," ord(asc)=",ord];
  Print["   M=",Factor[MM]];
  ];
(* failing chamber: minus legs {-4 (a), derived ~5}, plus -3, ~4.87 *)
scan[{-4,-3,49/10},"failA (m~{-4,5})"];
scan[{-4,-3,5},"failA variant"];
scan[{3,2,-4},"m={3,-4}? a=3,b=2,c=-4"];
scan[{5,-3,-4},"a=5,b=-3,c=-4"];
scan[{-7,2,-6},"a=-7"];
