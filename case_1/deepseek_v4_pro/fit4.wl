(* Generate A4 data and try to find formula *)

mag[k_]:=Abs[k];
FKernelSafe[3,ps_]:=Module[{a,b},a=mag[ps[[1]]];b=mag[ps[[2]]];If[a==0||b==0,-1,-1-ps[[1]]*ps[[2]]/(a*b)]];
EKernel[3,ps_]:=-1/2(mag[ps[[1]]]*mag[ps[[2]]]+ps[[1]]*ps[[2]]);
EKernel[n_/;n>=4,ps_]:=Module[{p1=ps[[1]],p2=ps[[2]],r=ps[[3;;]],q2,rst},q2=mag[p2];rst=q2^(n-3)*EKernel[3,{p1,p2,Total[r]}]/(n-2)!;Do[rst-=q2^m/m!*EKernel[n-m,Join[{p1,p2+Total[r[[1;;m]]]},r[[m+1;;]]]],{m,1,n-3}];rst];
FKernelSafe[n_/;n>=4,ps_]:=Module[{p1=ps[[1]],p2=ps[[2]],r=ps[[3;;]],q1,q2,rst,sM},q1=mag[p1];q2=mag[p2];If[q1==0||q2==0,Return[0]];rst=2*EKernel[n,ps]/q1;Do[sM=p2+Total[r[[1;;m]]];rst-=2*EKernel[m+2,Join[{-sM,p2},r[[1;;m]]]]*FKernelSafe[n-m,Join[{p1,sM},r[[m+1;;]]]],{m,1,n-3}];rst/q2];
VertexSafe[n_,moms_,omegas_]:=Module[{r=0},Do[r+=omegas[[p[[1]]]]*omegas[[p[[2]]]]*FKernelSafe[n,moms[[p]]],{p,Permutations[Range[n]]}];(-I/2)*r];
Propagator[w_,k_,g_]:=-I/(w^2/mag[k]-g);
SetPartitions[S_List,1]:={{S}};
SetPartitions[S_List,k_]/;k>Length[S]:={};
SetPartitions[S_List,k_]:=Module[{mn=Min[S],r={}},Do[Module[{fp=Join[{mn},sub],rem,sps},rem=Complement[S,fp];If[Length[rem]>=k-1,sps=SetPartitions[rem,k-1];Do[AppendTo[r,Join[{fp},sp]],{sp,sps}]]],{sub,Subsets[Complement[S,{mn}],{0,Length[S]-k}]}];r];
Clear[BGCurrent];BGCurrent[{i_Integer}]:=1;
BGCurrent[S_List]:=BGCurrent[S]=Module[{wS,kS,r=0,sMs,sWs,vMs,vWs},wS=Total[$wList[[S]]];kS=Total[$kList[[S]]];If[kS==0,Return[0]];Do[Do[sMs=Table[Total[$kList[[part[[j]]]]],{j,m}];sWs=Table[Total[$wList[[part[[j]]]]],{j,m}];vMs=Prepend[sMs,-kS];vWs=Prepend[sWs,-wS];r+=VertexSafe[m+1,vMs,vWs]*Product[BGCurrent[part[[j]]],{j,m}],{part,SetPartitions[S,m]}],{m,2,Length[S]}];r*Propagator[wS,kS,$gVal]];
BGAmplitude[moms_,ws_,g_]:=Module[{n=Length[moms],rest,r=0},$kList=moms;$wList=ws;$gVal=g;DownValues[BGCurrent]=Select[DownValues[BGCurrent],!FreeQ[#,Pattern|Blank]&];rest=Range[2,n];Do[Do[Module[{sMs,sWs,vMs,vWs},sMs=Table[Total[$kList[[part[[j]]]]],{j,m}];sWs=Table[Total[$wList[[part[[j]]]]],{j,m}];vMs=Prepend[sMs,$kList[[1]]];vWs=Prepend[sWs,$wList[[1]]];r+=VertexSafe[m+1,vMs,vWs]*Product[BGCurrent[part[[j]]],{j,m}]],{part,SetPartitions[rest,m]}],{m,2,n-1}];r];
MakeKinematics[n_,freeW_,sigmas_,g_]:=Module[{sumFree,sigmaFree,sSW2,wn,w1,allW,allK},sumFree=Total[freeW];sigmaFree=sigmas[[2;;n-1]];sSW2=Total[sigmaFree*freeW^2];wn=-(sigmas[[1]]*sumFree^2+sSW2)/(2*sigmas[[1]]*sumFree);w1=-(sumFree+wn);allW=Join[{w1},freeW,{wn}];allK=sigmas*allW^2/g;{allK,allW}];

gVal=1;

(* A4 formula exploration *)
Print["=== A4 formula exploration ==="];
Print["Using parametrization: w1=-w3, w2=w2, w3=w3, w4=-w2 (from MakeKinematics)"];
Print["A4 is pure imaginary. Let A4hat = A4/I (real)"];
Print[""];

(* Generate data *)
data = {};
Do[
  w2 = i; w3 = j;
  sigmas = {-1,-1,1,1};
  {ks, ws} = MakeKinematics[4, {w2, w3}, sigmas, gVal];
  amp = BGAmplitude[ks, ws, gVal];
  a4hat = amp/I;
  AppendTo[data, {{w2, w3}, a4hat}];
  , {i, 1, 5}, {j, 1, 5}];

Print["A4/I values (w2 rows, w3 cols):"];
Do[
  vals = Table[Select[data, #[[1,1]]==w2 && #[[1,2]]==w3 &][[1,2]], {w3,1,5}];
  Print["  w2=",w2,": ", N[vals]];
  , {w2, 1, 5}];

Print[""];
Print["Let me try: A4/I = w2*w3*(w2^2+w3^2) ?"];
Do[
  w2=i; w3=j;
  {ks,ws}=MakeKinematics[4,{w2,w3},{-1,-1,1,1},gVal];
  amp=BGAmplitude[ks,ws,gVal];
  pred = -w2*w3*(w2^2+w3^2);  (* sign? *)
  Print["  w2=",w2," w3=",w3,": actual=",N[amp/I]," pred=",pred," ratio=",N[(amp/I)/pred]];
  ,{i,1,5},{j,1,5}];

Print[""];
Print["Let me try: A4/I = w2^2*w3^2?"];
Do[
  w2=i; w3=j;
  {ks,ws}=MakeKinematics[4,{w2,w3},{-1,-1,1,1},gVal];
  amp=BGAmplitude[ks,ws,gVal];
  pred = w2^2*w3^2;
  Print["  w2=",w2," w3=",w3,": actual=",N[amp/I]," pred=",pred," ratio=",N[(amp/I)/pred]];
  ,{i,1,3},{j,1,3}];
