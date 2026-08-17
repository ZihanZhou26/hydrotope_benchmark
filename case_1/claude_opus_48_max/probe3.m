Get["/home/zihanz/waterhedron_benchmark_blind/case_1/claude_opus_48_max/bg_core.m"];

(* Symbolic A5, two-minus. Free freqs {a,b,c} = {w2,w3,w4}; solve w1,w5.
   Resolve each Abs[arg] by the sign of arg at a numeric reference point
   (valid throughout that sign-chamber), then Factor.  Compare chambers. *)

sig = {-1, -1, 1, 1, 1};
{ks, ws} = MakeKinematics[5, {a, b, c}, sig, 1];
Print["ws = ", ws];

rawAmp = BGAmplitude[ks, ws, 1];
Print["raw amp leafcount = ", LeafCount[rawAmp]];

(* function: resolve Abs using numeric sign at reference point refpt *)
resolveAbs[expr_, refpt_] := expr //. Abs[x_] :> Sign[N[x /. refpt]] x;

chamberRational[refpt_] := Module[{r},
  r = resolveAbs[rawAmp, refpt];
  r = Together[r];
  r];

(* Chamber A: a<b<c all positive *)
ptA = {a -> 2, b -> 3, c -> 5};
ratA = chamberRational[ptA];
Print["=== Chamber A (a=2,b=3,c=5) ==="];
Print["  contains Abs? ", ! FreeQ[ratA, Abs]];
numA = Numerator[ratA]; denA = Denominator[ratA];
Print["  numerator FactorList:"]; Print[FactorList[numA]];
Print["  denominator FactorList:"]; Print[FactorList[denA]];

(* Chamber B: different ordering c<a<b but still all positive *)
ptB = {a -> 7, b -> 11, c -> 2};
ratB = chamberRational[ptB];
Print["=== Chamber B (a=7,b=11,c=2) ==="];
Print["  contains Abs? ", ! FreeQ[ratB, Abs]];

(* Chamber C: mixed signs, a>0,b>0,c<0 *)
ptC = {a -> 3, b -> 5, c -> -2};
ratC = chamberRational[ptC];
Print["=== Chamber C (a=3,b=5,c=-2) ==="];

Print["=== Compare chambers (Simplify of differences) ==="];
Print["  ratA - ratB simplifies to 0 ? ", Simplify[ratA - ratB] === 0];
Print["  ratA - ratC simplifies to 0 ? ", Simplify[ratA - ratC] === 0];

Print["=== ratA fully factored ==="];
Print[Factor[ratA]];
