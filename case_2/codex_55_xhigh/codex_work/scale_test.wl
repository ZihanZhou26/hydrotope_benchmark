Get["codex_work/bg_core.wl"];
base = {2, 5/2, 3};
Do[
  {ws, amp} = TwoMinusAmplitude[lam base];
  Print["lam=", lam, " ws=", ws, " amp=", Simplify[amp], " ratio=", Simplify[amp/(-2304 I)]],
  {lam, {1, 2, 3, 1/2}}]
