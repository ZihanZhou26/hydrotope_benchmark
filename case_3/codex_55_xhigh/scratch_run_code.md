# Scratch Code And Commands

This file records the substantive code snippets and commands I ran while
working out the formula.  Some of the earliest directory-inspection commands
looked at the case layout before I read the prompt restriction; the actual
formula search used only `prompt.md`, `OnShellBG.m`, and generated data.

## Initial orientation

```sh
pwd && rg --files waterhedron_benchmark_blind/case_3 waterhedron_benchmark_blind_case_3 2>/dev/null | head -200
```

```sh
find /home/zihanz -maxdepth 3 \( -path '*/waterhedron_benchmark_blind/case_3' -o -path '*/waterhedron_benchmark_blind_case_3' \) -print
```

```sh
sed -n '1,240p' prompt.md
```

```sh
sed -n '1,260p' OnShellBG.m
```

```sh
find claude_opus_48_max -maxdepth 1 -type f -printf '%f\n' | sort
```

```sh
command -v wolframscript || true
command -v math || true
python3 --version
```

## Low-point exact BG probes

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; gVal=1; Do[sig=Join[{-1,-1},Table[1,n-2]]; free=Range[2,n-1]; {ks,ws}=MakeKinematics[n,free,sig,gVal]; amp=BGAmplitude[ks,ws,gVal]; Print["n=",n," ws=",ws," amp=",Simplify[amp]," N=",N[amp,20]],{n,4,7}]'
```

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; g=1; cases={{5,{2,5/2,3}},{5,{1,3,5}},{5,{2,7,11}},{5,{1/3,2,9}},{6,{2,3,5,7}},{6,{1,4,9,16}},{7,{2,3,5,7,11}}}; Do[n=c[[1]]; free=c[[2]]; sig=Join[{-1,-1},Table[1,n-2]]; {ks,ws}=MakeKinematics[n,free,sig,g]; amp=Simplify[BGAmplitude[ks,ws,g]]; Print["DATA n=",n," free=",free," ws=",ws," amp=",amp," real=",Re[amp/I]*(-1)];,{c,cases}]'
```

## Ratio and invariant checks

```python
from fractions import Fraction
samples=[
(5,[Fraction(-9,2),Fraction(2),Fraction(5,2),Fraction(3),Fraction(-3)],Fraction(2304)),
(5,[Fraction(-19,3),Fraction(1),Fraction(3),Fraction(5),Fraction(-8,3)],Fraction(304,3)),
(5,[Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)],Fraction(36224,5)),
(5,[Fraction(-160,17),Fraction(1,3),Fraction(2),Fraction(9),Fraction(-98,51)],Fraction(2560,4131)),
(6,[Fraction(-184,17),Fraction(2),Fraction(3),Fraction(5),Fraction(7),Fraction(-105,17)],Fraction(753664,17)),
(6,[Fraction(-313,15),Fraction(1),Fraction(4),Fraction(9),Fraction(16),Fraction(-137,15)],Fraction(10016,15)),
]
for n,ws,B in samples:
    prod=Fraction(1)
    for w in ws: prod*=w
    prodpos=Fraction(1)
    for w in ws[2:]: prodpos*=w
    prodneg=ws[0]*ws[1]
    print('n',n,'B',B,'prod',prod,'B/prod',B/prod,'prodpos',prodpos,'B/prodpos',B/prodpos,'prodneg',prodneg)
    P=sum(ws[2:])
    Q=sum(w*w for w in ws[2:])
    e2=sum(ws[i]*ws[j] for i in range(2,n) for j in range(i+1,n))
    print(' positives P,Q,e2',P,Q,e2,'negprod',prodneg)
    print('B/(prodpos*prodneg)', B/(prodpos*prodneg))
```

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; Clear[w1,w2,w3,w4,w5]; ks={-w1^2,-w2^2,w3^2,w4^2,w5^2}; ws={w1,w2,w3,w4,w5}; amp=BGAmplitude[ks,ws,1]; Print[StringTake[ToString[InputForm[amp]],UpTo[4000]]];'
```

```python
from fractions import Fraction
samples=[
([Fraction(-9,2),Fraction(2),Fraction(5,2),Fraction(3),Fraction(-3)],Fraction(2304)),
([Fraction(-19,3),Fraction(1),Fraction(3),Fraction(5),Fraction(-8,3)],Fraction(304,3)),
([Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)],Fraction(36224,5)),
([Fraction(-160,17),Fraction(1,3),Fraction(2),Fraction(9),Fraction(-98,51)],Fraction(2560,4131)),
]
for ws,B in samples:
    pos=ws[2:]
    e1=sum(pos)
    e2=sum(pos[i]*pos[j] for i in range(3) for j in range(i+1,3))
    e3=pos[0]*pos[1]*pos[2]
    print('pos',pos,'e1,e2,e3',e1,e2,e3,'B',B)
    candidates={
        'e1*e2*e3': e1*e2*e3,
        'e2^2': e2*e2,
        'e1^2*e2': e1*e1*e2,
        'e1^3*e3': e1**3*e3,
        'e2*e3': e2*e3,
        'e1*e3': e1*e3,
        'e3': e3,
        'e2/e3': e2/e3,
    }
    for k,v in candidates.items():
        if v: print(' ',k, 'B/v=', B/v)
```

## Failed pure symmetric polynomial fit

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs];
monos[e1_,e2_,e3_]:={e1^6,e1^4 e2,e1^3 e3,e1^2 e2^2,e1 e2 e3,e2^3,e3^2};
raw={{2,5/2,3},{1,3,5},{2,7,11},{1/3,2,9},{3,4,8},{5,6,13},{2,9,10},{4,7,17},{3/2,11/3,8},{7/5,4,19/2}};
rows={}; vals={};
Do[
 sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,fw,sig,1]; amp=Simplify[BGAmplitude[ks,ws,1]]; B=Simplify[I amp];
 pos=ws[[3;;5]]; e1=Total[pos]; e2=Sum[pos[[i]] pos[[j]],{i,1,2},{j,i+1,3}]; e3=Times@@pos;
 AppendTo[rows,monos[e1,e2,e3]]; AppendTo[vals,B];
 Print["pt ",fw," B=",B," e=",{e1,e2,e3}];
,{fw,raw}];
coeff=LinearSolve[rows[[1;;7]],vals[[1;;7]]]; Print["coeff=",coeff];
Do[pred=Simplify[rows[[i]].coeff]; Print["check ",i," diff=",Simplify[pred-vals[[i]]]],{i,Length[rows]}];
'
```

## Symmetry and kernel probes

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{2,5/2,3},sig,1]; Print["orig ws=",ws," ks=",ks," amp=",Simplify[BGAmplitude[ks,ws,1]]]; perms={{1,2,3,4,5},{2,1,3,4,5},{1,2,4,3,5},{3,2,1,4,5},{5,2,3,4,1}}; Do[p=p0; Print[p," sigmas=",Sign[ks[[p]]]," amp=",Simplify[BGAmplitude[ks[[p]],ws[[p]],1]]],{p0,perms}]'
```

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; tests={{1,2,3,4},{1,3,5,7},{-1,-2,-3,-4},{1,-2,3,4},{-1,2,3,4},{3,4,-1,2}}; Do[Print["ps=",ps," F3prefix=",If[Length[ps]>=3,FKernel[3,ps[[1;;3]]],""]," F4=",If[Length[ps]>=4,Simplify[FKernel[4,ps]],""]],{ps,tests}]; Do[Print["n=",n," allpos=",Simplify[FKernel[n,Range[n]]]],{n,3,7}]'
```

## More chamber data

```python
from fractions import Fraction
samples=[
([Fraction(-9,2),Fraction(2),Fraction(5,2),Fraction(3),Fraction(-3)],Fraction(2304)),
([Fraction(-19,3),Fraction(1),Fraction(3),Fraction(5),Fraction(-8,3)],Fraction(304,3)),
([Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)],Fraction(36224,5)),
([Fraction(-160,17),Fraction(1,3),Fraction(2),Fraction(9),Fraction(-98,51)],Fraction(2560,4131)),
([Fraction(-184,17),Fraction(2),Fraction(3),Fraction(5),Fraction(7),Fraction(-105,17)],Fraction(753664,17)),
([Fraction(-313,15),Fraction(1),Fraction(4),Fraction(9),Fraction(16),Fraction(-137,15)],Fraction(10016,15)),
]
for ws,B in samples:
    n=len(ws)
    prod=Fraction(1)
    for w in ws: prod*=w
    d=ws[0]-ws[1]
    pos=ws[2:]
    P=sum(pos)
    Q=sum(w*w for w in pos)
    print('\nn',n,'ws',ws,'B',B)
    for expr,name in [(prod,'prod'),(prod*d*d,'prod*d2'),(prod/(d*d) if d else 0,'prod/d2'),(prod*P,'prod*P'),(prod*P*P,'prod*P2'),(prod*Q,'prod*Q'),(prod*sum(abs(w) for w in pos),'prod*sumabspos')]:
        if expr: print(name, 'ratio', B/expr, 'float', float(B/expr))
```

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; cases={{-2,1,10},{-3,1,12},{-1,2,20},{-5,2,30},{-1/2,1,8},{-4,3,25}}; Do[sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,fw,sig,1]; amp=Simplify[BGAmplitude[ks,ws,1]]; Print["fw=",fw," ws=",ws," amp=",amp," B=",I amp],{fw,cases}]'
```

```python
from fractions import Fraction
samples=[([Fraction(-89,9),Fraction(-2),Fraction(1),Fraction(10),Fraction(8,9)], Fraction(-364544,729)),
([Fraction(-59,5),Fraction(-3),Fraction(1),Fraction(12),Fraction(9,5)], Fraction(-458784,125)),
([Fraction(-268,9),Fraction(-5),Fraction(2),Fraction(30),Fraction(25,9)], Fraction(-107200000,729)),
([Fraction(-199,8),Fraction(-4),Fraction(3),Fraction(25),Fraction(7,8)], Fraction(-87759,4))]
for ws,B in samples:
    prod=Fraction(1)
    for w in ws: prod*=w
    print(ws,'B',B,'prod',prod,'B/prod',B/prod)
    vals=[abs(w) for w in ws]
    print('abs',vals,'min',min(vals),'max',max(vals))
    for p in range(1,5):
        print('B/(prod*min^%d)'%p, B/(prod*min(vals)**p))
```

```python
from fractions import Fraction
samples=[
([Fraction(-9,2),Fraction(2),Fraction(5,2),Fraction(3),Fraction(-3)],Fraction(2304)),
([Fraction(-19,3),Fraction(1),Fraction(3),Fraction(5),Fraction(-8,3)],Fraction(304,3)),
([Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)],Fraction(36224,5)),
([Fraction(-160,17),Fraction(1,3),Fraction(2),Fraction(9),Fraction(-98,51)],Fraction(2560,4131)),
([Fraction(-89,9),Fraction(-2),Fraction(1),Fraction(10),Fraction(8,9)],Fraction(-364544,729)),
]
for ws,B in samples:
    sig=[-1,-1]+[1]*(len(ws)-2)
    for p in [3,4,5]:
        S=sum(Fraction(s)*w**p for s,w in zip(sig,ws))
        if S: print('p',p,'B/S^2',B/(S*S),'B/S',B/S)
    Splain=sum(w**3 for w in ws)
    print('plain3',B/(Splain*Splain) if Splain else None,'Ssig3',sum(s*w**3 for s,w in zip(sig,ws)))
    print()
```

## Fixed simple family across n

This run was stopped while the `n=8` exact point was still taking too long.

```sh
wolframscript -code 'defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; Do[n=m; sig=Join[{-1,-1},Table[1,n-2]]; free=Range[2,n-1]; {ks,ws}=MakeKinematics[n,free,sig,1]; amp=Simplify[BGAmplitude[ks,ws,1]]; prod=Times@@ws; Print["n=",n," ws=",ws," Iamp=",Simplify[I amp]," Iamp/prod=",Simplify[I amp/prod]],{m,5,8}]'
```

## Five-point chamber factorization

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; Clear[a,b,c]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{a,b,c},sig,1]; amp=BGAmplitude[ks,ws,1]; sample={a->-3,b->1,c->12}; absArgs=DeleteDuplicates[Cases[amp,Abs[x_]:>x,Infinity]]; Print["num abs=",Length[absArgs]]; repl=Table[Abs[x]->Sign[N[x/.sample]] x,{x,absArgs}]; expr=FullSimplify[amp/.repl]; Print["ws=",ws]; Print["expr=",Factor[expr]]; Print["check=",Simplify[(expr/.sample) - (BGAmplitude[ks/.sample,ws/.sample,1])]];
'
```

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; Clear[a,b,c]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{a,b,c},sig,1]; amp=BGAmplitude[ks,ws,1]; samples={{a->-3,b->1,c->12},{a->2,b->3,c->5},{a->2,b->7,c->11},{a->1/3,b->2,c->9},{a->3,b->4,c->8},{a->4,b->7,c->17}}; Do[absArgs=DeleteDuplicates[Cases[amp,Abs[x_]:>x,Infinity]]; repl=Table[Abs[x]->Sign[N[x/.s]] x,{x,absArgs}]; expr=Factor[FullSimplify[amp/.repl]]; Print["sample=",s," ws=",ws/.s," expr=",expr," check=",Simplify[(expr/.s)-BGAmplitude[ks/.s,ws/.s,1]]],{s,samples}]
'
```

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; Clear[a,b,c]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{a,b,c},sig,1]; amp=BGAmplitude[ks,ws,1]; absArgs=DeleteDuplicates[Cases[amp,Abs[x_]:>x,Infinity]];
samples={{2,3,5},{-3,1,12},{-2,1,10},{-5,2,30},{2,-3,10},{2,10,-3},{-2,10,-3},{5,-1,12},{5,12,-1},{-1,5,12},{1,-5,12},{1,12,-5},{4,1,8},{4,8,1},{-4,8,1},{-4,1,8},{8,1,4},{8,4,1},{1,4,8},{1,8,4}};
seen=<||>;
Do[s={a->t[[1]],b->t[[2]],c->t[[3]]}; If[Denominator[ws[[5]]/.s]===0,Continue[]]; If[Or@@Thread[(ws/.s)==0],Continue[]];
 repl=Table[Abs[x]->Sign[N[x/.s]] x,{x,absArgs}]; expr=Factor[FullSimplify[amp/.repl]];
 key=ToString[InputForm[expr]]; If[!KeyExistsQ[seen,key], seen[key]=1; Print["--- sample ",t," ws=",ws/.s," sortedAbs=",Sort[Transpose[{Abs[ws/.s],Range[5],ws/.s}]],"\n",expr,"\n"]];
,{t,samples}]; Print["unique=",Length[Keys[seen]]];
'
```

## Spline/finite-difference false start

```python
from fractions import Fraction

def dd(xs, m, plus=True, absf=False):
    ys=[]
    for x in xs:
        if plus:
            y=x**m if x>0 else Fraction(0)
        elif absf:
            y=abs(x)**m
        else:
            y=x**m
        ys.append(y)
    n=len(xs)
    coef=ys[:]
    for j in range(1,n):
        coef=[(coef[i+1]-coef[i])/(xs[i+j]-xs[i]) for i in range(n-j)]
    return coef[0]

samples=[
([Fraction(-13,2),Fraction(2),Fraction(3),Fraction(5),Fraction(-7,2)], Fraction(3328)),
([Fraction(-59,5),Fraction(-3),Fraction(1),Fraction(12),Fraction(9,5)], Fraction(-458784,125)),
([Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)], Fraction(36224,5)),
([Fraction(-109,13),Fraction(4),Fraction(1),Fraction(8),Fraction(-60,13)], None),]
for ws,B in samples:
    print('ws',ws,'B',B)
    prod=Fraction(1)
    for w in ws: prod*=w
    for m in range(4,12):
        d=dd(ws,m,plus=True)
        if d: print(' m',m,'B/(prod*dd+)', B/(prod*d) if B else 'dd',d,'prod*dd',prod*d)
    print('abs')
    for m in range(4,12):
        d=dd(ws,m,plus=False,absf=True)
        if d: print(' m',m,'ratio', B/(prod*d) if B else d)
    print()
```

```python
from fractions import Fraction

def lag_sum(ws, weights, m):
    s=Fraction(0)
    n=len(ws)
    for i,w in enumerate(ws):
        den=Fraction(1)
        for j,u in enumerate(ws):
            if i!=j: den*=w-u
        s += weights[i]*w**m/den
    return s

samples=[
([Fraction(-13,2),Fraction(2),Fraction(3),Fraction(5),Fraction(-7,2)], Fraction(3328)),
([Fraction(-59,5),Fraction(-3),Fraction(1),Fraction(12),Fraction(9,5)], Fraction(-458784,125)),
([Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)], Fraction(36224,5)),
([Fraction(-160,17),Fraction(1,3),Fraction(2),Fraction(9),Fraction(-98,51)], Fraction(2560,4131)),
([Fraction(-184,17),Fraction(2),Fraction(3),Fraction(5),Fraction(7),Fraction(-105,17)], Fraction(753664,17)),
]
for name,wfun in [('ones',lambda ws,sig:[1]*len(ws)),('sigma',lambda ws,sig:sig),('tau',lambda ws,sig:[1 if w>0 else -1 for w in ws]),('sig*tau',lambda ws,sig:[sig[i]*(1 if ws[i]>0 else -1) for i in range(len(ws))])]:
    print('\n',name)
    for ws,B in samples:
        n=len(ws); sig=[-1,-1]+[1]*(n-2)
        prod=Fraction(1)
        for w in ws: prod*=w
        L=lag_sum(ws,wfun(ws,sig),2*n-5)
        val=prod*L
        print('n',n,'B/val', B/val if val else None,'L',L)
```

```python
from fractions import Fraction

def lag(nodes, weights, m):
    s=Fraction(0); n=len(nodes)
    for i,x in enumerate(nodes):
        den=Fraction(1)
        for j,y in enumerate(nodes):
            if i!=j: den*=x-y
        s+=weights[i]*x**m/den
    return s

samples=[
([Fraction(-13,2),Fraction(2),Fraction(3),Fraction(5),Fraction(-7,2)], Fraction(3328)),
([Fraction(-59,5),Fraction(-3),Fraction(1),Fraction(12),Fraction(9,5)], Fraction(-458784,125)),
([Fraction(-283,20),Fraction(2),Fraction(7),Fraction(11),Fraction(-117,20)], Fraction(36224,5)),
([Fraction(-184,17),Fraction(2),Fraction(3),Fraction(5),Fraction(7),Fraction(-105,17)], Fraction(753664,17)),]
nodefuns=[('w',lambda ws,sig:ws),('sigw',lambda ws,sig:[sig[i]*ws[i] for i in range(len(ws))]),('absw',lambda ws,sig:[abs(w) for w in ws]),('sigabs',lambda ws,sig:[sig[i]*abs(ws[i]) for i in range(len(ws))])]
weightfuns=[('1',lambda ws,sig:[1]*len(ws)),('sig',lambda ws,sig:sig),('tau',lambda ws,sig:[1 if w>0 else -1 for w in ws]),('sigtau',lambda ws,sig:[sig[i]*(1 if ws[i]>0 else -1) for i in range(len(ws))])]
for nf,nfun in nodefuns:
  for wf,wfun in weightfuns:
    ratios=[]
    ok=True
    for ws,B in samples:
      n=len(ws); sig=[-1,-1]+[1]*(n-2)
      nodes=nfun(ws,sig)
      if len(set(nodes))<len(nodes): ok=False; break
      prod=Fraction(1)
      for w in ws: prod*=w
      L=lag(nodes,wfun(ws,sig),2*n-5)
      val=prod*L
      if val==0: ok=False; break
      ratios.append(B/val)
    if ok and len(set(ratios))==1:
      print('constant',nf,wf,ratios[0])
```

## Symbolic simplification attempt that exhausted resources

This broad simplification was attempted and the Wolfram process exited with a
license/error after consuming too much memory.

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; Clear[a,b,c]; sig={-1,-1,1,1,1}; {ks,ws}=MakeKinematics[5,{a,b,c},sig,1]; amp=Together[BGAmplitude[ks,ws,1]]; w1=ws[[1]]; rat=Together[amp/(16 I w1)]; Print["leaf raw=",LeafCount[rat]," bytes=",StringLength[ToString[InputForm[rat]]]]; simp=TimeConstrained[FullSimplify[rat],20,rat]; Print["leaf simp=",LeafCount[simp]," bytes=",StringLength[ToString[InputForm[simp]]]]; Print[StringTake[ToString[InputForm[simp]],UpTo[6000]]];
'
```

## First candidate verification, partially failing

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs];
Clear[ClampedPower,ClosedA];
ClampedPower[U_, xs_List] := Module[{m=Length[xs]-1, knots=Sort[xs], z, expr, order, coeff}, expr=z^m; Do[If[U < knots[[r]], Break[]]; order=m-r+1; coeff=(D[expr,{z,order}]/.z->knots[[r]])/order!; expr=Expand[expr-coeff*(z-knots[[r]])^order],{r,1,m}]; Simplify[expr/.z->U]];
ClosedA[ws_List, sig_List, g_] := Module[{neg,pos,soft,hard,n=Length[ws]}, neg=Pick[ws,sig,-1]; pos=Pick[ws,sig,1]; If[neg[[1]]^2<=neg[[2]]^2, soft=neg[[1]]; hard=neg[[2]], soft=neg[[2]]; hard=neg[[1]]]; Simplify[I*2^(n-1)*hard*soft*ClampedPower[soft^2,pos^2]/g^(n-3)]];
cases={
{5,{2,3,5}},{5,{-3,1,12}},{5,{2,-3,10}},{5,{4,1,8}},{5,{8,1,4}},{5,{1/3,2,9}},{5,{2,7,11}},
{6,{2,3,5,7}},{6,{1,4,9,16}},{6,{-3,1,5,20}},{6,{4,1,8,10}},{6,{2,-3,10,11}},
{7,{2,3,5,7,11}},{7,{1,4,9,16,25}},{7,{-3,1,5,20,21}}
};
Do[n=tc[[1]]; free=tc[[2]]; sig=Join[{-1,-1},Table[1,n-2]]; {ks,ws}=MakeKinematics[n,free,sig,1]; bg=Simplify[BGAmplitude[ks,ws,1]]; cf=ClosedA[ws,sig,1]; diff=Simplify[bg-cf]; Print["n=",n," free=",free," ws=",ws," bg=",bg," cf=",cf," diff=",diff],{tc,cases}];
'
```

## Normalized `n=6` chamber data

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; NormG[ws_,sig_,amp_]:=Module[{neg=Pick[ws,sig,-1],pos=Pick[ws,sig,1],soft,hard,n=Length[ws]},If[neg[[1]]^2<=neg[[2]]^2,soft=neg[[1]];hard=neg[[2]],soft=neg[[2]];hard=neg[[1]]];Simplify[amp/(I*2^(n-1)*hard*soft)]];
cases={{2,3,5,7},{1,4,9,16},{-3,1,5,20},{-3,1,12,20},{4,1,8,10},{8,1,4,10},{20,1,4,8},{2,-3,10,11},{-10,1,2,30},{-5,1,2,20}};
Do[n=6;sig=Join[{-1,-1},Table[1,n-2]];{ks,ws}=MakeKinematics[n,fw,sig,1];amp=Simplify[BGAmplitude[ks,ws,1]];neg=Pick[ws,sig,-1];pos=Pick[ws,sig,1];soft=If[neg[[1]]^2<=neg[[2]]^2,neg[[1]],neg[[2]]];xs=Sort[pos^2];r=Count[xs,x_/;x<soft^2];Print["fw=",fw," ws=",ws," soft=",soft," U=",soft^2," xs=",xs," r=",r," G=",NormG[ws,sig,amp]],{fw,cases}]
'
```

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs]; NormG[ws_,sig_,amp_]:=Module[{neg=Pick[ws,sig,-1],pos=Pick[ws,sig,1],soft,hard,n=Length[ws]},If[neg[[1]]^2<=neg[[2]]^2,soft=neg[[1]];hard=neg[[2]],soft=neg[[2]];hard=neg[[1]]];Simplify[amp/(I*2^(n-1)*hard*soft)]]; cases={{8,2,5,10},{10,2,5,12},{-8,2,5,30},{-6,2,4,20},{12,3,5,20},{15,2,7,30}}; Do[n=6;sig=Join[{-1,-1},Table[1,n-2]];{ks,ws}=MakeKinematics[n,fw,sig,1];amp=Simplify[BGAmplitude[ks,ws,1]];neg=Pick[ws,sig,-1];pos=Pick[ws,sig,1];soft=If[neg[[1]]^2<=neg[[2]]^2,neg[[1]],neg[[2]]];xs=Sort[pos^2];r=Count[xs,x_/;x<soft^2];Print["fw=",fw," ws=",ws," U=",soft^2," xs=",xs," r=",r," G=",NormG[ws,sig,amp]],{fw,cases}]'
```

## Final formula verification

This is the final Wolfram verification that produced exact zero differences.
It is also saved, with cleaner file-path handling, as `verify_formula.m`.

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs];
Clear[FiniteG,ClosedA];
FiniteG[U_, xs_List] := Module[{m=Length[xs]-1, below, r}, below=Select[Sort[xs], # < U &]; r=Min[m,Length[below]]; Total[Table[(-1)^Length[S]*(U-Total[S])^m,{S,Subsets[below[[1;;r]]]}]]];
ClosedA[ws_List, sig_List, g_] := Module[{neg,pos,soft,hard,n=Length[ws]}, neg=Pick[ws,sig,-1]; pos=Pick[ws,sig,1]; If[neg[[1]]^2<=neg[[2]]^2, soft=neg[[1]]; hard=neg[[2]], soft=neg[[2]]; hard=neg[[1]]]; Simplify[I*2^(n-1)*hard*soft*FiniteG[soft^2,pos^2]/g^(n-3)]];
cases={
{5,{2,3,5}},{5,{-3,1,12}},{5,{2,-3,10}},{5,{4,1,8}},{5,{8,1,4}},{5,{1/3,2,9}},{5,{2,7,11}},
{6,{2,3,5,7}},{6,{1,4,9,16}},{6,{-3,1,5,20}},{6,{-3,1,12,20}},{6,{4,1,8,10}},{6,{8,1,4,10}},{6,{20,1,4,8}},{6,{2,-3,10,11}},{6,{-10,1,2,30}},{6,{-5,1,2,20}},
{7,{2,3,5,7,11}},{7,{1,4,9,16,25}},{7,{-3,1,5,20,21}}
};
Do[n=tc[[1]]; free=tc[[2]]; sig=Join[{-1,-1},Table[1,n-2]]; {ks,ws}=MakeKinematics[n,free,sig,1]; bg=Simplify[BGAmplitude[ks,ws,1]]; cf=ClosedA[ws,sig,1]; diff=Simplify[bg-cf]; Print["n=",n," free=",free," diff=",diff," bg=",bg],{tc,cases}];
'
```

## `n=4` limiting probe attempted

This attempt failed to start because the OS was already refusing new process
creation with `Out of memory (os error 12)`.

```sh
wolframscript -code '
defs=First@StringSplit[Import["OnShellBG.m","Text"],"(* ================================================================ *)\n(*  VI. TESTS"]; ToExpression[defs];
Clear[eps]; a=2; b=3; ws0={-b,a,b,-a}; ks0={-b^2,-a^2,b^2,a^2}; Print["raw=",BGAmplitude[ks0,ws0,1]];
Do[ws={-b,a,b,-a+e}; ks={-b^2,-a^2,b^2,(-a+e)^2}; amp=N[BGAmplitude[ks,ws,1],30]; Print["e=",e," amp=",amp],{e,{1/10,1/100,1/1000,-1/100,-1/1000}}];
Print["formula=",8 I*(-b)*a*a^2];
'
```

## OOM/process checks

These commands were attempted after the heavy Wolfram runs.  They failed at
process creation with `Out of memory (os error 12)` until the environment
briefly recovered for file patching.

```sh
ps -u "$USER" -o pid,comm,%mem,%cpu --sort=-%mem | head -20
true
find codex_55_xhigh -maxdepth 1 -type f -printf '%f\n' | sort
ps -u "$USER" -o pid,ppid,stat,etime,comm,args | rg 'wolfram|Wolfram|math|verify_formula|OnShellBG|codex_55|wolframscript' || true
ls -la /home/zihanz/waterhedron_benchmark_blind/case_3/codex_55_xhigh
```

