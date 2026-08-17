Get["codex_work/bg_core.wl"];

cases = {
  {4, {2, 3}},
  {4, {2, -3}},
  {4, {-2, 3}},
  {4, {-2, -3}},
  {5, {2, 5/2, 3}},
  {5, {2, -5/2, 3}},
  {5, {-2, 5/2, 3}},
  {6, {3/2, 2, 5/2, 3}},
  {6, {1, -2, 3, 4}}
};

Do[
  free = c[[2]];
  {ws, amp} = TwoMinusAmplitude[free];
  Print["n=", c[[1]], " free=", free];
  Print["ws=", ws];
  Print["ks=", Join[{-1, -1}, Table[1, c[[1]] - 2]]*ws^2];
  Print["amp=", Simplify[amp], " N=", N[amp, 20]];
  Print[""];
  ,
  {c, cases}]
