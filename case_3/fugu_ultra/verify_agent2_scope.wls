Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
pp[x_]:=If[x>0,x,0];
TP[m_,t_,a_List]:=Sum[(-1)^Length[S] pp[t-Total[S]]^m,{S,Subsets[a]}];
Agent2[ws_,g_]:=Module[{n=Length[ws],m,cands,a,p,q,R},
  m=n-3;
  cands=Select[{1,2},Function[a2,Length[Select[Range[3,n],Sign[ws[[#]]]==Sign[ws[[a2]]]&]]==m]];
  If[Length[cands]<1,Return[$Failed]];
  a=cands[[1]]; p=ws[[a]]; q=ws[[3-a]];
  R=Select[Range[3,n],Sign[ws[[#]]]==Sign[p]&];
  I*2^(n-1)*q*p*TP[m,p^2,ws[[R]]^2]/g^(n-3)];
SeedRandom[7];
Do[
  okcov=0; failcov=0; gap=0;
  Do[
    free=Table[RandomInteger[{-7,7}]+RandomChoice[{1/3,1/2,1,3/2,5/2}],{n-2}];
    sig=Join[{-1,-1},Table[1,n-2]];
    {ks,ws}=MakeKinematics[n,free,sig,1];
    If[MemberQ[ws,0]||MemberQ[ks,0],Continue[]];
    bg=Quiet[BGAmplitude[ks,ws,1]];
    fm=Agent2[ws,1];
    If[fm===$Failed, gap++; Continue[]];
    If[bg===fm || PossibleZeroQ[bg-fm], okcov++, failcov++; If[failcov<=3,Print["MISMATCH n=",n," ws=",InputForm[ws]," bg=",InputForm[bg]," fm=",InputForm[fm]]]],
    {120}];
  Print["n=",n,": covered-correct=",okcov,", covered-WRONG=",failcov,", gap($Failed)=",gap],
  {n,{5,6,7}}]
