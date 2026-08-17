<< bg_core.m
gVal = 1;
twoMinusSigma[n_] := Join[{-1,-1}, Table[1, n-2]];

(* safe compute: returns amp or $Failed if pole *)
compAmp[n_, freeW_] := Block[{sig, ks, ws, amp},
  sig = twoMinusSigma[n];
  {ks, ws} = MakeKinematics[n, freeW, sig, gVal];
  amp = Quiet @ Check[BGAmplitude[ks, ws, gVal], $Failed];
  If[amp === Indeterminate || amp === ComplexInfinity, amp = $Failed];
  {ws, ks, amp}];

(* ---- scaling check: scale a working n=5 point by lambda ---- *)
Print["==== SCALING CHECK (n=5) ===="];
base = {2, 3, 5};
{ws0, ks0, a0} = compAmp[5, base];
Print["base freeW=", base, " A5=", a0];
Do[
  {wsL, ksL, aL} = compAmp[5, lam*base];
  Print["  lambda=", lam, "  A5=", aL, "  ratio A5(lam)/A5 = ", If[a0=!=$Failed && a0=!=0, aL/a0, "?"]],
  {lam, {2, 3}}];
Print[""];

(* ---- g-dependence check (n=5): vary g ---- *)
Print["==== g-DEPENDENCE CHECK (n=5), freeW=", base, " ===="];
Do[Block[{sig=twoMinusSigma[5], ks, ws, amp},
   {ks, ws} = MakeKinematics[5, base, sig, gg];
   amp = Quiet@Check[BGAmplitude[ks, ws, gg], $Failed];
   Print["  g=", gg, "  A5=", amp]],
  {gg, {1, 2, 3}}];
Print[""];
