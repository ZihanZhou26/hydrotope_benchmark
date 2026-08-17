(* ============================================================
   Self-contained verification of the closed-form A_n
   in the two-minus sector, against the supplied Berends-Giele code.

   Run:  wolframscript -file verify.m
   ============================================================ *)

Get["BG_core.m"];     (* verbatim definitions from OnShellBG.m (lines 1-144) *)
Get["formula.m"];      (* defines Aformula[omegas]                            *)
gVal = 1;

(* combinatorial chamber: which INDEX-subsets of the sorted plus-legs have sigma_S < a
   (this is the actual polynomial-piece label, not a numeric value) *)
chamberId[ws_] := Module[{m = ws^2, a, plus, idx},
  a = Min[m[[1]], m[[2]]]; plus = Sort[m[[3 ;;]]]; idx = Range[Length[plus]];
  Sort[Select[Subsets[idx], Total[plus[[#]]] < a &]]];

Print["======================================================================"];
Print["  Closed form:  A_n = I 2^(n-1) w1 w2 Sum_{S<=Plus} (-1)^|S| (a-sigma_S)_+^(n-3)"];
Print["  a = min(w1^2,w2^2),  Plus = {w3^2..wn^2},  exact rational arithmetic."];
Print["======================================================================\n"];

(* ---- (A) the three original OnShellBG.m test points ---- *)
Print["--- (A) Original OnShellBG.m test points ---"];
Do[Module[{n = tc[[1]], fw = tc[[2]], sig, ks, ws, bg, af},
   sig = Join[{-1, -1}, Table[1, n - 2]];
   {ks, ws} = MakeKinematics[n, fw, sig, gVal];
   bg = BGAmplitude[ks, ws, gVal]; af = Aformula[ws];
   Print["  n=", n, " fw=", fw, ":  BG=", bg, "  formula=", af, "  EQUAL=", bg === af];
  ], {tc, {{5, {2, 5/2, 3}}, {6, {2, 5/2, 3, 7/2}}, {7, {2, 5/2, 3, 7/2, 4}}}}];

(* ---- (B) random multi-chamber scans, n=5,6,7 (exact equality) ---- *)
Print["\n--- (B) Random multi-chamber scans (exact equality vs BGAmplitude) ---"];
Do[Module[{n = nn, sig, npts, raw, chambers, alleq},
   sig = Join[{-1, -1}, Table[1, n - 2]];
   npts = If[n == 7, 12, 150];
   SeedRandom[314 + n]; raw = {};
   While[Length[raw] < npts,
     Module[{fw, ks, ws, bg, af},
      fw = Table[RandomChoice[{-1, -1, 1, 1, 1}] RandomInteger[{1, 30}]/RandomInteger[{1, 6}], {n - 2}];
      {ks, ws} = MakeKinematics[n, fw, sig, gVal];
      If[MemberQ[ws, 0], Continue[]];
      bg = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
      If[bg === $Failed || ! FreeQ[bg, Indeterminate] || ! FreeQ[bg, ComplexInfinity] || ! FreeQ[bg, DirectedInfinity], Continue[]];
      af = Aformula[ws];
      AppendTo[raw, {ws, bg === af, chamberId[ws]}]]];
   alleq = AllTrue[raw, #[[2]] &];
   chambers = DeleteDuplicates[raw[[All, 3]]];
   Print["  n=", n, ":  ", Length[raw], " points,  distinct polynomial chambers hit = ",
     Length[chambers], ",  ALL EXACTLY EQUAL = ", alleq,
     "  (exact rational equality => relative error = 0 < 1e-10)"];
  ], {nn, {5, 6, 7}}];

(* ---- (C) n=4 degenerate limit ---- *)
Print["\n--- (C) n=4 (on-shell forces a propagator pole; compare BG limit to formula) ---"];
A4limit[s_, t_] := Module[{ws, ks},
  ws = {-(s + eps), t, s, -t + eps};   (* off-resonant approach, eps->0 *)
  ks = {-1, -1, 1, 1} ws^2;
  Limit[BGAmplitude[ks, ws, gVal], eps -> 0]];
Do[Module[{s = pt[[1]], t = pt[[2]], lim, af},
   lim = A4limit[s, t]; af = Aformula[{-s, t, s, -t}];
   Print["  (s,t)=", {s, t}, ":  BG-limit=", lim, "  formula=", af, "  EQUAL=", lim === af];
  ], {pt, {{2, 3}, {3, 2}, {1, 5}, {5, 2}, {7, 3}}}];

(* ---- (D) n=8 spot-check (general-n structure) ---- *)
Print["\n--- (D) n=8 spot-check ---"];
Do[Module[{fw = tc, ks, ws, bg, af},
   {ks, ws} = MakeKinematics[8, fw, Join[{-1, -1}, Table[1, 6]], gVal];
   bg = BGAmplitude[ks, ws, gVal]; af = Aformula[ws];
   Print["  fw=", fw, ":  EQUAL=", bg === af, "  (A8=", bg, ")"];
  ], {tc, {{1, 2, 3, 4, 5, 6}}}];   (* n=8 BG is slow; one point suffices *)

Print["\n======================  DONE  ======================"];
