Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* scan w2=t over a wide range, w3=4, w4=9 fixed.
   group by signature, reconstruct A(t) per chamber, express via omega. *)
ts = Table[k/4, {k, 1, 60}];   (* t = 0.25 .. 15 *)
rows = {};
Do[Module[{ws, A, sg},
   ws = genPt[5, {t, 4, 9}]; A = ampR[ws];
   If[A === Indeterminate, Continue[]];
   sg = chamberSig[ws];
   AppendTo[rows, <|"t" -> t, "w" -> ws, "A" -> A, "sig" -> sg|>]],
  {t, ts}];

groups = GatherBy[rows, #["sig"] &];
Print["chambers along the line: ", Length[groups]];
Do[Module[{g, trange, fit, p, vals, ip, ok, expr, w1, w2, w5},
   g = grp;
   trange = MinMax[#["t"] & /@ g];
   Print["\n=== chamber sig=", g[[1]]["sig"]];
   Print["    t in ", trange, "  (", Length[g], " pts)"];
   (* try A(t)*(13+t)^p = polynomial *)
   Do[vals = {#["t"], #["A"]*(13 + #["t"])^p} & /@ g;
      If[Length[vals] < 9, Break[]];
      ip = Expand[InterpolatingPolynomial[vals[[1 ;; 8]], t]];
      ok = Table[(ip /. t -> vals[[i, 1]]) - vals[[i, 2]], {i, 9, Length[vals]}];
      If[Max[Abs[ok]] == 0,
        Print["    A(t)*(13+t)^", p, " = ", ip, "   (deg ", Exponent[ip, t], ")"];
        Print["    => A(t) = ", Factor[ip/(13 + t)^p]];
        Break[]],
     {p, 0, 5}];
   ],
  {grp, groups}];
