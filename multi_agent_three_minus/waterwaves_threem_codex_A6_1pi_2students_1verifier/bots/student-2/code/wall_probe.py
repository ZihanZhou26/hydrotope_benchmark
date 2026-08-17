
from fractions import Fraction
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple
import json

import sympy as sp

from kinematics import KinematicsPoint, BGOracle, fraction_to_str

T = sp.symbols("t")


def frac_to_symq(x: Fraction) -> sp.Rational:
    return sp.Rational(x.numerator, x.denominator)


def wall_sign_dict_from_point(point: KinematicsPoint, kind: str) -> Dict[str, int]:
    vals = point.pair_q if kind == "pair" else point.triple_q
    out = {}
    for k, v in vals.items():
        if v > 0:
            out[k] = 1
        elif v < 0:
            out[k] = -1
        else:
            out[k] = 0
    return out


def exact_bg_sample(oracle: BGOracle, params: Tuple[Fraction, Fraction, Fraction, Fraction]):
    b, c, d, e = params
    point = KinematicsPoint(b, c, d, e)
    checks = point.conservation_checks()
    if not checks["sum_omega_ok"] or not checks["sum_momentum_ok"]:
        return {"error": "off-shell", "checks": checks}
    if b <= 0 or c <= 0 or d <= 0 or e <= 0:
        return {"error": "nonpositive_param", "checks": checks}

    res = oracle.solve_on_shell((b, c, d, e), n=6)
    F = res.amp_im * point.delta
    return {
        "t_params": {
            "b": fraction_to_str(b),
            "c": fraction_to_str(c),
            "d": fraction_to_str(d),
            "e": fraction_to_str(e),
        },
        "omega": [fraction_to_str(x) for x in point.omega],
        "word": point.sorted_magnitude_word()[0],
        "pair_signs": wall_sign_dict_from_point(point, "pair"),
        "triple_signs": wall_sign_dict_from_point(point, "triple"),
        "amp_im": fraction_to_str(res.amp_im),
        "delta": fraction_to_str(point.delta),
        "F": fraction_to_str(F),
        "pair_a": [fraction_to_str(v) for v in point.pair_q.values()],
        "triple_a": [fraction_to_str(v) for v in point.triple_q.values()],
        "a": fraction_to_str(point.a),
        "f": fraction_to_str(point.f),
        "is_generic": point.is_generic(),
    }


def interpolate_polynomial(samples: List[Dict[str, str]], max_degree: int = 17):
    if len(samples) < 2:
        return {"status": "insufficient", "count": len(samples)}
    points = []
    for r in samples:
        if "F" not in r:
            continue
        t = Fraction(r["t"])
        y = Fraction(r["F"])
        points.append((frac_to_symq(t), frac_to_symq(y)))

    n = len(points)
    if n < 2:
        return {"status": "insufficient"}

    holdout_count = min(3, max(0, n - 2))
    fit_count = max(2, n - holdout_count)
    if fit_count > max_degree + 1:
        fit_count = max_degree + 1
    fit_points = points[:fit_count]

    poly = sp.interpolate(fit_points, T)
    poly_expr = sp.expand(poly)
    ppoly = sp.Poly(poly_expr, T, domain=sp.QQ)
    degree = ppoly.degree()
    status = "ok"
    residual_ok = True
    residual_max = None
    residuals = []
    for tval, yval in points[fit_count:]:
        pred = ppoly.eval(tval)
        res = sp.simplify(pred - yval)
        residuals.append({"t": str(tval), "pred": str(pred), "obs": str(yval), "res": str(res)})
        if res != 0:
            residual_ok = False
    if not residual_ok or degree > max_degree:
        status = "nonpoly"
    return {
        "status": status,
        "fit_count": fit_count,
        "total_count": n,
        "degree": int(degree),
        "term_count": len(ppoly.terms()),
        "expr": str(poly_expr),
        "residuals": residuals,
        "residual_ok": residual_ok,
        "poly": ppoly,
    }


def rational_interpolation(samples: List[Dict[str, str]], max_degree: int = 17):
    points = []
    for r in samples:
        if "F" not in r:
            continue
        t = Fraction(r["t"])
        y = Fraction(r["F"])
        points.append((frac_to_symq(t), frac_to_symq(y)))
    n = len(points)
    if n < 3:
        return {"status": "insufficient", "points": n}

    for den_deg in range(1, 5):
        num_deg = min(max_degree, n - den_deg - 1)
        if num_deg < 1:
            continue
        var_cnt = num_deg + 1 + den_deg
        if n < var_cnt:
            continue

        xs = points[:var_cnt]
        A = [[sp.Rational(0) for _ in range(var_cnt)] for _ in range(var_cnt)]
        b = [sp.Rational(0) for _ in range(var_cnt)]
        for r, (x, y) in enumerate(xs):
            row = []
            for j in range(num_deg + 1):
                row.append(x ** j)
            for j in range(1, den_deg + 1):
                row.append(-y * x ** j)
            A[r] = row
            b[r] = y

        M = sp.Matrix(A)
        if M.det() == 0:
            continue
        coeff = M.LUsolve(sp.Matrix(b))
        p = 0
        for j in range(num_deg + 1):
            p += coeff[j] * T ** j
        q = 1
        for j in range(1, den_deg + 1):
            q += coeff[num_deg + j - 1] * T ** j

        ok = True
        residuals = []
        for x, y in points:
            pred = sp.simplify(p.subs(T, x) / q.subs(T, x))
            res = sp.simplify(pred - y)
            residuals.append({"t": str(x), "pred": str(pred), "obs": str(y), "res": str(res)})
            if res != 0:
                ok = False
                break
        if ok:
            ppoly = sp.together(p / q)
            return {
                "status": "ok",
                "num_degree": num_deg,
                "den_degree": den_deg,
                "expr": str(sp.expand(ppoly)),
                "denominator": str(sp.expand(q)),
                "den_factorization": str(sp.factor(q)),
                "residuals": residuals,
            }
    return {"status": "failed", "points": n}


def factor_branch_diff(left_expr, right_expr, t0: Fraction):
    target = T - frac_to_symq(t0)
    left = sp.expand(left_expr)
    right = sp.expand(right_expr)
    diff = sp.expand(left - right)
    f_list = sp.factor_list(diff)
    mult_t0 = 0
    mult_t = 0
    for fac, e in f_list[1]:
        if fac == T:
            mult_t = e
        if fac == target:
            mult_t0 = e
    return {
        "diff": str(diff),
        "factorized": str(sp.factor(diff)),
        "factor_list": [[str(f), int(exp)] for f, exp in f_list[1]],
        "mult_t": mult_t,
        "mult_t_minus_t0": mult_t0,
        "t0": str(t0),
    }


def wall_profile(oracle: BGOracle, name: str, path_fn: Callable[[Fraction], Tuple[Fraction, Fraction, Fraction, Fraction]], t0: Fraction, target_key: str):
    left_samples: List[Dict[str, object]] = []
    right_samples: List[Dict[str, object]] = []
    step = Fraction(1, 6)
    for k in range(1, 9):
        t = t0 - k * step
        rec = exact_bg_sample(oracle, path_fn(t))
        rec["t"] = str(t)
        if "error" not in rec:
            left_samples.append(rec)
    for k in range(1, 9):
        t = t0 + k * step
        rec = exact_bg_sample(oracle, path_fn(t))
        rec["t"] = str(t)
        if "error" not in rec:
            right_samples.append(rec)

    interp_left = interpolate_polynomial(left_samples)
    interp_right = interpolate_polynomial(right_samples)

    branch_info = {"status": "not_available"}
    if interp_left.get("status") == "ok" and interp_right.get("status") == "ok":
        branch_info = {
            "status": "poly",
            "factorization": factor_branch_diff(interp_left["poly"].as_expr(), interp_right["poly"].as_expr(), t0),
        }
    else:
        rat_left = rational_interpolation(left_samples)
        rat_right = rational_interpolation(right_samples)
        branch_info = {
            "status": "rational",
            "left": rat_left,
            "right": rat_right,
        }

    # wall-isolation check with one-signed sample on each side
    iso_ok = True
    if left_samples and right_samples:
        l1, r1 = left_samples[0], right_samples[0]
        for k in ("pair_signs", "triple_signs"):
            pass
        pL = l1.get("pair_signs", {})
        pR = r1.get("pair_signs", {})
        tL = l1.get("triple_signs", {})
        tR = r1.get("triple_signs", {})
        if pL != pR and k != target_key:
            iso_ok = False

    return {
        "wall": name,
        "t0": str(t0),
        "target_key": target_key,
        "left": left_samples,
        "right": right_samples,
        "left_count": len(left_samples),
        "right_count": len(right_samples),
        "left_fit": interp_left,
        "right_fit": interp_right,
        "branch": branch_info,
        "iso_ok": iso_ok,
    }


def find_pair_wall(oracle: BGOracle) -> Optional[Tuple[Fraction, Fraction, Fraction]]:
    for u in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
        for c in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
            for e in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
                def path(t: Fraction):
                    return (u + t, c, u - t, e)

                # two-sided generic test
                tL = Fraction(-1, 4)
                tR = Fraction(1, 4)
                l = KinematicsPoint(*path(tL))
                r = KinematicsPoint(*path(tR))
                if not l.is_generic() or not r.is_generic():
                    continue
                psL = wall_sign_dict_from_point(l, "pair")
                psR = wall_sign_dict_from_point(r, "pair")
                tsL = wall_sign_dict_from_point(l, "triple")
                tsR = wall_sign_dict_from_point(r, "triple")

                target = "q_2_4"
                if target not in psL or target not in psR:
                    continue
                if psL[target] * psR[target] >= 0:
                    continue
                if any(psL[k] != psR[k] for k in psL if k != target):
                    continue
                if any(tsL[k] != tsR[k] for k in tsL):
                    continue
                return (u, c, e)
    return None


def find_af_wall(oracle: BGOracle) -> Optional[Dict[str, str]]:
    # search a path family where a-f flips and no other tracked wall flips
    families = {
        "vary_cd": lambda u, b, e: lambda t: (b, u + t, u - t, e),
        "vary_bc": lambda u, d, e: lambda t: (u + t, u - t, d, e),
        "vary_be": lambda u, b, d: lambda t: (u + t, b, d, u - t),
    }

    for name, ctor in families.items():
        for u in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
            for x in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
                for y in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
                    if name == "vary_cd":
                        path = ctor(u, x, y)
                    elif name == "vary_bc":
                        path = ctor(u, x, y)
                    else:
                        path = ctor(u, x, y)

                    tL = Fraction(-1, 6)
                    tR = Fraction(1, 6)
                    try:
                        l = KinematicsPoint(*path(tL))
                        r = KinematicsPoint(*path(tR))
                    except Exception:
                        continue
                    if not l.is_generic() or not r.is_generic():
                        continue
                    if (l.a - l.f) * (r.a - r.f) >= 0:
                        continue
                    pL = wall_sign_dict_from_point(l, "pair")
                    pR = wall_sign_dict_from_point(r, "pair")
                    ttrL = wall_sign_dict_from_point(l, "triple")
                    ttrR = wall_sign_dict_from_point(r, "triple")
                    if pL != pR and ttrL != ttrR:
                        continue
                    return {
                        "family": name,
                        "u": fraction_to_str(u),
                        "x": fraction_to_str(x),
                        "y": fraction_to_str(y),
                        "root_t0": "0",
                    }
    return None


def find_triple_wall() -> Optional[Tuple[Fraction, Fraction, Fraction]]:
    # q_{b;d,e}=d^2+e^2-b^2 ; with b=u+t, d=u-t -> root t0=e^2/(4u)
    for u in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
        for c in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
            for e in [Fraction(1), Fraction(2), Fraction(3), Fraction(4)]:
                t0 = e * e / (Fraction(4) * u)
                def path(t: Fraction):
                    return (u + t, c, u - t, e)
                tL = t0 - Fraction(1, 4)
                tR = t0 + Fraction(1, 4)
                l = KinematicsPoint(*path(tL))
                r = KinematicsPoint(*path(tR))
                if not l.is_generic() or not r.is_generic():
                    continue
                triL = wall_sign_dict_from_point(l, "triple")
                triR = wall_sign_dict_from_point(r, "triple")
                target = "q_2_45"
                if target not in triL:
                    continue
                if triL[target] * triR[target] >= 0:
                    continue
                if any(
                    triL[k] != triR[k] for k in triL
                    if k != target
                ):
                    continue
                # keep all pair walls fixed
                pL = wall_sign_dict_from_point(l, "pair")
                pR = wall_sign_dict_from_point(r, "pair")
                if any(pL[k] != pR[k] for k in pL):
                    continue
                return (u, c, e)
    return None


def main():
    qdir = Path(".").resolve()
    out_json = qdir / "bots/student-2/data/wall_probe.json"
    out_txt = qdir / "bots/student-2/derivations/wall_probe.txt"
    oracle = BGOracle(qdir / "bots/student-2/bg")

    result = {
        "pair_wall": {"status": "not_found"},
        "triple_wall": {"status": "not_found"},
        "af_wall": {"status": "not_found"},
    }

    pair_choice = find_pair_wall(oracle)
    if pair_choice is not None:
        u, c, e = pair_choice
        result["pair_wall"] = wall_profile(
            oracle=oracle,
            name="pair_b_eq_d",
            path_fn=lambda t, uu=u, cc=c, ee=e: (uu + t, cc, uu - t, ee),
            t0=Fraction(0),
            target_key="q_2_4",
        )
        result["pair_wall"]["path_params"] = {"u": fraction_to_str(u), "c": fraction_to_str(c), "e": fraction_to_str(e)}

    af = find_af_wall(oracle)
    if af is not None:
        result["af_wall"] = af

    triple_choice = find_triple_wall()
    if triple_choice is not None:
        u, c, e = triple_choice
        t0 = e * e / (Fraction(4) * u)
        result["triple_wall"] = wall_profile(
            oracle=oracle,
            name="triple_bde",
            path_fn=lambda t, uu=u, cc=c, ee=e: (uu + t, cc, uu - t, ee),
            t0=t0,
            target_key="q_2_45",
        )
        result["triple_wall"]["path_params"] = {"u": fraction_to_str(u), "c": fraction_to_str(c), "e": fraction_to_str(e)}
        result["triple_wall"]["formula_t0"] = str(t0)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True, default=str))

    with out_txt.open("w") as fp:
        fp.write("# Wall probe full expressions\n\n")
        fp.write(json.dumps(result, indent=2, sort_keys=True, default=str))

    print(out_json)
    print(out_txt)


if __name__ == "__main__":
    main()
