(* ================================================================ *
 *  Definitive verification of the two-minus closed form.          *
 *  Imports ONLY ../OnShellBG.m (demo tests stripped).             *
 * ================================================================ *)
Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];

(* ---- The closed form (canonical physical channel) ----
   Positive free frequencies -> MakeKinematics gives
   omega1<0, omega_n<0, and omega2..omega_{n-1} > 0.
   p = omega2 (the sigma=- leg with positive frequency),
   q = omega1 (the other sigma=- leg),
   R = positive sigma=+ legs = {3,...,n-1}, |R| = n-3 = m.
   [x]_+ = Max(x,0). *)
pp[x_] := Max[x, 0];
TP[m_, t_, a_List] := Sum[(-1)^Length[S] pp[t - Total[S]]^m, {S, Subsets[a]}];

FormulaAmp[ws_List, g_] := Module[{n = Length[ws], m, R},
  m = n - 3;
  R = Range[3, n - 1];                       (* the n-3 positive plus legs *)
  I*2^(n - 1)*ws[[1]]*ws[[2]]*TP[m, ws[[2]]^2, ws[[R]]^2]/g^(n - 3)
];

TwoMinusKin[n_, freeW_, g_] := MakeKinematics[n, freeW, Join[{-1, -1}, Table[1, n - 2]], g];

(* n=4: the bare BG hits a removable internal pole (0/0). Evaluate the
   on-shell amplitude as the regular limit of an energy-conserving
   one-parameter deformation that keeps the two-minus sector. *)
BGval[4, freeW_, g_] := Module[{w2 = freeW[[1]], w3 = freeW[[2]], eps, ws, ks, amp},
  ws = {-w3 - eps, w2, w3, -w2 + eps};       (* energy-conserving for all eps *)
  ks = {-1, -1, 1, 1}*ws^2/g;                (* momentum cons holds at eps=0 *)
  amp = Quiet[BGAmplitude[ks, ws, g]];
  Limit[amp, eps -> 0]
];
BGval[n_, freeW_, g_] := Module[{ks, ws}, {ks, ws} = TwoMinusKin[n, freeW, g]; BGAmplitude[ks, ws, g]];

relErr[a_, b_] := Module[{na = N[a, 40], nb = N[b, 40]},
  N[Abs[na - nb]/Max[1, Abs[na], Abs[nb]], 20]];

(* Kinematic points: generic, plus non-generic magnitude regimes
   (one freq much larger / much smaller), and a couple of g != 1. *)
cases = {
  {4, {2, 3}, 1}, {4, {3, 2}, 1}, {4, {1/100, 7}, 1}, {4, {9, 1/10}, 1}, {4, {5, 1/2}, 2}, {4, {2, 3}, 3/2},
  {5, {2, 5/2, 3}, 1}, {5, {1, 3, 7}, 1}, {5, {1/100, 3, 7}, 1}, {5, {50, 1, 2}, 1}, {5, {3, 50, 4}, 1}, {5, {2, 5/2, 3}, 2},
  {6, {3/2, 2, 5/2, 3}, 1}, {6, {1, 3, 5, 7}, 1}, {6, {1/100, 3, 5, 7}, 1}, {6, {40, 1, 2, 3}, 1}, {6, {2, 80, 3, 4}, 1}, {6, {1, 2, 3, 4}, 2},
  {7, {3/2, 2, 5/2, 3, 7/2}, 1}, {7, {1/100, 2, 3, 4, 5}, 1}, {7, {30, 1, 2, 3, 4}, 1}, {7, {2, 3, 4, 60, 5}, 1},
  {8, {1, 2, 3, 4, 5, 6}, 1}, {8, {1/100, 2, 3, 4, 5, 6}, 1}
};

Print["================================================================"];
Print[" Two-minus closed form:  A_n = i 2^(n-1) w1 w2 TP_{n-3}(w2^2;{wj^2}) / g^(n-3)"];
Print[" TP_m(t;{a}) = Sum_{S subset R} (-1)^|S| Max(t - Sum_{j in S} a_j, 0)^m,  R={3..n-1}"];
Print["================================================================"];
Print[StringPadRight["n",3], StringPadRight["g",6], StringPadRight["freeW",26], StringPadRight["BG (exact)",24], StringPadRight["formula",24], "relErr"];
maxErr = 0;
Do[
  n = c[[1]]; fw = c[[2]]; g = c[[3]];
  {ks, ws} = TwoMinusKin[n, fw, g];
  bg = BGval[n, fw, g];
  fm = FormulaAmp[ws, g];
  er = relErr[bg, fm];
  maxErr = Max[maxErr, er];
  Print[StringPadRight[ToString[n],3], StringPadRight[ToString[g],6],
        StringPadRight[ToString[InputForm[fw]],26],
        StringPadRight[ToString[InputForm[bg]],24],
        StringPadRight[ToString[InputForm[fm]],24],
        ScientificForm[er,3]];
  , {c, cases}];
Print["----------------------------------------------------------------"];
Print["MAX relative error over all ", Length[cases], " points = ", ScientificForm[maxErr,3]];
Print["PASS (<=1e-10): ", maxErr <= 10^-10];
