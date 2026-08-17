Get["fu_defs.m"];
sig={-1,-1,1,1,1};
(* RIGOROUS check: minus legs fixed at (-9/2, 2); vary plus-leg config keeping e1=5/2,e2=-9.
   If A = 16 w1 w2^5 (minus legs only) it must be CONSTANT = -2304 for all such configs. *)
m1=-9/2;m2=2;e1=-(m1+m2);e2=m1 m2;
agent=16*m1*m2^5;
Print["agent prediction (constant) = ",agent];
Do[
 roots=z/.NSolve[z^3-e1 z^2+e2 z-e3==0,z,60];
 If[Max[Abs[Im[roots]]]<10^-25,
  plus=Re[roots];ws=Join[{m1,m2},plus];ks=sig*ws^2;
  amp=Quiet[Check[Re[BGAmplitude[N[ks,60],N[ws,60],1]/I],$Failed]];
  If[NumericQ[amp],Print["e3=",e3," plus=",NumberForm[plus,6]," BG A/I=",NumberForm[amp,10]," agent=",agent]];
 ];
,{e3,{-15,-16,-17,-19,-21}}];
