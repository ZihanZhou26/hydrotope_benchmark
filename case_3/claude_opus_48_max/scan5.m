<< bg_core.m
Unprotect[mag]; ClearAll[mag];
scan[refpt_] := Block[{ref, sig, fw, ks, ws, amp, cc, MM, ka, ord},
  ref = Thread[{x1,x2,x3} -> refpt];
  mag[z_] := z * Sign[z /. ref];
  sig = {-1,-1,1,1,1}; fw = {x1,x2,x3};
  {ks, ws} = MakeKinematics[5, fw, sig, 1];
  amp = BGAmplitude[ks, ws, 1];
  cc = Together[Simplify[amp/I]];
  MM = Simplify[cc/(2^4 * ws[[1]]*ws[[2]])];
  ka = (ws^2) /. ref;
  ord = Ordering[ka];
  Clear[mag];
  Print["ref=",refpt,"  |k|order(asc)=",ord," |k|=",N[ka,4]];
  Print["    M = ", Factor[MM]];
  ];
scan[{2,3,5}];
scan[{40,2,3}];
scan[{40,3,5}];
scan[{-6,3,5}];
scan[{4,2,-2}];
scan[{1,10,2}];
scan[{1,2,10}];
scan[{7,2,3}];
scan[{20,2,3}];
scan[{-1,4,2}];
scan[{10,1,2}];
scan[{2,3,50}];
