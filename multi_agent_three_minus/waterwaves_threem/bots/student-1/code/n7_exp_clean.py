#!/usr/bin/env python3
"""Clean n=7 (1=3) exponent + multi-chamber confirmation, using n7lib.signature
(42 deduped walls -> sd=1 means clean single-wall). Reuses n7_walls.measure."""
from fractions import Fraction as F
import n7_walls as W

# (1=3) a_2=b_4+b_5+b_6: cross by varying TWO plus legs IN the wall (more chamber room).
# w4^2+w5^2+w6^2 = w2^2 at t=0; vary w4=A+t, w6=B-t (both in wall, keeps sumFree).
print("=== (1=3) a2=b4+b5+b6 : vary w4,w6 (both in the wall) ===")
# w2=7 -> 49 ; w4=6,w5=2,w6=3 -> 36+4+9=49
W.measure("(1=3) #1", [F(7), F(11,2), F(6), F(2), F(3)], 2, 4, F(6), F(3), step=F(1,90), maxn=46)
# w2=9 -> 81; w4=8,w5=1,w6=4 -> 64+1+16=81
W.measure("(1=3) #2", [F(9), F(13,2), F(8), F(1), F(4)], 2, 4, F(8), F(4), step=F(1,90), maxn=46)
# w2=13 ->169; w4=12,w5=3,w6=4 ->144+9+16=169
W.measure("(1=3) #3", [F(13), F(15,2), F(12), F(3), F(4)], 2, 4, F(12), F(4), step=F(1,120), maxn=46)

print("\n=== (1=2) a2=b4+b5 : multi-chamber (check local exponent stability) ===")
# vary w4 in wall, compensate w6 (plus, not in wall)
W.measure("(1=2) #1", [F(5), F(11,3), F(3), F(4), F(15,2)], 2, 4, F(3), F(15,2), step=F(1,90), maxn=46)
# w2=13 ->169; w4=5,w5=12 ->25+144=169 ; vary w4, comp w6
W.measure("(1=2) #2", [F(13), F(7,2), F(5), F(12), F(9)], 2, 4, F(5), F(9), step=F(1,120), maxn=46)
# w2=10 ->100; w4=6,w5=8 ->36+64=100; vary w4, comp w6
W.measure("(1=2) #3", [F(10), F(9,2), F(6), F(8), F(11,2)], 2, 4, F(6), F(11,2), step=F(1,120), maxn=46)

print("\n=== (1=1) a2=b4 : multi-chamber ===")
W.measure("(1=1) #1", [F(3), F(5), F(3), F(8), F(11,2)], 2, 3, F(3), F(8), step=F(1,90), maxn=46)
W.measure("(1=1) #2", [F(4), F(7), F(4), F(19,2), F(13,2)], 2, 3, F(4), F(19,2), step=F(1,90), maxn=46)
