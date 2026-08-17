"""
(1) Validate bg_float vs exact anchors.
(2) DECISIVE TEST: fix the minus pair (w1,w2) [=> fix e1,e2], vary the plus
    configuration (changing P3,P4,...), and see if a_5 changes.
"""
import mpmath as mp
from bg_float import amp_from_allW

mp.mp.dps = 60
sig5 = [-1, -1, 1, 1, 1]

print("=== validate bg_float vs exact ===")
# {1,2,3}: allW=[-4,1,2,3,-2], exact A=-64 i
A = amp_from_allW([-4, 1, 2, 3, -2], sig5)
print(f"  {{1,2,3}}: A={mp.nstr(A,15)}  (exact -64 i)  re~{mp.nstr(A.real,5)}")
# {2,5/2,3}: allW=[-9/2,2,5/2,3,-3], exact A=-2304 i
A = amp_from_allW([-4.5, 2, 2.5, 3, -3], sig5)
print(f"  {{2,5/2,3}}: A={mp.nstr(A,15)}  (exact -2304 i)")


def plus_config(w1, w2, z):
    """plus legs (x,y,z) with x+y+z=-(w1+w2), x^2+y^2+z^2=w1^2+w2^2."""
    A = -(w1 + w2)
    B = w1 ** 2 + w2 ** 2
    s = A - z          # x+y
    p = ((A - z) ** 2 - (B - z ** 2)) / 2   # xy
    disc = s ** 2 - 4 * p
    if disc < 0:
        return None
    r = mp.sqrt(disc)
    x = (s + r) / 2
    y = (s - r) / 2
    return x, y, z


print("\n=== P3-independence: minus=(-4,1), vary plus config (vary z) ===")
w1, w2 = mp.mpf(-4), mp.mpf(1)
e1 = w1 + w2
e2 = w1 * w2
print(f"  fixed e1={e1}, e2={e2}")
vals = []
for z in [mp.mpf('0.7'), mp.mpf('1.3'), mp.mpf('2.1'), mp.mpf('2.7'), mp.mpf('-1.1')]:
    pc = plus_config(w1, w2, z)
    if pc is None:
        print(f"  z={z}: disc<0 skip")
        continue
    x, y, z = pc
    allW = [w1, w2, x, y, z]
    P3 = sum(w ** 3 for w in [x, y, z])
    P4 = sum(w ** 4 for w in [x, y, z])
    try:
        A = amp_from_allW(allW, sig5)
        vals.append(A.imag)
        print(f"  z={mp.nstr(z,4)}: plus=({mp.nstr(x,5)},{mp.nstr(y,5)},{mp.nstr(z,4)}) "
              f"P3={mp.nstr(P3,6)} P4={mp.nstr(P4,6)}  a_5={mp.nstr(A.imag,15)}  re={mp.nstr(A.real,3)}")
    except Exception as e:
        print(f"  z={z}: error {e}")

if len(vals) >= 2:
    spread = max(vals) - min(vals)
    print(f"\n  spread of a_5 across plus configs: {mp.nstr(spread, 5)}")
    print("  => a_5 " + ("INDEPENDENT of plus distribution (depends only on e1,e2)"
                         if abs(spread) < mp.mpf('1e-40') else
                         "DEPENDS on plus distribution (P3,...)"))
