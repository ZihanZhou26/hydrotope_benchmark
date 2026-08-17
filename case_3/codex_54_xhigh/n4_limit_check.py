import sympy as sp

from analysis import BGEngine


def regularized_a4(a, x, delta):
    ws = (-x, a, x, -a)
    # Move the external momenta slightly off the exact singular point.
    ks = (-x**2 - delta, -a**2 - 2 * delta, x**2 + 3 * delta, a**2 + 5 * delta)
    return BGEngine(ks, ws, 1).amplitude()


def candidate_a4(a, x):
    ws = (-x, a, x, -a)
    return 8 * sp.I * ws[0] * ws[1] ** 3


def main():
    cases = [(sp.Integer(2), sp.Integer(3)), (sp.Rational(3, 2), sp.Integer(5))]
    deltas = [sp.Rational(1, 10**5), sp.Rational(1, 10**6), sp.Rational(1, 10**7)]

    for a, x in cases:
        cand = sp.N(candidate_a4(a, x) / sp.I, 30)
        print("a =", a, "x =", x, "candidate/I =", cand)
        for delta in deltas:
            amp = sp.N(regularized_a4(a, x, delta) / sp.I, 30)
            rel = sp.N(abs((amp - cand) / cand), 20)
            print("  delta =", delta, "amp/I =", amp, "relative error =", rel)
        print("")


if __name__ == "__main__":
    main()
