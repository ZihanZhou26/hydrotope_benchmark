Get["codex_work/bg_core.wl"];
Do[
  ps = Range[n];
  Print["n=", n, " E=", Simplify[EKernel[n, ps]], " F=", Simplify[FKernel[n, ps]]],
  {n, 3, 8}]

Do[
  ps = Join[{-Range[n][[1]]}, Range[2, n]];
  Print["mixed n=", n, " ps=", ps, " E=", Simplify[EKernel[n, ps]], " F=", Simplify[FKernel[n, ps]]],
  {n, 3, 7}]
