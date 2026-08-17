Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

sig5 = {-1, -1, 1, 1, 1};
{ks, ws} = MakeKinematics[5, {a, b, c}, sig5, 1];
w1 = ws[[1]]; w5 = ws[[5]];
Print["w1 = ", Simplify[w1], "    w5 = ", Simplify[w5]];
rawAmp = BGAmplitude[ks, ws, 1];
resolveAbs[expr_, refpt_] := Together[expr //. Abs[x_] :> Sign[N[x /. refpt]] x];

chambers = {
  {"a smallest  (2,3,5)", {a -> 2, b -> 3, c -> 5}},
  {"a middle    (3,2,5)", {a -> 3, b -> 2, c -> 5}},
  {"a largest   (5,2,3)", {a -> 5, b -> 2, c -> 3}},
  {"b<0         (3,-2,5)", {a -> 3, b -> -2, c -> 5}},
  {"a<0         (-2,3,5)", {a -> -2, b -> 3, c -> 5}},
  {"a<0 small   (-1,3,5)", {a -> -1, b -> 3, c -> 5}}
};

Do[Module[{lbl, pt, rat, num, den},
   {lbl, pt} = ch;
   rat = resolveAbs[rawAmp, pt];
   Print["================ ", lbl, " ================"];
   Print["  Factor (in a,b,c): ", Factor[rat]];
   (* re-express via w1, w5: a=w2, and try to write using w1=ws[[1]] *)
   ],
  {ch, chambers}]

(* Also: is chamber-A result exactly 16 I w1 a^5 ? *)
Print[];
Print["check 16 I w1 a^5 - fA(chamberA) = ",
  Simplify[16 I w1 a^5 - resolveAbs[rawAmp, {a -> 2, b -> 3, c -> 5}]]];
