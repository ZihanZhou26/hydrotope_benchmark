import subprocess
from fractions import Fraction
from itertools import combinations

import common


def solve_n5_from_free(free, signs):
    return common.solve_from_free(free, signs)


def two_minus_formula_n5(omega):
    omega = [Fraction(w) for w in omega]
    if len(omega) != 5:
        raise ValueError("require five frequencies")
    beta = min(abs(omega[0]), abs(omega[1]))
    a = [w * w for w in omega[2:]]
    b = Fraction(0)
    for r in range(len(a) + 1):
        for idxs in combinations(range(len(a)), r):
            x = sum(a[i] for i in idxs)
            term = beta * beta - x
            if term > 0:
                b += Fraction((-1) ** r) * term * term
    return Fraction(16) * omega[0] * omega[1] * b


def bg_two_minus(omega, signs):
    s = ",".join(common.frac_to_str(x) for x in omega[1:-1])
    cmd = [str(common.BG_BIN), "-n", "5", "-w", s, "-s", ",".join(map(str, signs)), "-g", "1"]
    proc = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    txt = proc.stdout
    import re

    m = re.search(r"A_5\s*=\s*\(\s*([^)]*?)\s*\)\s*\+\s*i\s*\(\s*([^)]*?)\s*\)", txt)
    if m:
        return common.parse_fraction(m.group(2))
    m = re.search(r"A_5\s*=\s*i\s*\*?\s*\(?\s*([^)\\n]*)\s*\)?", txt)
    if m:
        return common.parse_fraction(m.group(1))
    raise ValueError("failed parse A_5")


def fmt_line(tag, omega, val_formula, val_bg):
    status = "OK" if val_formula == val_bg else "DIFF"
    return (
        f"{tag} omega={list(map(common.frac_to_str, omega))} "
        f"formula={common.frac_to_str(val_formula)} bg={common.frac_to_str(val_bg)} {status}"
    )


def main():
    lines = []
    two_minus_signs = [-1, -1, 1, 1, 1]
    signflip_signs = [1, 1, -1, -1, -1]
    free_points_two_minus = [
        [Fraction(2, 1), Fraction(3, 1), Fraction(1, 1)],
        [Fraction(5, 2), Fraction(-1, 1), Fraction(4, 1)],
        [Fraction(-3, 2), Fraction(2, 1), Fraction(7, 2)],
        [Fraction(1, 3), Fraction(5, 3), Fraction(2, 5)],
    ]
    lines.append("=== two-minus calibration (n=5) ===")
    for idx, free in enumerate(free_points_two_minus[:2]):
        omega = solve_n5_from_free(free, two_minus_signs)
        bg_im = bg_two_minus(omega, two_minus_signs)
        formula_im = two_minus_formula_n5(omega)
        lines.append(fmt_line(f"two-minus #{idx}", omega, formula_im, bg_im))

    lines.append("=== sign-flipped two-minus / three-minus invariance check (n=5) ===")
    for idx, free in enumerate(free_points_two_minus):
        omega = solve_n5_from_free(free, signflip_signs)
        s = ",".join(common.frac_to_str(x) for x in omega[1:-1])
        cmd1 = [str(common.BG_BIN), "-n", "5", "-w", s, "-s", ",".join(map(str, two_minus_signs)), "-g", "1"]
        cmd2 = [str(common.BG_BIN), "-n", "5", "-w", s, "-s", ",".join(map(str, signflip_signs)), "-g", "1"]
        p1 = subprocess.run(
            cmd1, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        p2 = subprocess.run(
            cmd2, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
        )
        import re

        m1 = re.search(r"A_5\s*=\s*\(\s*([^)]*?)\s*\)\s*\+\s*i\s*\(\s*([^)]*?)\s*\)", p1.stdout)
        if not m1:
            m1 = re.search(r"A_5\s*=\s*i\s*\*?\s*\(?\s*([^)\\n]*)\s*\)?", p1.stdout)
            a1 = common.parse_fraction(m1.group(1)) if m1 else None
        else:
            a1 = common.parse_fraction(m1.group(2))
        m2 = re.search(r"A_5\s*=\s*\(\s*([^)]*?)\s*\)\s*\+\s*i\s*\(\s*([^)]*?)\s*\)", p2.stdout)
        if not m2:
            m2 = re.search(r"A_5\s*=\s*i\s*\*?\s*\(?\s*([^)\\n]*)\s*\)?", p2.stdout)
            a2 = common.parse_fraction(m2.group(1)) if m2 else None
        else:
            a2 = common.parse_fraction(m2.group(2))
        if a1 is None or a2 is None:
            lines.append(f"three-minus-invariance #{idx}: parse failed")
            continue
        status = "OK" if a1 == a2 else "DIFF"
        lines.append(
            f"three-minus #{idx} omega={list(map(common.frac_to_str, omega))} "
            f"A_-(two-minus-ref)={common.frac_to_str(a1)} A_+(flipped)={common.frac_to_str(a2)} {status}"
        )

    lines.append("=== direct run check (A_5 exact) ===")
    for idx, free in enumerate(free_points_two_minus):
        omega = solve_n5_from_free(free, signflip_signs)
        a2 = bg_two_minus(omega, signflip_signs)
        formula = two_minus_formula_n5(omega) if idx < 2 else None
        if formula is None:
            lines.append(f"bg run #{idx} omega={list(map(common.frac_to_str, omega))} A_5={common.frac_to_str(a2)}")
        else:
            lines.append(fmt_line(f"bg check #{idx}", omega, formula, a2))
    return "\n".join(lines)


if __name__ == "__main__":
    print(main())
