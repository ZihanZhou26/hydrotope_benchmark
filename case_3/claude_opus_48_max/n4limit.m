<< bg_core.m
$MaxExtraPrecision=400;
g=1; sig={-1,-1,1,1};
(* n=4 two-minus is forced onto {w1,w2}={-w3,-w4}: an internal line is exactly
   on-shell (0/0). Regularize: deform off momentum-conservation by eps, limit eps->0. *)
formula[ws_]:=I*2^3*g^(3-4)*(ws[[1]]*ws[[2]])*Min[ws[[1]]^2,ws[[2]]^2]^(4-3);
test[w3_,w4_]:=Block[{vals,fw,a,c},
  Print["plus legs w3=",w3," w4=",w4,"  -> minus legs forced {-w3,-w4}"];
  Print["  formula c = ", formula[{-w3,-w4,w3,w4}]/I, " * I"];
  Do[
   fw=N[{-w3, -w4-eps, w3+eps, w4}, 60];
   a=Quiet@Check[BGAmplitude[sig*fw^2/g, fw, g],$Failed];
   Print["   eps=",N[eps,3],"  c=A/I=",N[a/I,12]],
   {eps,{1/100,1/1000,1/10000,1/100000}}];
  Print[""]];
test[3,2];
test[5,2];
test[7,3];
