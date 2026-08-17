(* Fit A5 formula using linear system *)

mag[k_]:=Abs[k];
FK3[3,ps_]:=Module[{a,b},a=mag[ps[[1]]];b=mag[ps[[2]]];If[a==0||b==0,-1,-1-ps[[1]]*ps[[2]]/(a*b)]];
EK[3,ps_]:=-1/2(mag[ps[[1]]]*mag[ps[[2]]]+ps[[1]]*ps[[2]]);
EK[n_/;n>=4,ps_]:=Module[{p1=ps[[1]],p2=ps[[2]],r=ps[[3;;]],q2,rst},q2=mag[p2];rst=q2^(n-3)*EK[3,{p1,p2,Total[r]}]/(n-2)!;Do[rst-=q2^m/m!*EK[n-m,Join[{p1,p2+Total[r[[1;;m]]]},r[[m+1;;]]]],{m,1,n-3}];rst];
FK3[n_/;n>=4,ps_]:=Module[{p1=ps[[1]],p2=ps[[2]],r=ps[[3;;]],q1,q2,rst,sM},q1=mag[p1];q2=mag[p2];If[q1==0||q2==0,Return[0]];rst=2*EK[n,ps]/q1;Do[sM=p2+Total[r[[1;;m]]];rst-=2*EK[m+2,Join[{-sM,p2},r[[1;;m]]]]*FK3[n-m,Join[{p1,sM},r[[m+1;;]]]],{m,1,n-3}];rst/q2];
Vtx[n_,moms_,omegas_]:=Module[{r=0},Do[r+=omegas[[p[[1]]]]*omegas[[p[[2]]]]*FK3[n,moms[[p]]],{p,Permutations[Range[n]]}];(-I/2)*r];
Prop[w_,k_,g_]:=-I/(w^2/mag[k]-g);
SP[S_List,1]:={{S}};SP[S_List,k_]/;k>Length[S]:={};SP[S_List,k_]:=Module[{mn=Min[S],r={}},Do[Module[{fp=Join[{mn},sub],rem,sps},rem=Complement[S,fp];If[Length[rem]>=k-1,sps=SP[rem,k-1];Do[AppendTo[r,Join[{fp},sp]],{sp,sps}]]],{sub,Subsets[Complement[S,{mn}],{0,Length[S]-k}]}];r];
Clear[BGJ];BGJ[{i_Integer}]:=1;
BGJ[S_List]:=BGJ[S]=Module[{wS,kS,r=0,sMs,sWs,vMs,vWs},wS=Total[$wList[[S]]];kS=Total[$kList[[S]]];If[kS==0,Return[0]];Do[Do[sMs=Table[Total[$kList[[part[[j]]]]],{j,m}];sWs=Table[Total[$wList[[part[[j]]]]],{j,m}];vMs=Prepend[sMs,-kS];vWs=Prepend[sWs,-wS];r+=Vtx[m+1,vMs,vWs]*Product[BGJ[part[[j]]],{j,m}],{part,SP[S,m]}],{m,2,Length[S]}];r*Prop[wS,kS,$gVal]];
BGA[moms_,ws_,g_]:=Module[{n=Length[moms],rest,r=0},$kList=moms;$wList=ws;$gVal=g;DownValues[BGJ]=Select[DownValues[BGJ],!FreeQ[#,Pattern|Blank]&];rest=Range[2,n];Do[Do[Module[{sMs,sWs,vMs,vWs},sMs=Table[Total[$kList[[part[[j]]]]],{j,m}];sWs=Table[Total[$wList[[part[[j]]]]],{j,m}];vMs=Prepend[sMs,$kList[[1]]];vWs=Prepend[sWs,$wList[[1]]];r+=Vtx[m+1,vMs,vWs]*Product[BGJ[part[[j]]],{j,m}]],{part,SP[rest,m]}],{m,2,n-1}];r];
MK[n_,fw_,sig_,g_]:=Module[{sf,sfree,sSW2,wn,w1,aW,aK},sf=Total[fw];sfree=sig[[2;;n-1]];sSW2=Total[sfree*fw^2];wn=-(sig[[1]]*sf^2+sSW2)/(2*sig[[1]]*sf);w1=-(sf+wn);aW=Join[{w1},fw,{wn}];aK=sig*aW^2/g;{aK,aW}];

gVal=1;

(* Compute A5 at many points, try to identify simple formula *)
Print["=== Computing A5 at many random points ==="];
data = {};
Do[
  fw = Table[RandomInteger[{1,8}], {3}];
  sigmas = {-1,-1,1,1,1};
  {ks,ws} = MK[5, fw, sigmas, gVal];
  anyZ = False;
  Do[If[Total[ks[[s]]]==0, anyZ=True; Break[]], {s, Subsets[Range[2,5], {2,3}]}];
  If[!anyZ,
    amp = BGA[ks, ws, gVal];
    If[amp =!= Indeterminate,
      AppendTo[data, {fw, ws, amp/I}]];
  ];
  , {30}];

Print["Got ", Length[data], " points"];
Print[""];

(* Try to see pattern: A5/I = -4 * w2*w3*w4 * something? *)
Print["Testing various product formulas:"];
Do[
  {fw, ws, val} = data[[i]];
  w2=fw[[1]]; w3=fw[[2]]; w4=fw[[3]];
  prod = w2*w3*w4;
  Print["  free=",fw," A5/I=",N[val]," A5/(I*w2*w3*w4)=",N[val/prod]];
  , {i, 1, Min[10, Length[data]]}];

Print[""];
Print["Now test with squared omegas:"];
Do[
  {fw, ws, val} = data[[i]];
  w = ws; (* full frequency list *)
  a = w^2; (* squared frequencies *)
  prod2 = a[[1]]*a[[2]]*a[[3]]*a[[4]]*a[[5]];
  Print["  ws=",N[w]," A5/I=",N[val,12]," A5/(I*prod_a)=",N[val/prod2,12]];
  , {i, 1, Min[8, Length[data]]}];
