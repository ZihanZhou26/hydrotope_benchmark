(* Verification script for the branch formula. It expects bg_defs.wls in the
   parent directory; bg_defs.wls was generated from the allowed OnShellBG.m
   definitions during the run. *)
Get["../bg_defs.wls"];
BranchFormula[ws_List] := Module[{n=Length[ws], negs={ws[[1]],ws[[2]]}, p, q},
  p=Select[negs,#>0&];
  If[Length[p]!=1,Return[$Failed]];
  p=p[[1]]; q=Times@@negs/p;
  I*2^(n-1)*q*p^(2 n-5)
];
cases={{5,{2,5/2,3}},{5,{-9/2,5/2,3}},{5,{3,4,5}},{5,{1,2,4}},
       {6,{3,4,5,6}},{6,{2,3,5,7}},{6,{-184/17,3,5,7}},
       {7,{3,4,5,6,7}},{7,{2,3,5,7,11}}};
Do[
  n=case[[1]]; fw=case[[2]];
  sig=Join[{-1,-1},Table[1,n-2]];
  {ks,ws}=MakeKinematics[n,fw,sig,1];
  amp=BGAmplitude[ks,ws,1]; form=BranchFormula[ws];
  Print["n=",n," fw=",fw," ws=",ws," BG/I=",Simplify[amp/I],
        " formula/I=",Simplify[form/I]," diff=",Simplify[(amp-form)/I]];
,{case,cases}]
