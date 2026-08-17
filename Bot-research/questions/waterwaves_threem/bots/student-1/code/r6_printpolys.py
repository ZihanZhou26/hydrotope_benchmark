#!/usr/bin/env python3
"""Print the explicit coefficient polynomials B, P0, R0 fully (and factored) to stdout
and to r6_polys.txt for the writeup."""
import pickle, sympy as sp
d=pickle.load(open("r6_polys.pkl","rb"))
B,P0,R0=d['B'],d['P0'],d['R0']
out=[]
out.append("=== B (base; e1=e1plus=-e1minus, e2=e2plus=e2minus, e3m=w1w2w3, e3p=w4w5w6) ===")
out.append("expanded:"); out.append(str(sp.expand(B)))
out.append("factored:"); out.append(str(sp.factor(B)))
out.append("")
out.append("=== P0 (single-(1=1) coeff; reference wall {a1=b4};")
out.append("    x=w1, y=w4, A1=w2+w3, A2=w2*w3, B1=w5+w6, B2=w5*w6) ===")
out.append("expanded:"); out.append(str(sp.expand(P0)))
out.append("factored:"); out.append(str(sp.factor(P0)))
out.append("")
out.append("=== R0 (pair-(1=1) coeff; reference pair walls {a1=b4} & {a2=b5},")
out.append("    leftover legs minus-3, plus-6; raw vars w1..w6) ===")
out.append("expanded:"); out.append(str(sp.expand(R0)))
out.append("factored:"); out.append(str(sp.factor(R0)))
txt="\n".join(out)
open("r6_polys.txt","w").write(txt)
print(txt)
