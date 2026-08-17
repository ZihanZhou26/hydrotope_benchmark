<< bg_core.m
Unprotect[mag]; ClearAll[mag];
scan[refpt_] := Block[{ref,sig,fw,ks,ws,amp,cc,MM,ka,ord},
  ref=Thread[{x1,x2,x3}->refpt]; mag[z_]:=z*Sign[z/.ref];
  sig={-1,-1,1,1,1}; fw={x1,x2,x3};
  {ks,ws}=MakeKinematics[5,fw,sig,1];
  amp=BGAmplitude[ks,ws,1]; cc=Together[Simplify[amp/I]];
  MM=Simplify[cc/(16 ws[[1]] ws[[2]])];
  ka=N[ws^2/.ref]; ord=Ordering[ka]; Clear[mag];
  Print["ref=",refpt," ord=",ord," |k|=",N[ka,4]];
  Print["   M=",Factor[MM]];
  (* also express M in terms of k_i = sigma_i w_i^2 symbolic *)
  Print["   M/.(in w) simplified deg: ",Exponent[Numerator[Together[MM]],x1]];
  ];
scan[{4,3,5}];   (* intermediate: leg3(+),leg2(-) softest, M=207 *)
scan[{-2,3,5}];  (* leg5(+),leg2(-) softest, M=31/16 *)
scan[{-4,3,5}];  (* leg5(+),leg3(+) softest?, M=9/8 *)
scan[{7/2,3,5}]; (* M=279/2 *)
