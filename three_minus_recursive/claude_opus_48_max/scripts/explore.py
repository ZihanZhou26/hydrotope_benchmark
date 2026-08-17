"""explore.py — probe three-minus invariants: homogeneity, symmetry, sign, magnitudes."""
import itertools, sys
from fractions import Fraction as Fr
import harness


def three_minus_sigma(n):
    return [-1, -1, -1] + [1] * (n - 3)


def B_onshell(n, free_w, g=1):
    sigma = three_minus_sigma(n)
    r = harness.onshell(n, free_w, sigma, g=g)
    assert r["A_re"] == 0, f"real part nonzero: {r['A_re']}"
    return r["omega"], r["A_im"]


def B_raw_from_omega(omega, sigma, g=1):
    """Compute B for explicit omega (Fractions) with given sigma via raw --amp."""
    K = [Fr(sigma[i]) * Fr(omega[i]) ** 2 / Fr(g) for i in range(len(omega))]
    r = harness.rawamp(K, omega, g=g)
    assert r["A_re"] == 0, f"real part nonzero: {r['A_re']}"
    return r["A_im"]


def show_data(n, free_list, g=1):
    print(f"=== n={n} three-minus data ===")
    for fw in free_list:
        om, B = B_onshell(n, fw, g=g)
        print(f"  omega={[str(x) for x in om]}  B={B}  (~{float(B):.6g})")


def test_homogeneity(n, fw, g=1):
    om, B = B_onshell(n, fw, g=g)
    # scale all free freqs by lambda; recompute via raw on the scaled FULL omega
    for lam in [Fr(2), Fr(3), Fr(1, 2)]:
        om2 = [lam * x for x in om]
        sigma = three_minus_sigma(n)
        B2 = B_raw_from_omega(om2, sigma, g=g)
        ratio = B2 / B if B != 0 else None
        print(f"  n={n} lambda={lam}: B(lam*om)/B = {ratio}  (lam^? )")
        if ratio is not None:
            # find exponent
            for d in range(0, 4 * n):
                if lam ** d == ratio:
                    print(f"      => degree {d}")
                    break


def test_symmetry(n, fw, g=1):
    om, B = B_onshell(n, fw, g=g)
    sigma = three_minus_sigma(n)
    print(f"  base omega={[str(x) for x in om]} B={B}")
    # permute minus legs (indices 0,1,2)
    minus_idx = [0, 1, 2]
    plus_idx = list(range(3, n))
    print("  -- permute minus legs {1,2,3}:")
    for perm in itertools.permutations(minus_idx):
        om2 = list(om)
        for a, b in zip(minus_idx, perm):
            om2[a] = om[b]
        B2 = B_raw_from_omega(om2, sigma, g=g)
        print(f"     perm {perm}: B={B2}  {'=' if B2==B else 'DIFF'}")
    print("  -- permute plus legs:")
    for perm in itertools.permutations(plus_idx):
        om2 = list(om)
        for a, b in zip(plus_idx, perm):
            om2[a] = om[b]
        B2 = B_raw_from_omega(om2, sigma, g=g)
        print(f"     perm {perm}: B={B2}  {'=' if B2==B else 'DIFF'}")


if __name__ == "__main__":
    n5 = [[2, 3, 5], [1, 2, 4], [Fr(7, 2), 4, Fr(9, 5)], [3, 1, 6],
          [5, 2, 3], [4, 7, 2], [10, 1, 2], [1, 1, 3], [2, 2, 5]]
    show_data(5, n5)
    print("\n--- homogeneity n=5 ---")
    test_homogeneity(5, [2, 3, 5])
    print("\n--- symmetry n=5 ---")
    test_symmetry(5, [2, 3, 5])
