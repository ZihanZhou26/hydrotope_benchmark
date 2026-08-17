<< bg_core.m
Unprotect[mag]; ClearAll[mag];
doChamber[refpt_] := Block[{ref, sig, fw, ks, ws, amp, R},
  ref = Thread[{a,b,c} -> refpt];
  mag[x_] := x * Sign[x /. ref];
  sig = {-1,-1,1,1,1}; fw = {a,b,c};
  {ks, ws} = MakeKinematics[5, fw, sig, 1];
  amp = BGAmplitude[ks, ws, 1];
  R = Together[Simplify[amp/I]];   (* c = A/I *)
  Print["--- ref (a,b,c)=", refpt, "  (w2=a) ---"];
  Print["  ws = ", Simplify[ws]];
  Print["  c=A/I = ", R];
  Print["  Num=",Factor[Numerator[R]],"  Den=",Factor[Denominator[R]]];
  Clear[mag]; ];

doChamber[{2,3,5}];     (* w2 small positive: known 16 w1 w2^5 *)
doChamber[{40,2,3}];    (* w2 large positive: FAILED case *)
doChamber[{-6,3,5}];    (* w2 large negative: disamb passed *)
doChamber[{4,2,-2}];    (* mixed plus-leg signs *)
