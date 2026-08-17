Get["BGcore.m"];
gVal = 1;
amp = Get["amp5_symbolic.m"];
sigmas = {-1,-1,1,1,1};
{ksym, wsym} = MakeKinematics[5, {a,b,c}, sigmas, gVal];
w1f = wsym[[1]]; w5f = wsym[[5]];

resolveAt[refpt_] := Module[{r},
  r = amp /. Abs[x_] :> Sign[N[x /. refpt, 50]]*x;
  r = Together[r];
  r = r/(-I);
  r];

(* representative free points for the 5 chambers found *)
reps = {
  {a->32/7, b->29/4, c->38/7},
  {a->21,   b->9,    c->7/6},
  {a->8/5,  b->18/7, c->3/4},
  {a->29/5, b->2,    c->16},
  {a->7/2,  b->8/3,  c->10/3}
};
Do[
  Module[{p, pf, allw, mags, num, den},
   p = resolveAt[reps[[i]]];
   pf = Factor[p];
   num = Factor[Numerator[Together[p]]];
   den = Factor[Denominator[Together[p]]];
   allw = N[{w1f, a, b, c, w5f} /. reps[[i]]];
   mags = allw^2;
   Print["==== chamber ", i, " ===="];
   Print["  free a,b,c = ", {a,b,c}/.reps[[i]]];
   Print["  all w  = ", allw];
   Print["  w^2    = ", mags];
   Print["  ascending w^2 leg order: ", Ordering[mags]];
   Print["  P5 (factored) = ", pf];
   Print["  numerator = ", num];
   Print["  denominator = ", den];
   Print[];
  ],
  {i, Length[reps]}];
