Get["BGcore.m"];
gVal = 1;
amp = Get["amp5_symbolic.m"];
Print["loaded amp, LeafCount=", LeafCount[amp]];

(* a=w2,b=w3,c=w4 free.  Resolve Abs at a numeric reference point. *)
resolveAt[refpt_] := Module[{r},
  r = amp /. Abs[x_] :> Sign[N[x /. refpt, 30]]*x;
  r = Together[r];
  r = Simplify[r];
  r];

(* polynomial in a,b,c?  *)
testpts = {
  {a -> 1, b -> 2, c -> 3},
  {a -> 1, b -> 3, c -> 2},
  {a -> 2, b -> 1, c -> 3},
  {a -> 3, b -> 1, c -> 2},
  {a -> 2, b -> 3, c -> 1},
  {a -> 3, b -> 2, c -> 1},
  {a -> 10, b -> 1, c -> 1},
  {a -> 1, b -> 10, c -> 1},
  {a -> 5, b -> 4, c -> 2},
  {a -> 1, b -> 1, c -> 10}
};
Do[
  Block[{p, isPoly},
   p = resolveAt[pt];
   isPoly = PolynomialQ[Numerator[Together[p]], {a, b, c}] && (Denominator[Together[p]] === 1 || PolynomialQ[Denominator[Together[p]],{a,b,c}]);
   Print["pt=", pt, "  isPoly(den=1)?=", (Denominator[Together[p]] === 1)];
   Print["   P/(-I) = ", Expand[p/(-I)]];
   Print["   ---"];
  ],
  {pt, testpts}
];
