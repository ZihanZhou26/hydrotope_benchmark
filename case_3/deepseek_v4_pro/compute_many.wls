(* Fast numeric BG for two-minus sector *)
SetDirectory[NotebookDirectory[]];
Get["BGlib.m"];
gVal = 1;

twoMinusSigma[n_] := Join[{-1, -1}, Table[1, n - 2]];

(* Compute A_n for given numeric frequencies and return ws, A *)
computeNumeric[n_, fw_] := Module[{sigmas, ks, ws, amp},
  sigmas = twoMinusSigma[n];
  fwRat = Map[# &, fw];  (* keep as numbers *)
  {ks, ws} = MakeKinematics[n, fwRat, sigmas, gVal];
  If[ks === $Failed, Return[$Failed]];
  amp = BGAmplitude[ks, ws, gVal];
  N[{ws, amp}]
];

(* Tabulate data for n=5 and n=6 *)
Print["=== n=5 ==="];
For[i = 1, i <= 20, i++,
  fw = Table[RandomInteger[{1, 10}], {3}];
  If[fw[[1]] == fw[[3]], Continue[]]; (* avoid degenerate *)
  {ws, amp} = computeNumeric[5, fw];
  Print["fw=", fw, " ws=", ws, " A=", amp];
];

Print["=== n=6 ==="];
For[i = 1, i <= 10, i++,
  fw = Table[RandomInteger[{1, 10}], {4}];
  {ws, amp} = computeNumeric[6, fw];
  Print["fw=", fw, " ws=", ws, " A=", amp];
];
