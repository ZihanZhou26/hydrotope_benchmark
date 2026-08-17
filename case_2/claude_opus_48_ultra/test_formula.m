(* ============================================================
   Exhaustive sweep: closed form vs BGAmplitude over thousands of points.
   n=5 generated fresh here; n=6 (4500 pts) and n=7 (560 pts) read from the
   parallel-generated datasets in scratch/ (stored as {ws, A/(-I)}).
   Reports # mismatches per n (target: 0).

   Run:  wolframscript -file test_formula.m
   ============================================================ *)
Get["BG_core.m"];
Get["formula.m"];
gVal = 1;

sweep[n_, raw_] := Module[{bad},
  bad = Count[raw, e_ /; (e[[2]] =!= Aformula[e[[1]]])];
  Print["  n=", n, ":  ", Length[raw], " points,  mismatches = ", bad]; bad];

(* --- n=5 fresh (signed free frequencies span many chambers) --- *)
sig5 = {-1, -1, 1, 1, 1};
SeedRandom[20240620]; raw5 = {};
While[Length[raw5] < 500,
  Module[{fw, ks, ws, amp},
   fw = Table[RandomChoice[{-1, -1, 1, 1, 1}] RandomInteger[{1, 25}]/RandomInteger[{1, 5}], {3}];
   {ks, ws} = MakeKinematics[5, fw, sig5, gVal];
   If[MemberQ[ws, 0], Continue[]];
   amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
   If[amp === $Failed || ! FreeQ[amp, Indeterminate] || ! FreeQ[amp, ComplexInfinity] || ! FreeQ[amp, DirectedInfinity], Continue[]];
   AppendTo[raw5, {ws, amp}]]];

Print["Exhaustive sweep   (BGAmplitude  ===  Aformula):"];
total = sweep[5, raw5];
If[FileNames["scratch/n6_part_*.m"] =!= {},
  Module[{raw6 = DeleteDuplicates[Join @@ (Get /@ FileNames["scratch/n6_part_*.m"])]},
   total += sweep[6, {#[[1]], -I #[[2]]} & /@ raw6]]];
If[FileNames["scratch/n7_part_*.m"] =!= {},
  Module[{raw7 = DeleteDuplicates[Join @@ (Get /@ FileNames["scratch/n7_part_*.m"])]},
   total += sweep[7, {#[[1]], -I #[[2]]} & /@ raw7]]];
Print["TOTAL MISMATCHES = ", total];
