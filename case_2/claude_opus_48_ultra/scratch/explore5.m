Get["BGcore.m"];
gVal = 1;
amp = Get["amp5_symbolic.m"];
Print["loaded amp, LeafCount=", LeafCount[amp]];

(* w1,w5 as functions of a,b,c *)
sigmas = {-1,-1,1,1,1};
{ksym, wsym} = MakeKinematics[5, {a,b,c}, sigmas, gVal];
w1f = wsym[[1]]; w5f = wsym[[5]];

resolveAt[refpt_] := Module[{r},
  r = amp /. Abs[x_] :> Sign[N[x /. refpt, 40]]*x;
  r = Factor[Together[r]];
  r];

(* generic reference points covering many orderings & signs, avoiding walls *)
SeedRandom[12345];
pts = {};
Do[
  Module[{a0,b0,c0,pt,ok,allw,abss},
   a0 = RandomInteger[{-9,9}]+RandomChoice[{1/7,2/7,3/7,1/3,1/5}];
   b0 = RandomInteger[{1,9}]+RandomChoice[{1/7,2/7,3/7,1/3,1/5}];
   c0 = RandomInteger[{1,9}]+RandomChoice[{1/7,2/7,3/7,1/3,1/5}];
   pt = {a->a0,b->b0,c->c0};
   AppendTo[pts, pt];
  ], {200}];

results = {};
Do[
  Module[{p, key, allw, mags},
   p = Quiet@Check[resolveAt[pt], $Failed];
   If[p === $Failed || !FreeQ[p, Indeterminate] || !FreeQ[p, ComplexInfinity], Continue[]];
   p = Expand[p/(-I)]; (* the real polynomial P5 *)
   AppendTo[results, {p, pt}];
  ], {pt, pts}];

distinct = GatherBy[results, First];
Print["Number of distinct polynomials found: ", Length[distinct]];
Do[
  Module[{poly, reps, pt0, allw, mags, sq},
   poly = distinct[[i,1,1]];
   reps = distinct[[i, All, 2]];
   pt0 = reps[[1]];
   allw = N[{w1f, a, b, c, w5f} /. pt0];
   sq = allw^2;
   Print["=== chamber ", i, " (", Length[reps], " pts) ==="];
   Print["  factored P5 = ", Factor[poly]];
   Print["  rep pt a,b,c = ", {a,b,c}/.pt0];
   Print["  all w  = ", allw];
   Print["  all w^2= ", sq];
   Print["  order of w^2 (legs 1..5) by size: ", Ordering[sq]];
  ], {i, Length[distinct]}];
