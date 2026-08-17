Get["fu_defs.m"];
n=5; sig=Join[{-1,-1},Table[1,n-2]];
(* channel factor F_S = (sum_{i in S} w_i)^2 - sum_{i in S} sigma_i w_i^2, for proper subsets S, 2<=|S|<=n-2, modulo complement (F_S=F_{Sbar} on-shell). *)
allS=Select[Subsets[Range[n],{2,n-2}],True&];
(* dedupe by complement: keep S with 1 in S, or smallest *)
reps={};seen={};
Do[ co=Complement[Range[n],S]; key=Sort[{S,co}]; If[!MemberQ[seen,key],AppendTo[seen,key];AppendTo[reps,S]],{S,allS}];
Print["channel reps=",reps];
Fsym[S_,w_]:=(Total[w[[S]]])^2 - Total[Table[sig[[i]] w[[i]]^2,{i,S}]];
(* Denominator candidate = product over reps of Fsym. degree each =2, total deg = 2*len. *)
ndeg=2*Length[reps];
Print["denominator degree=",ndeg];
(* A degree6 => numerator degree = 6+ndeg. Numerator generic polynomial in w1..w5 homogeneous deg (6+ndeg), but on-shell constraints reduce variables. Use free vars: w2,w3,w_{n-1} (n-2=3 free) plus parametrize.
   Simpler: fit numerator as polynomial in the SAME channel factors + symmetric building blocks. 
   Hard. Instead: directly fit A * Denominator = Numerator(poly in w). Sample many rational pts, 
   require numerator be polynomial of total degree 6+ndeg in w1..wn (homogeneous). *)
(* Get data *)
data={};
SeedRandom[5];
While[Length[data]<400,
 fw=Table[RandomInteger[{-9,9}],{n-2}];
 If[Total[fw]==0,Continue[]];
 {ks,ws}=Quiet[Check[MakeKinematics[n,fw,sig,1],$Failed]];
 If[ws===$Failed||!FreeQ[ws,ComplexInfinity]||MemberQ[ws,0],Continue[]];
 amp=Quiet[Check[BGAmplitude[ks,ws,1]/I,$Failed]];
 If[amp===$Failed||!FreeQ[amp,Indeterminate|ComplexInfinity],Continue[]];
 AppendTo[data,{ws,amp}];
];
Print["data pts=",Length[data]];
(* numerator monomials: homogeneous deg d in w1..w5 *)
d=6+ndeg;
mons=Select[Tuples[Range[0,d],n],Total[#]==d&];
Print["raw num monomials (deg ",d,")=",Length[mons]," (too many)"];
