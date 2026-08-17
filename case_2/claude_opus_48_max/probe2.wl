Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/bg_defs.wl"];
gVal = 1;
sig[n_] := Join[{-1, -1}, Table[1, {n - 2}]];

(* Flexible solver: free = all legs except {a,b}; solve for leg a (sigma=-1)
   and leg b (sigma=+1).  vals is an Association idx->value for free legs. *)
MakeKinAB[n_, a_, b_, vals_] := Module[
  {s = sig[n], others, A, B, wa, wb, w, k},
  others = Complement[Range[n], {a, b}];
  A = Total[vals /@ others];                 (* sum of free omegas *)
  B = -Total[(s[[#]]*vals[#]^2) & /@ others]; (* = sigma_a wa^2 + sigma_b wb^2 *)
  (* sigma_a=-1, sigma_b=+1:  wa+wb=-A,  -wa^2+wb^2=B  =>  wb-wa=-B/A *)
  wb = -(A + B/A)/2;
  wa = -(A - B/A)/2;
  w = Table[Which[i == a, wa, i == b, wb, True, vals[i]], {i, n}];
  k = s*w^2/gVal;
  {k, w}];

Print["=== Check MakeKinematics forces w4=-w2 at n=4 (symbolic) ==="];
Module[{w2, w3, ks, ws},
  {ks, ws} = MakeKinematics[4, {w2, w3}, sig[4], gVal];
  Print["  MakeKinematics n=4 allW = ", Simplify[ws]];
];

Print["\n=== n=4 generic points: solve legs (1,3), free (w2,w4) ==="];
Do[Module[{vals, ks, ws, amp, k24},
   vals = <|2 -> w2v, 4 -> w4v|>;
   {ks, ws} = MakeKinAB[4, 1, 3, vals];
   k24 = ks[[2]] + ks[[4]];
   amp = BGAmplitude[ks, ws, gVal];
   Print["  (w2,w4)=", {w2v, w4v}, "  allW=", ws, "  k24=", k24, "  A4=", amp];
   ],
  {w2v, {1, 2, 3/2}}, {w4v, {3, 5/2, 7/3}}];
