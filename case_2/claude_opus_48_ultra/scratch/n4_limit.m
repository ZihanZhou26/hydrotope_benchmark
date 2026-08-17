Get["BGcore.m"];
gVal = 1;
(* n=4 two-minus manifold: w = (-w3, w2, w3, -w2). Sits on a propagator pole.
   Compute A_4 as a limit approaching from off-resonant (energy-conserved, on-shell) points. *)

(* approach 1: perturb leg 4 and leg 1 by eps *)
A4limit[s_, t_, dir_] := Module[{w2, w3, w4, w1, ws, ks, amp},
  (* dir = {d1,d2,d3,d4} perturbation directions in eps, keeping sum w =0 *)
  w2 = t + dir[[2]]*eps; w3 = s + dir[[3]]*eps; w4 = -t + dir[[4]]*eps;
  w1 = -(w2 + w3 + w4);
  ws = {w1, w2, w3, w4};
  ks = {-1, -1, 1, 1}*ws^2;
  amp = BGAmplitude[ks, ws, gVal];
  Limit[amp, eps -> 0]];

Do[Module[{s = pt[[1]], t = pt[[2]], a, b, c, predR, predP},
  Print["s=", s, " t=", t, " (mu1=min(s^2,t^2)=", Min[s^2, t^2], ")"];
  a = A4limit[s, t, {0, 0, 0, 1}];     (* perturb leg4 *)
  b = A4limit[s, t, {0, 1, 0, 0}];     (* perturb leg2 *)
  c = A4limit[s, t, {0, 1, -1, 1}];    (* generic dir *)
  Print["   limit dir1 = ", a, " = ", N[a]];
  Print["   limit dir2 = ", b, " = ", N[b]];
  Print["   limit dir3 = ", c, " = ", N[c]];
  (* formula prediction: P4 = -16 w1 w2 mu1, mu1 = smaller magnitude. w1=-s,w2=t *)
  predR = Min[s^2, t^2];
  predP = -16*(-s)*(t)*predR;
  Print["   formula pred A4 = -i*P4 = ", -I*predP, " = ", N[-I*predP]];
 ], {pt, {{2, 3}, {3, 2}, {1, 5}, {5, 2}}}];
