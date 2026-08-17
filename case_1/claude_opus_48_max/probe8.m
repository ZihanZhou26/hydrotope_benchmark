Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];
twoMinusSigma[n_] := Join[{-1, -1}, Table[1, {n - 2}]];
mk[n_, fw_] := MakeKinematics[n, fw, twoMinusSigma[n], 1];

(* ===== candidate GENERAL n=5 piecewise rule =====
   A5 = 16 I * (w1 w2) * Phi,  Phi depends on the TWO smallest |w|.
   f1<=f2 smallest magnitudes; s1,s2 their sigma (-1 minus / +1 plus).
   if s1==-1            : Phi = f1^4
   elif s1==+1,s2==-1   : Phi = f1^2 (2 f2^2 - f1^2)
   else (s1==+1,s2==+1) : Phi = 2 f1^2 f2^2                               *)
ruleA5[ws_] := Module[{mags, idx, leg1, leg2, f1, f2, s1, s2, phi, prodMu},
  prodMu = ws[[1]] ws[[2]];                 (* signed product of minus legs *)
  mags = Abs[ws];
  idx = Ordering[mags];                      (* indices sorted by |w| ascending *)
  leg1 = idx[[1]]; leg2 = idx[[2]];
  f1 = mags[[leg1]]; f2 = mags[[leg2]];
  s1 = If[leg1 <= 2, -1, 1]; s2 = If[leg2 <= 2, -1, 1];
  phi = Which[
    s1 == -1, f1^4,
    s1 == 1 && s2 == -1, f1^2 (2 f2^2 - f1^2),
    True, 2 f1^2 f2^2];
  16 I prodMu phi];

(* random n=5 test points, arbitrary free-freq signs/orderings *)
SeedRandom[12345];
pts = Table[
   Table[RandomChoice[{-1, 1}] RandomInteger[{1, 12}] + RandomChoice[{0, 1/2, 1/3}],
     {3}], {40}];
pts = Select[pts, (Total[#] != 0) &];  (* avoid s1=0 *)

nFail = 0; nOk = 0;
Do[Module[{ks, ws, bg, pred},
   {ks, ws} = mk[5, fw];
   bg = BGAmplitude[ks, ws, 1];
   pred = ruleA5[ws];
   If[Simplify[bg - pred] === 0, nOk++,
     nFail++;
     If[nFail <= 10,
       Print["FAIL fw=", fw, "  ws=", N[ws, 5],
         "  BG=", N[bg], "  rule=", N[pred],
         "  sortedLegs=", Ordering[Abs[ws]]]]]],
  {fw, pts}]
Print["n=5 general rule:  OK = ", nOk, "   FAIL = ", nFail, "   (of ", Length[pts], ")"];
