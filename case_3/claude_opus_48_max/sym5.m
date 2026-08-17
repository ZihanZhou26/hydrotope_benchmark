<< bg_core.m
(* symbolic free freqs a,b,c = w2,w3,w4 ; reference point (2,3,5) sets signs *)
ref = {a->2, b->3, c->5};
(* override mag to resolve Abs by sign at reference point, keeping symbolic *)
Unprotect[mag]; ClearAll[mag];
mag[x_] := x * Sign[x /. ref];

g = 1;
sig = {-1,-1,1,1,1};
fw = {a, b, c};
{ks, ws} = MakeKinematics[5, fw, sig, g];
ws = Simplify[ws];
Print["ws = ", ws];
Print["ks = ", Simplify[ks]];
amp = BGAmplitude[ks, ws, g];
amp = Together[Simplify[amp]];
Print["A5 (raw) = ", amp];
Print["----"];
A5 = Simplify[amp/(-I)];   (* A5 = -I * R, so R = amp/(-I) *)
Print["R5 = A5/(-I) = ", A5];
Print["----factored----"];
Print["Numerator   = ", Factor[Numerator[A5]]];
Print["Denominator = ", Factor[Denominator[A5]]];
(* sanity: numeric check at ref *)
Print["check at (2,3,5): R5 = ", A5 /. ref, "  (expect 3328)"];
