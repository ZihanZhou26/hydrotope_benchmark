import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path

import common
from common import (
    BG_BIN,
    SIG_FULL,
    frac_to_str,
    parse_fraction,
    canonicalize_wall_signatures,
    wall_sign_map,
)


def _as_fraction(x):
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x)
    return parse_fraction(str(x))


def run_bg_exact(omega, g="1", use_double=False):
    cmd = [str(BG_BIN), "--amp"]
    if use_double:
        cmd.append("--double")
    cmd.extend(
        [
            "-K",
            ",".join(
                frac_to_str(_as_fraction(SIG_FULL[i]) * _as_fraction(omega[i]) * _as_fraction(omega[i]) / _as_fraction(g))
                for i in range(6)
            ),
        ]
    )
    cmd.extend(["-W", ",".join(frac_to_str(_as_fraction(w)) for w in omega)])
    cmd.append("-g")
    cmd.append(str(g))
    proc = subprocess.run(
        cmd,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"bg failed: {proc.stderr.strip() or proc.stdout.strip()}")
    text = proc.stdout
    m = re.search(r"A_6\s*=\s*\(\s*([^)]*?)\s*\)\s*\+\s*i\s*\(\s*([^)]*?)\s*\)", text)
    if m:
        re_part = m.group(1).strip()
        im_part = m.group(2).strip()
        return _as_fraction(re_part), _as_fraction(im_part)
    m = re.search(r"A_6\s*=\s*i\s*\*?\s*\(?\s*([^)\n]+)\s*\)?", text)
    if m:
        return Fraction(0), _as_fraction(m.group(1))
    raise ValueError(f"unable to parse bg output: {text}")


class OracleResult(object):
    def __init__(
        self,
        sample_id,
        omega,
        A_re,
        A_im,
        wall_signs,
        wall_signature,
        wall_signature_swap,
        raw_wall_signature,
        min_abs_pole_num,
    ):
        self.sample_id = sample_id
        self.omega = omega
        self.A_re = A_re
        self.A_im = A_im
        self.wall_signs = wall_signs
        self.wall_signature = wall_signature
        self.wall_signature_swap = wall_signature_swap
        self.raw_wall_signature = raw_wall_signature
        self.min_abs_pole_numerator = min_abs_pole_num


def _validate_kinematics_exact(omega):
    if any(w == 0 for w in omega):
        return False, "zero frequency"
    if sum(omega) != 0:
        return False, "sum_omega_nonzero"
    if sum(SIG_FULL[i] * omega[i] * omega[i] for i in range(6)) != 0:
        return False, "kinematic_on_shell_failed"
    return True, ""


def min_abs_pole_numerator(omega):
    vals = []
    for mask in common.internal_subset_bits(6):
        h, _ = common.h_T(omega, mask, SIG_FULL)
        if h == 0:
            return 0
        vals.append(abs(h.numerator))
    return min(vals) if vals else 0


def safe_kinematics_ok(omega, wall_catalog):
    ok, msg = _validate_kinematics_exact(omega)
    if not ok:
        return False, msg

    for value in wall_sign_map(omega, wall_catalog).values():
        if value == 0:
            return False, "mixed wall hit"

    for mask in common.internal_subset_bits(6):
        h, q = common.h_T(omega, mask, SIG_FULL)
        if h == 0:
            return False, "candidate pole hit at subset mask %s" % mask
        if q == 0:
            return False, "q wall q_T=0 at subset mask %s" % mask
    return True, ""


def evaluate_omega(omega, sample_id, wall_catalog, use_double=False):
    omega = [_as_fraction(w) for w in omega]
    if len(omega) != 6:
        raise ValueError("need six omegas")

    if use_double:
        A_re, A_im = run_bg_exact(omega, use_double=True)
    else:
        ok, msg = safe_kinematics_ok(omega, wall_catalog)
        if not ok:
            raise ValueError(msg)
        A_re, A_im = run_bg_exact(omega)

    raw = wall_sign_map(omega, wall_catalog)
    raw_sig = ",".join("%s:%s" % (str(k), raw[k]) for k in [it["id"] for it in wall_catalog])
    wall_noswap, sig_noswap = canonicalize_wall_signatures(
        omega,
        wall_catalog,
        (0, 1, 2),
        (3, 4, 5),
        allow_swap=False,
    )
    wall_swap, sig_swap = canonicalize_wall_signatures(
        omega,
        wall_catalog,
        (0, 1, 2),
        (3, 4, 5),
        allow_swap=True,
    )

    return OracleResult(
        sample_id,
        list(omega),
        A_re,
        A_im,
        raw,
        sig_noswap,
        sig_swap,
        raw_sig,
        min_abs_pole_numerator(omega),
    )


def write_json_lines(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            d = {
                "sample_id": row.sample_id,
                "omega": [frac_to_str(w) for w in row.omega],
                "A_re": frac_to_str(row.A_re),
                "A_im": frac_to_str(row.A_im),
                "raw_wall_signature": row.raw_wall_signature,
                "wall_signature": row.wall_signature,
                "wall_signature_swap": row.wall_signature_swap,
                "wall_signs": row.wall_signs,
                "min_abs_pole_numerator": row.min_abs_pole_numerator,
                "min_abs_candidate_pole_numerator": row.min_abs_pole_numerator,
            }
            f.write(json.dumps(d) + "\n")


def main():
    raise RuntimeError("exact_oracle is intended as a library module")


if __name__ == "__main__":
    main()
