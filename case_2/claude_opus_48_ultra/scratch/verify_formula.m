(* ============================================================
   VERIFY the closed-form A_n in the two-minus sector:
     A_n = I * 2^(n-1) * w1*w2 * Sum_{S subset Plus} (-1)^|S| (a - sigma_S)_+^(n-3)
   where a = min(w1^2,w2^2), Plus = {w3^2,...,wn^2}, sigma_S = sum_{i in S} wi^2.
   Compare against BGAmplitude (exact rational) for n=5,6,7 (direct) and n=4 (limit).
   ============================================================ *)
Get["BGcore.m"];
gVal = 1;
pw[x_, d_] := If[x > 0, x^d, 0];

(* the closed form *)
Aformula[ws_List] := Module[{n = Length[ws], m, a, plus, d, subs},
  n = Length[ws]; m = ws^2; a = Min[m[[1]], m[[2]]]; plus = m[[3 ;;]]; d = n - 3;
  subs = Subsets[plus];
  I*2^(n - 1)*ws[[1]]*ws[[2]]*Total[((-1)^Length[#]) pw[a - Total[#], d] & /@ subs]];

(* chamber label: which plus-subsets have sigma_S < a (sorted by size) -> signature *)
chamberId[ws_] := Module[{m = ws^2, a, plus},
  a = Min[m[[1]], m[[2]]]; plus = Sort[m[[3 ;;]]];
  Tally[Length /@ Select[Subsets[plus], Total[#] < a &]]];

relErr[exact_, approx_] := If[exact == 0, Abs[N[approx, 30]], Abs[N[(exact - approx)/exact, 30]]];

Print["================= n = 5, 6, 7 : formula vs BGAmplitude ================="];
Do[Module[{n = nn, sig, raw, results, chambers, maxRel, nzero},
   sig = Join[{-1, -1}, Table[1, n - 2]];
   SeedRandom[9000 + n];
   raw = {}; While[Length[raw] < If[n == 7, 60, 200],
     Module[{fw, ks, ws, amp},
      fw = Table[RandomChoice[{-1, -1, 1, 1, 1}] RandomInteger[{1, 30}]/RandomInteger[{1, 6}], {n - 2}];
      {ks, ws} = MakeKinematics[n, fw, sig, gVal];
      If[MemberQ[ws, 0], Continue[]];
      amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
      If[amp === $Failed || ! FreeQ[amp, Indeterminate] || ! FreeQ[amp, ComplexInfinity] || ! FreeQ[amp, DirectedInfinity], Continue[]];
      AppendTo[raw, {ws, amp}]]];
   results = Table[
      Module[{ws = e[[1]], amp = e[[2]], af, exactEq, re},
       af = Aformula[ws];
       exactEq = (Simplify[af - amp] === 0);
       re = relErr[amp, af];
       {exactEq, re, chamberId[ws]}], {e, raw}];
   chambers = DeleteDuplicates[results[[All, 3]]];
   maxRel = Max[results[[All, 2]]];
   Print["n=", n, ": ", Length[raw], " pts; all-exact-equal = ", AllTrue[results, #[[1]] &],
     "; max rel.err = ", ScientificForm[N[maxRel], 3], "; distinct chambers tested = ", Length[chambers]];
  ], {nn, {5, 6, 7}}];

Print[];
Print["================= n = 4 (limit) vs formula ================="];
(* n=4 forced: w=(-s,t,s,-t). Compute BG limit by eps-perturbation; compare to formula. *)
A4limit[s_, t_] := Module[{w2, w3, w4, w1, ws, ks, amp},
  w2 = t; w3 = s; w4 = -t + eps; w1 = -(w2 + w3 + w4); ws = {w1, w2, w3, w4};
  ks = {-1, -1, 1, 1} ws^2; amp = BGAmplitude[ks, ws, gVal]; Limit[amp, eps -> 0]];
Do[Module[{s = pt[[1]], t = pt[[2]], ws, lim, af},
   ws = {-s, t, s, -t}; lim = A4limit[s, t]; af = Aformula[ws];
   Print["  s=", s, ",t=", t, ": BG-limit = ", lim, " ; formula = ", af,
     " ; equal? ", Simplify[lim - af] === 0];
  ], {pt, {{2, 3}, {3, 2}, {1, 5}, {5, 2}, {7, 3}, {4, 9}}}];
