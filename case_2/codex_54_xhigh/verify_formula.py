from __future__ import print_function

import importlib.util
from fractions import Fraction


SPEC = importlib.util.spec_from_file_location(
    "abg",
    "/home/zihanz/waterhedron_benchmark_blind/case_2/codex_54_xhigh/analyze_bg.py",
)
ABG = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ABG)


def subset_data(arr):
    n = len(arr)
    for mask in range(1 << n):
        total = Fraction(0, 1)
        items = []
        bits = 0
        for i in range(n):
            if (mask >> i) & 1:
                total += arr[i]
                items.append(i + 3)
                bits += 1
        yield tuple(items), bits, total


def truncated_power_spline(x, arr):
    degree = len(arr)
    out = Fraction(0, 1)
    for _, bits, total in subset_data(arr):
        diff = x - total
        if diff > 0:
            out += ((-1) ** bits) * (diff ** degree)
    return out


def active_subsets(ws):
    x = ws[1] * ws[1]
    arr = [w * w for w in ws[2:-1]]
    out = []
    for items, _, total in subset_data(arr):
        if x - total > 0:
            out.append(items)
    return out


def formula_coeff(ws):
    n = len(ws)
    x = ws[1] * ws[1]
    arr = [w * w for w in ws[2:-1]]
    return Fraction(2 ** (n - 1), 1) * ws[0] * ws[1] * truncated_power_spline(x, arr)


def rel_error(a, b):
    af = float(a)
    bf = float(b)
    if bf == 0.0:
        return abs(af - bf)
    return abs(af - bf) / abs(bf)


def exact_checks():
    samples = {
        5: [
            [2, 3, 4],
            [5, 2, 3],
            [2, 1, 3],
            [4, 3, 3],
            [3, 5, 7],
        ],
        6: [
            [2, 3, 4, 5],
            [2, 1, 3, 5],
            [4, 3, 3, 5],
            [3, 5, 7, 11],
            [2, 4, 7, 9],
        ],
        7: [
            [2, 3, 4, 5, 6],
            [6, 2, 3, 4, 5],
            [2, 1, 3, 5, 8],
            [3, 5, 7, 11, 13],
            [2, 4, 7, 9, 10],
        ],
    }

    print("Exact On-Shell Checks")
    print("=====================")
    for n in sorted(samples):
        print("")
        print("n = {0}".format(n))
        for fw in samples[n]:
            ws = ABG.make_kinematics(fw)[1]
            bg = ABG.amplitude_coeff_from_free(fw)
            guess = formula_coeff(ws)
            print("  freeW   = {0}".format(fw))
            print("  ws      = {0}".format(ws))
            print("  active  = {0}".format(active_subsets(ws)))
            print("  BG      = {0}".format(bg))
            print("  formula = {0}".format(guess))
            print("  relerr  = {0:.3e}".format(rel_error(bg, guess)))
            print("")


def four_point_limit_checks():
    print("")
    print("Four-Point Limiting Checks")
    print("==========================")

    cases = [
        {
            "name": "omega2^2 < omega3^2",
            "target_ws": [Fraction(-3, 1), Fraction(1, 1), Fraction(3, 1), Fraction(-1, 1)],
            "delta_den": 10 ** 5,
            "perturbed_ws": lambda d: [
                Fraction(-3, 1) - Fraction(1, d),
                Fraction(1, 1),
                Fraction(3, 1),
                Fraction(-1, 1) + Fraction(1, d),
            ],
        },
        {
            "name": "omega2^2 > omega3^2",
            "target_ws": [Fraction(-1, 1), Fraction(3, 1), Fraction(1, 1), Fraction(-3, 1)],
            "delta_den": 10 ** 11,
            "perturbed_ws": lambda d: [
                Fraction(-1, 1) - Fraction(1, d),
                Fraction(3, 1),
                Fraction(1, 1),
                Fraction(-3, 1) + Fraction(1, d),
            ],
        },
    ]

    for case in cases:
        d = case["delta_den"]
        target_ws = case["target_ws"]
        guess = formula_coeff(target_ws)
        ws = case["perturbed_ws"](d)
        ks = [-ws[0] * ws[0], -ws[1] * ws[1], ws[2] * ws[2], ws[3] * ws[3]]
        bg = ABG.BG(tuple(ks), tuple(ws), Fraction(1, 1)).amplitude_coeff()
        print("  case    = {0}".format(case["name"]))
        print("  target  = {0}".format(target_ws))
        print("  delta   = 1/{0}".format(d))
        print("  BG      = {0}".format(bg))
        print("  formula = {0}".format(guess))
        print("  relerr  = {0:.3e}".format(rel_error(bg, guess)))
        print("")


def main():
    exact_checks()
    four_point_limit_checks()


if __name__ == "__main__":
    main()
