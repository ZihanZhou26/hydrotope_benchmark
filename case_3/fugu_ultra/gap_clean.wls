Get[FileNameJoin[{DirectoryName[$InputFileName], "loader.wls"}]];
pp[x_]:=If[x>0,x,0];
TP[m_,t_,a_List]:=Sum[(-1)^Length[S] pp[t-Total[S]]^m,{S,Subsets[a]}];
(* agent2 generalized: try BOTH minus legs as p; need a plus-subset R of size n-3
   among plus legs SHARING SIGN with p. Returns list of candidate values. *)
cand[ws_,g_]:=Module[{n=Length[ws],m=Length[ws]-3,res={},p,q,R},
  Do[ p=ws[[a]]; q=ws[[3-a]];
      R=Select[Range[3,n],Sign[ws[[#]]]==Sign[p]&];
      If[Length[R]==m, AppendTo[res, I*2^(n-1)*q*p*TP[m,p^2,ws[[R]]^2]/g^(n-3)]],
   {a,{1,2}}];
  res];
SeedRandom[123];
Do[
  cov=0;mis=0;gap=0;deg=0;both=0;
  Do[
    free=N[Table[RandomReal[{-6,6}],{n-2}],30];
    sig=Join[{-1,-1},Table[1,n-2]];
    {ks,ws}=MakeKinematics[n,free,sig,1];
    bg=Quiet[BGAmplitude[ks,ws,1]];
    If[!NumberQ[bg]||!FreeQ[bg,Indeterminate]||!FreeQ[bg,ComplexInfinity]||Abs[bg]>10^40||Abs[bg]<10^-30, deg++; Continue[]];
    cs=cand[ws,1];
    If[Length[cs]==0, gap++; Continue[]];
    If[Length[cs]==2, both++];
    ok=Or@@(Abs[#-bg]/Max[1,Abs[bg]]<10^-9&/@cs);
    If[ok,cov++,mis++; If[mis<=2,Print["MIS n=",n," bg=",bg," cands=",cs]]],
    {300}];
  Print["n=",n,": covered=",cov,", miscovered=",mis,", uncovered-gap=",gap,", degenerate-skipped=",deg,", (both-cands cases=",both,")"],
  {n,{4,5,6,7}}]
