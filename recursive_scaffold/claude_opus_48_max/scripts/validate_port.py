"""Validate the Python BG port against the wolframscript oracle anchor values."""
from fractions import Fraction as F
from bg import amp_two_minus, DegenerateKinematics

# (n, freeW, expected A_n as (re,im)); None expected = degenerate/indeterminate
anchors = [
    (4, [F(2), F(3)], None),
    (4, [F(1), F(3)], None),
    (4, [F(3), F(5)], None),
    (5, [F(2), F(5, 2), F(3)], (0, F(-2304))),
    (5, [F(1), F(2), F(3)], (0, F(-64))),
    (6, [F(3, 2), F(2), F(5, 2), F(3)], (0, F(-11907, 4))),
]

allok = True
for n, fw, exp in anchors:
    try:
        A, allW, allK = amp_two_minus(n, fw)
        got = (A.re, A.im)
        if exp is None:
            print(f"n={n} freeW={fw}: port gave {got} but oracle was INDETERMINATE -- MISMATCH")
            allok = False
        else:
            ok = (A.re == F(exp[0]) and A.im == F(exp[1]))
            allok = allok and ok
            print(f"n={n} freeW={fw}: A={A.re}{'+' if A.im>=0 else ''}{A.im} i  expected i*{exp[1]}  {'OK' if ok else 'MISMATCH'}")
    except (DegenerateKinematics, ZeroDivisionError) as e:
        if exp is None:
            print(f"n={n} freeW={fw}: DEGENERATE as expected ({e})  OK")
        else:
            print(f"n={n} freeW={fw}: unexpectedly DEGENERATE ({e})  MISMATCH")
            allok = False

print("\nALL ANCHORS MATCH" if allok else "\nSOME MISMATCH")
