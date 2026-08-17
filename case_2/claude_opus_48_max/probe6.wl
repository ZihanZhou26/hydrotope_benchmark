Get["/home/zihanz/waterhedron_benchmark_blind/case_2/claude_opus_48_max/lib.wl"];

(* 1-parameter family: w3=4, w4=9 fixed, w2=t symbolic; assume small t>0 *)
$Assumptions = 0 < t < 3/2;
Module[{ks, ws, amp},
  {ks, ws} = MakeKinematics[5, {t, 4, 9}, sig[5], gVal];
  ws = Simplify[ws]; ks = Simplify[ks];
  Print["ws(t) = ", ws];
  Print["ks(t) = ", ks];
  amp = BGAmplitude[ks, ws, gVal];
  amp = Simplify[amp/(-I), 0 < t < 3/2];
  Print["A5(t)/(-I) = ", amp];
  Print["  Together: ", Together[amp]];
  Print["  numerator: ", Numerator[Together[amp]]];
  Print["  denominator: ", Denominator[Together[amp]]];
];
