Get["bg_defs.m"];
(* n=5 kinematics: ks={-81/4,-4,25/4,9,9} *)
ks = {-81/4, -4, 25/4, 9, 9};
ws = {-9/2, 2, 5/2, 3, -3};
Print["EKernel3 ", EKernel[3, {ks[[1]], ks[[2]], ks[[3]]}]];
Print["EKernel {k1,k2,k3,k4} ", EKernel[4, ks[[1;;4]]]];
Print["EKernel {k1,k2,k3,k4,k5} ", EKernel[5, ks]];
Print["FKernel3 ", FKernel[3, {ks[[1]], ks[[2]], ks[[3]]}]];
Print["FKernel4 ", FKernel[4, ks[[1;;4]]]];
Print["FKernel5 ", FKernel[5, ks]];
Print["Vertex3 ", Vertex[3, ks[[1;;3]], ws[[1;;3]]]];
Print["Vertex4 ", Vertex[4, ks[[1;;4]], ws[[1;;4]]]];
(* a BG current: subset {2,3} (1-based) -> indices for momenta *)
$kList = ks; $wList = ws; $gVal = 1;
DownValues[BGCurrent] = Select[DownValues[BGCurrent], !FreeQ[#, Pattern | Blank] &];
Print["Current{2,3} ", BGCurrent[{2, 3}]];
Print["Current{2,3,4} ", BGCurrent[{2, 3, 4}]];
Print["Current{3,4,5} ", BGCurrent[{3, 4, 5}]];
