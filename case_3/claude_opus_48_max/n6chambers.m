<< bg_core.m
Unprotect[mag]; ClearAll[mag];
scan[refpt_] := Block[{ref,sig,fw,ks,ws,amp,cc,MM,ka,ord},
  ref=Thread[{x1,x2,x3,x4}->refpt]; mag[z_]:=z*Sign[z/.ref];
  sig={-1,-1,1,1,1,1}; fw={x1,x2,x3,x4};
  {ks,ws}=MakeKinematics[6,fw,sig,1];
  amp=BGAmplitude[ks,ws,1]; cc=Together[Simplify[amp/I]];
  MM=Simplify[cc/(2^5 ws[[1]] ws[[2]])];   (* c = 2^(n-1)(w1 w2) M, n=6 *)
  ka=N[ws^2/.ref]; ord=Ordering[ka]; Clear[mag];
  Print["ref=",refpt," ord(asc legs)=",ord];
  Print["   |k|=",N[ka,4]];
  Print["   M=",Factor[MM]];
  ];
scan[{2,3,5,7}];      (* w2 small: expect |k2|^3 *)
scan[{40,2,3,5}];     (* w2 large *)
scan[{40,3,5,7}];     (* w2 large, diff plus *)
scan[{-6,3,5,7}];     (* w2 large neg *)
scan[{5,3,5,7}];      (* intermediate *)
