Get["BGcore.m"];
Get["test_bspline.m"];
gVal=1;
(* n=6 from saved parts *)
parts = FileNames["n6_part_*.m"];
raw6 = DeleteDuplicates[Join @@ (Get /@ parts)];
testAll[6, raw6];
(* n=7 from parts *)
parts7 = FileNames["n7_part_*.m"];
raw7 = DeleteDuplicates[Join @@ (Get /@ parts7)];
testAll[7, raw7];
(* n=5 fresh *)
sig5 = {-1,-1,1,1,1};
SeedRandom[55]; raw5={};
Do[Module[{fw,ks,ws,amp},
  fw=Table[RandomChoice[{-1,1}]RandomInteger[{1,20}]/RandomInteger[{1,4}],{3}];
  {ks,ws}=MakeKinematics[5,fw,sig5,gVal];
  If[MemberQ[ws,0],Continue[]];
  amp=Quiet@Check[BGAmplitude[ks,ws,gVal],$Failed];
  If[amp===$Failed||!FreeQ[amp,Indeterminate]||!FreeQ[amp,ComplexInfinity]||!FreeQ[amp,DirectedInfinity],Continue[]];
  AppendTo[raw5,{ws,amp/(-I)}];],{400}];
testAll[5, raw5];
