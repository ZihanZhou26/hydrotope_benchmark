Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

qS[ws_, S_] := Total[ws[[#]]^2 & /@ S];
Aconj[ws_, active_] := Module[{n = Length[ws], plus, x, terms},
  plus = Range[3, n]; x = ws[[active]]^2; terms = 0;
  Do[If[x > qS[ws, S],
     terms += (-1)^(Length[S] + 1) (x - qS[ws, S])^(n - 3)],
   {S, Subsets[plus]}];
  2^(n - 1) ws[[1]] ws[[2]] terms];

(* n=4 on-shell point is forced to w=(-b,a,b,-a) [degenerate, k_{2,4}=0].
   Approach it with momentum slightly broken: w4 = -a + d, w1=-(a+b+w4).
   Compute off-shell BG (finite for d!=0), extrapolate d->0. *)
ampOff[ws_] := Module[{a}, a = BGAmplitude[kvec[ws], ws, gVal];
  If[NumericQ[a], a/(-I), Indeterminate]];

Print["n=4: BG limit vs formula  (formula = -8 w1 w2^3 on shell)"];
Do[Module[{a, b, vals, lim, ws0, formVal},
   {a, b} = ab;
   ws0 = {-b, a, b, -a};              (* exact on-shell degenerate point *)
   formVal = Aconj[ws0, If[ws0[[1]]^2 <= ws0[[2]]^2, 1, 2]];
   (* sequence of d -> 0 *)
   vals = Table[Module[{d = 1/10^k, w4, w1, ws},
       w4 = -a + d; w1 = -(a + b + w4); ws = {w1, a, b, w4};
       {d, ampOff[ws]}], {k, 2, 6}];
   Print["(a,b)=", {a, b}, "  w_onshell=", ws0];
   Print["   formula = ", formVal, " = ", N[formVal]];
   Print["   BG(d) as d->0:"];
   Do[Print["      d=", v[[1]], "  A=", N[v[[2]], 16]], {v, vals}];
   ],
  {ab, {{1, 3}, {2, 5}, {3, 7}}}];
