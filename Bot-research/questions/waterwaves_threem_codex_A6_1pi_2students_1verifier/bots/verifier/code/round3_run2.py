#!/usr/bin/env python3
"""Re-run V3 (compact four-leg brick) and V4 (spline exchange) with the
continuity-enforced (adjacency-guaranteed) extractor."""
import sys, os
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from round3_verify import reconstruct_H24, compact_same_energy_H, P_s1

print("="*70); print("V3  compact same-energy H24, four-leg beta (adjacency-enforced)")
print("-"*70)
envs = [("A minus-min",F(10),F(2),F(3)),("B plus-min ",F(10),F(4),F(1)),
        ("C plus-min ",F(12),F(5),F(1)),("D minus-min",F(14),F(2),F(5)),
        ("E plus-min ",F(16),F(6),F(1)),
        ("F plus-min ",F(18),F(7),F(1)),("G plus-min ",F(9),F(4),F(1))]
allok=True
for name,B,c,e in envs:
    r=reconstruct_H24(B,c,e)
    w=r.get('wall_omega')
    if w is None:
        print(f"[{name}] reconstruction failed"); allok=False; continue
    Hbg=r['H24']; Hf=compact_same_energy_H(w,1,3,'four'); Hm=compact_same_energy_H(w,1,3,'minus')
    mags={0:abs(w[0]),2:abs(w[2]),4:abs(w[4]),5:abs(w[5])}
    lbl={0:'w1(minus)',2:'w3(minus)',4:'w5(plus)',5:'w6(plus)'}[min(mags,key=lambda i:mags[i])]
    ok=(Hbg==Hf); allok=allok and ok
    print(f"[{name}] beta={lbl} step={r['step']} cont={r['continuity']} H_BG={Hbg}")
    print(f"    four-leg={Hf} match={ok} | minus-only match={Hbg==Hm} (differ:{Hf!=Hm})")
print("V3:", "PASS all envs" if allok else "MISMATCH remains")

print(); print("="*70); print("V4  spline exchange P(u)->P(6-u) (adjacency-enforced)")
print("-"*70)
tests=[("left",F(7,6)),("left",F(2)),("left",F(4)),
       ("right",F(11,2)),("right",F(13,2)),("right",F(7)),("right",F(9)),("right",F(10))]
v4=True
for side,u in tests:
    r=reconstruct_H24(F(10),u,F(6)-u)
    w=r.get('wall_omega')
    if w is None:
        print(f"u={u}: reconstruction failed"); v4=False; continue
    Hbg=r['H24']; Pu=P_s1(u); P6=P_s1(F(6)-u); Hf=compact_same_energy_H(w,1,3,'four')
    m='P(u)' if Hbg==Pu else ('P(6-u)' if Hbg==P6 else 'NEITHER')
    exp=Pu if side=='left' else P6
    ok=(Hbg==exp and Hbg==Hf); v4=v4 and ok
    print(f"u={str(u):>5}[{side:>5}] step={r['step']} H_BG={Hbg} -> {m}; formula_match={Hbg==Hf} exp_match={Hbg==exp}")
print("V4:", "PASS" if v4 else "CHECK")
