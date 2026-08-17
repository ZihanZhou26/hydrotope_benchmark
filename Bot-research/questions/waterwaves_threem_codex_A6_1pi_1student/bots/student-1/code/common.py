from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BG_BIN = ROOT / "bg"

SIG_M = [-1, -1, -1]
SIG_P = [1, 1, 1]
SIG_FULL = [-1, -1, -1, 1, 1, 1]


# ---------- generic utilities ----------


def parse_fraction(text):
    text = str(text).strip()
    if text == "" or text.lower() == "nan":
        raise ValueError("empty fraction")
    return Fraction(text)


def frac_to_str(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else "%s/%s" % (x.numerator, x.denominator)


def iter_subsets(n, min_size=1, max_size=None):
    if max_size is None:
        max_size = n
    out = []
    for r in range(min_size, max_size + 1):
        for idxs in combinations(range(n), r):
            out.append(bits_to_mask(idxs))
    return out


def subset_bits(mask):
    out = []
    p = 0
    while mask:
        if mask & 1:
            out.append(p)
        mask >>= 1
        p += 1
    return out


def bits_to_mask(idxs):
    m = 0
    for i in idxs:
        m |= 1 << i
    return m


def solve_from_free(omega2_omega5, signs):
    if len(omega2_omega5) + 2 != len(signs):
        raise ValueError("sign vector length must be free count + 2")
    if len(omega2_omega5) + 2 < 3:
        raise ValueError("invalid kinematics")

    free = [Fraction(w) for w in omega2_omega5]
    s = sum(free)
    if s == 0:
        raise ZeroDivisionError("sum free frequencies is zero")
    sum_sig = sum(signs[i + 1] * free[i] ** 2 for i in range(len(free)))
    sig0 = Fraction(signs[0])
    wn = -(sig0 * s * s + sum_sig) / (2 * sig0 * s)
    w1 = -(s + wn)
    return (w1, *free, wn)


def momenta_from_omega(omega, signs, g=Fraction(1)):
    return [Fraction(signs[i]) * omega[i] * omega[i] / g for i in range(len(omega))]


# ---------- wall helpers ----------


def wall_key(mask_m, mask_p):
    return "I%02d_J%02d" % (mask_m, mask_p)


def wall_masks_to_expr_diff(mask_m, mask_p):
    terms = []
    for i in subset_bits(mask_m):
        terms.append("a%d" % (i + 1))
    for j in subset_bits(mask_p):
        terms.append("-a%d" % (3 + j + 1))
    if not terms:
        return "0"
    return " + ".join(terms)


def wall_masks_to_expr_sum(mask_m, j_anchor):
    terms = ["a%d" % (i + 1) for i in subset_bits(mask_m)]
    terms.append("a%d" % (3 + j_anchor + 1))
    return "(%s) - T" % (" + ".join(terms))


def _build_diff_walls():
    out = []
    for i in range(3):
        for j in range(3):
            i_mask = 1 << i
            j_mask = 1 << j
            out.append(
                {
                    "kind": "diff",
                    "id": "I%02d_J%02d" % (i_mask, j_mask),
                    "I_mask": i_mask,
                    "J_mask": j_mask,
                    "plus_anchor": j,
                    "q_expression": wall_masks_to_expr_diff(i_mask, j_mask),
                    "subset_sizes": [1, 1],
                    "subset_size_orbit": [1, 1],
                }
            )
    return out


def _build_sum_walls():
    full = 0b111
    out = []
    for i in range(3):
        i_mask = 1 << i
        for j in range(3):
            j_mask = full ^ (1 << j)
            out.append(
                {
                    "kind": "sum",
                    "id": "S_%02d_%02d" % (i_mask, j_mask),
                    "I_mask": i_mask,
                    "J_mask": j_mask,
                    "plus_anchor": j,
                    "q_expression": wall_masks_to_expr_sum(i_mask, j),
                    "subset_sizes": [1, 2],
                    "subset_size_orbit": [1, 2],
                }
            )
    return out


def _build_external_walls():
    out = []
    full = 0b111

    for i in range(3):
        i_mask = 1 << i
        out.append(
            {
                "kind": "boundary",
                "id": "EB_M%02d_P%02d" % (i_mask, full),
                "I_mask": i_mask,
                "J_mask": full,
                "plus_anchor": 0,
                "q_expression": wall_masks_to_expr_diff(i_mask, full),
                "subset_sizes": [1, 3],
                "subset_size_orbit": [1, 3],
            }
        )

    for j in range(3):
        j_mask = 1 << j
        out.append(
            {
                "kind": "boundary",
                "id": "EB_M%02d_P%02d" % (full, j_mask),
                "I_mask": full,
                "J_mask": j_mask,
                "plus_anchor": j,
                "q_expression": wall_masks_to_expr_diff(full, j_mask),
                "subset_sizes": [3, 1],
                "subset_size_orbit": [3, 1],
            }
        )

    return out


def build_wall_catalog():
    nondeg = sorted(_build_diff_walls() + _build_sum_walls(), key=lambda d: d["id"])
    dedup = []
    seen = set()
    for item in nondeg:
        key = item["id"]
        if key in seen:
            continue
        seen.add(key)
        dedup.append(item)
    return dedup


def build_external_wall_catalog():
    return sorted(_build_external_walls(), key=lambda d: d["id"])


def wall_value(a, wall):
    a = [Fraction(x) for x in a]
    I_mask = int(wall.get("I_mask"))
    J_mask = int(wall.get("J_mask"))
    kind = str(wall.get("kind", "diff"))

    sI = sum(a[i] for i in subset_bits(I_mask))
    if kind in ("diff", "boundary"):
        sJ = sum(a[3 + j] for j in subset_bits(J_mask))
        return sI - sJ

    if kind == "sum":
        # external formula: omega_i^2 + omega_{3+j}^2 - (sum of minus squares)
        j = int(wall.get("plus_anchor", 0))
        sM = a[0] + a[1] + a[2]
        return sI + a[3 + j] - sM

    raise ValueError("unknown wall kind")


def wall_sign_map(omega, wall_catalog):
    a = [Fraction(w) * Fraction(w) for w in omega]
    out = {}
    for item in wall_catalog:
        v = wall_value(a, item)
        out[str(item["id"])] = 1 if v > 0 else -1 if v < 0 else 0
    return out


def serialize_signs(sign_map, wall_catalog):
    return "|".join("%s:%s" % (item["id"], sign_map[str(item["id"])]) for item in wall_catalog)


def sort_partition_idx(omega, idxs):
    return sorted(list(idxs), key=lambda i: (omega[i] * omega[i], omega[i]))


def local_omega_from_perm(omega, minus_idx, plus_idx, perm_m, perm_p, swap):
    if swap:
        return tuple(omega[plus_idx[perm_m[i]]] for i in range(3)) + tuple(
            omega[minus_idx[perm_p[i]]] for i in range(3)
        )
    return tuple(omega[minus_idx[perm_m[i]]] for i in range(3)) + tuple(
        omega[plus_idx[perm_p[i]]] for i in range(3)
    )


def canonicalize_wall_signatures(omega, wall_catalog, minus_idx, plus_idx, allow_swap=True):
    perms = [tuple(p) for p in permutations(range(3))]
    swaps = (False, True) if allow_swap else (False,)
    full = list(omega)
    best = None

    for do_swap in swaps:
        for perm_m in perms:
            for perm_p in perms:
                local = local_omega_from_perm(full, minus_idx, plus_idx, perm_m, perm_p, do_swap)
                s = wall_sign_map(local, wall_catalog)
                key = serialize_signs(s, wall_catalog)
                if best is None or key < best[0]:
                    best = (key, s)

    if best is None:
        raise RuntimeError("cannot canonicalize wall signatures")
    return best[1], best[0]


def internal_subset_bits(n=6):
    out = []
    for r in (2, 3, 4):
        out.extend(iter_subsets(n, r, r))
    return out


def q_T_for_mask(omega, mask, signs):
    q = Fraction(0)
    for i in range(len(omega)):
        if (mask >> i) & 1:
            q += signs[i] * omega[i] * omega[i]
    return q


def h_T(omega, mask, signs):
    q = q_T_for_mask(omega, mask, signs)
    wsum = sum(omega[i] for i in range(len(omega)) if (mask >> i) & 1)
    h = wsum * wsum - abs(q)
    return h, q
