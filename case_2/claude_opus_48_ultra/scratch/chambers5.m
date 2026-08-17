Get["BGcore.m"];
gVal = 1;
n = 5;
sigmas = {-1, -1, 1, 1, 1};

(* chamber signature: signs of all proper-subset momentum sums (up to complement) *)
subsetsList = Select[Subsets[Range[n], {1, n - 1}], MemberQ[#, 1] &]; (* contain leg1 to break complement symmetry *)
chamberSig[ks_] := Sign[Map[Total[ks[[#]]] &, subsetsList]];

(* sample rational points, exact A5, record signature *)
SeedRandom[2024];
data = {};
cnt = 0;
While[cnt < 600,
  Module[{fw, ks, ws, sig, amp},
   fw = Table[RandomInteger[{1, 40}]/RandomInteger[{1, 7}], {n - 2}];
   {ks, ws} = MakeKinematics[n, fw, sigmas, gVal];
   sig = chamberSig[ks];
   If[MemberQ[sig, 0], Continue[]]; (* on a wall, skip *)
   (* avoid propagator poles: check all proper subset sums S: wS^2 != |kS| *)
   amp = Quiet@Check[BGAmplitude[ks, ws, gVal], $Failed];
   If[amp === $Failed || !FreeQ[amp, Indeterminate] || !FreeQ[amp, ComplexInfinity] || !FreeQ[amp, DirectedInfinity], Continue[]];
   AppendTo[data, {sig, fw, ws, ks, amp/(-I)}]; (* store P5 = A/(-i) *)
   cnt++;
  ]];
Print["collected ", Length[data], " points"];

groups = GatherBy[data, First];
Print["number of distinct chamber signatures: ", Length[groups]];
Print["group sizes: ", Sort[Length /@ groups, Greater]];

(* For each group with enough points, fit homogeneous deg-6 poly in (a,b,c)=free freqs *)
mons = Module[{vs = {a, b, c}},
   Flatten[Table[a^i*b^j*c^(6 - i - j), {i, 0, 6}, {j, 0, 6 - i}]]];
Print["num monomials deg6 in 3 vars: ", Length[mons]];

fitGroup[grp_] := Module[{pts, M, rhs, sol, ok, k},
  pts = grp;
  k = Length[mons];
  If[Length[pts] < k + 5, Return[{"too few", Length[pts]}]];
  (* build matrix from first many points *)
  M = Table[mons /. {a -> pts[[r, 2, 1]], b -> pts[[r, 2, 2]], c -> pts[[r, 2, 3]]}, {r, 1, Length[pts]}];
  rhs = pts[[All, 5]];
  (* exact least-squares via solving normal eqs is messy; instead solve exactly using k points then verify rest *)
  sol = Quiet@Check[LinearSolve[M[[1 ;; k]], rhs[[1 ;; k]]], $Failed];
  If[sol === $Failed, Return[{"singular subset", Length[pts]}]];
  (* verify on all points *)
  ok = AllTrue[Range[Length[pts]], (mons . sol /. {a -> pts[[#, 2, 1]], b -> pts[[#, 2, 2]], c -> pts[[#, 2, 3]]}) == rhs[[#]] &];
  {If[ok, "EXACT", "INCONSISTENT"], Length[pts], Factor[mons . sol]}
  ];

sorted = SortBy[groups, -Length[#] &];
Do[
  Module[{grp = sorted[[gi]], res, pt0, allw, mags},
   res = fitGroup[grp];
   pt0 = grp[[1]];
   allw = grp[[1, 3]];
   mags = allw^2;
   Print["==== chamber signature group ", gi, " (", Length[grp], " pts) ===="];
   Print["  fit status: ", res[[1]]];
   If[res[[1]] == "EXACT", Print["  P5 = ", res[[3]]]];
   Print["  rep all w = ", allw];
   Print["  rep w^2   = ", mags];
   Print["  |w| order (legs by ascending w^2): ", Ordering[mags]];
  ],
  {gi, Length[sorted]}];
