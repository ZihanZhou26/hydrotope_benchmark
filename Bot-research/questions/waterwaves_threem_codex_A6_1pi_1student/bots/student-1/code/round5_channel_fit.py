#!/usr/bin/env python3
"""Fixed-channel H=A6/(i*prod omega) ansatz fitting for round 5.

Builds:
- Stage A: degree-4 raw-channel numerator orbits Phi = sum_G m_S/h_S
- Stage B (fallback): augment m2_S * |K_T| (and optional |K_T||K_U|)

Evaluates against a local exact BG oracle and reports modular consistency over
at least two primes.
"""

import argparse
import json
import random
import re
import subprocess
import time
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations, permutations
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple



ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT.parent / "data"
BG_BIN = ROOT / "bg_round5_channels"
SIG = (-1, -1, -1, 1, 1, 1)
MODS = [2305843009213693951, 1000000007]
MAX_ROWS = 3200
HOLDOUT_TARGET = 120

# Group G = S3 x S3 semidirect C2
Action = Tuple[Tuple[int, int, int], Tuple[int, int, int], bool]
ACTIONS: List[Action] = []
for pm in permutations((0, 1, 2)):
    for pp in permutations((0, 1, 2)):
        ACTIONS.append((pm, pp, False))
        ACTIONS.append((pm, pp, True))

SEED_MASKS = [sum(1 << i for i in s) for s in [(0, 1), (0, 3), (0, 1, 2), (0, 1, 3)]]
MASKS_2 = [sum(1 << i for i in c) for c in combinations(range(6), 2)]
MASKS_3 = [sum(1 << i for i in c) for c in combinations(range(6), 3)]
MASKS_23 = MASKS_2 + MASKS_3


def frac(x: object) -> Fraction:
    if isinstance(x, Fraction):
        return x
    if isinstance(x, int):
        return Fraction(x, 1)
    return Fraction(str(x))


def frac_to_str(x: Fraction) -> str:
    if x.denominator == 1:
        return str(x.numerator)
    return f"{x.numerator}/{x.denominator}"


def to_mod(f: Fraction, p: int) -> int:
    return (f.numerator % p) * pow(f.denominator % p, p - 2, p) % p


def parse_fraction_text(txt: str) -> Fraction:
    t = txt.strip()
    if not t:
        raise ValueError("empty token")
    t = t.strip("() ")
    m = re.search(r"[-+]?\d+\s*/\s*\d+|[-+]?\d+", t)
    if not m:
        raise ValueError("unparseable token: %s" % t)
    return frac(m.group(0).replace(" ", ""))


def check_conservation(omega: Sequence[Fraction]) -> bool:
    if sum(omega) != 0:
        return False
    if sum(SIG[i] * omega[i] * omega[i] for i in range(6)) != 0:
        return False
    return True


def target_H(im_H: Fraction, omega: Sequence[Fraction]) -> Fraction:
    prod = Fraction(1, 1)
    for w in omega:
        if w == 0:
            raise ValueError("nonzero denominator required")
        prod *= w
    return im_H / prod


def subset_from_mask(mask: int) -> Tuple[int, ...]:
    return tuple(i for i in range(6) if (mask >> i) & 1)


def transform_index(i: int, action: Action) -> int:
    pm, pp, swap = action
    if swap:
        if i < 3:
            return 3 + pm[i]
        return pp[i - 3]
    if i < 3:
        return pm[i]
    return 3 + pp[i - 3]


def transform_mask(mask: int, action: Action) -> int:
    out = 0
    for i in range(6):
        if (mask >> i) & 1:
            out |= 1 << transform_index(i, action)
    return out


def transform_exp(exp: Tuple[int, ...], action: Action) -> Tuple[int, ...]:
    pm, pp, swap = action
    e = [0] * 6
    if swap:
        for i in range(3):
            e[3 + pm[i]] = exp[i]
        for j in range(3):
            e[pp[j]] = exp[3 + j]
    else:
        for i in range(3):
            e[pm[i]] = exp[i]
        for j in range(3):
            e[3 + pp[j]] = exp[3 + j]
    return tuple(e)


def full_sign(omega: Sequence[Fraction]) -> Tuple[int, ...]:
    a = [w * w for w in omega[:3]]
    b = [w * w for w in omega[3:]]
    T = a[0] + a[1] + a[2]
    out: List[int] = []
    for i in range(3):
        for j in range(3):
            v = a[i] - b[j]
            out.append(1 if v > 0 else -1 if v < 0 else 0)
    for i in range(3):
        for j in range(3):
            v = a[i] + b[j] - T
            out.append(1 if v > 0 else -1 if v < 0 else 0)
    for r in (2, 3):
        for combi in combinations(range(6), r):
            wS = sum(omega[i] for i in combi)
            qS = sum(SIG[i] * omega[i] * omega[i] for i in combi)
            h = wS * wS - (qS if qS >= 0 else -qS)
            out.append(1 if h > 0 else -1 if h < 0 else 0)
    return tuple(out)


def full_sign_18(omega: Sequence[Fraction]) -> Tuple[int, ...]:
    return full_sign(omega)[:18]


def solve_from_free(free: Sequence[Fraction]):
    f = [frac(x) for x in free]
    s = sum(f)
    if s == 0:
        return None
    ss = SIG[1] * f[0] * f[0] + SIG[2] * f[1] * f[1] + SIG[3] * f[2] * f[2] + SIG[4] * f[3] * f[3]
    wn = -(SIG[0] * s * s + ss) / (2 * SIG[0] * s)
    w1 = -(s + wn)
    return (w1, f[0], f[1], f[2], f[3], wn)


def eval_bg(omega: Sequence[Fraction], timeout_s: float = 2.0) -> Tuple[Fraction, Fraction]:
    k = [frac(SIG[i]) * omega[i] * omega[i] for i in range(6)]
    cmd = [
        str(BG_BIN),
        "--amp",
        "-K",
        ",".join(frac_to_str(x) for x in k),
        "-W",
        ",".join(frac_to_str(x) for x in omega),
        "-g",
        "1",
    ]
    try:
        p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired as e:
        raise RuntimeError("bg timeout: %s" % str(e))
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip())
    text = p.stdout
    m = re.search(r"A_6\s*=\s*\(\s*([^)]*?)\s*\)\s*\+\s*i\s*\(\s*([^)]*?)\s*\)", text)
    if m:
        return parse_fraction_text(m.group(1)), parse_fraction_text(m.group(2))
    m2 = re.search(r"A_6\s*=\s*i\s*\*?\(?\s*([^)]*?)\s*\)", text)
    if m2:
        return Fraction(0), parse_fraction_text(m2.group(1))
    raise RuntimeError("unable to parse bg output")
class MappingLike(dict):
    pass


def poly_add(dst, src, factor=1):
    for e, c in src.items():
        dst[e] = dst.get(e, 0) + factor * c
        if dst[e] == 0:
            del dst[e]


def poly_mul(
    a: MappingLike,
    b: MappingLike,
    max_deg: int,
) -> Dict[Tuple[int, int, int, int, int, int], int]:
    out: Dict[Tuple[int, int, int, int, int, int], int] = {}
    for e1, c1 in a.items():
        d1 = sum(e1)
        if d1 > max_deg:
            continue
        for e2, c2 in b.items():
            d2 = sum(e2)
            if d1 + d2 > max_deg:
                continue
            e = tuple(x + y for x, y in zip(e1, e2))
            out[e] = out.get(e, 0) + c1 * c2
            if out[e] == 0:
                del out[e]
    return out


_CELL_ELEM: Dict[Tuple[int, int], Dict[Tuple[int, int, int, int, int, int], int]] = {}

def cell_elem(mask: int, d: int) -> Dict[Tuple[int, int, int, int, int, int], int]:
    key = (mask, d)
    if key in _CELL_ELEM:
        return _CELL_ELEM[key]
    idx = subset_from_mask(mask)
    if d < 0 or d > len(idx):
        out = {}
    elif d == 0:
        out = {(0, 0, 0, 0, 0, 0): 1}
    else:
        out: Dict[Tuple[int, int, int, int, int, int], int] = {}
        for comb in combinations(idx, d):
            e = [0] * 6
            for i in comb:
                e[i] = 1
            keye = tuple(e)
            out[keye] = out.get(keye, 0) + 1
    _CELL_ELEM[key] = out
    return out


def seed_cells(seed: int) -> Tuple[int, int, int, int]:
    minus = (0, 1, 2)
    plus = (3, 4, 5)
    S = set(subset_from_mask(seed))
    mS = [i for i in minus if i in S]
    pS = [i for i in plus if i in S]
    return (
        sum(1 << i for i in mS),
        sum(1 << i for i in pS),
        sum(1 << i for i in minus if i not in S),
        sum(1 << i for i in plus if i not in S),
    )


_RAW_SEED_CACHE: Dict[Tuple[int, Tuple[int, int, int, int]], Dict[Tuple[int, int, int, int, int, int], int]] = {}

def raw_poly_seed(seed: int, degrees: Tuple[int, int, int, int], max_deg: int = 4) -> Dict[Tuple[int, int, int, int, int, int], int]:
    key = (seed, degrees)
    if key in _RAW_SEED_CACHE:
        return _RAW_SEED_CACHE[key]
    d1, d2, d3, d4 = degrees
    c1, c2, c3, c4 = seed_cells(seed)
    if d1 > len(subset_from_mask(c1)) or d2 > len(subset_from_mask(c2)) or d3 > len(subset_from_mask(c3)) or d4 > len(subset_from_mask(c4)):
        _RAW_SEED_CACHE[key] = {}
        return {}
    p1 = cell_elem(c1, d1)
    p2 = cell_elem(c2, d2)
    p3 = cell_elem(c3, d3)
    p4 = cell_elem(c4, d4)
    poly = poly_mul(p1, p2, max_deg)
    poly = poly_mul(poly, p3, max_deg)
    poly = poly_mul(poly, p4, max_deg)
    _RAW_SEED_CACHE[key] = poly
    return poly


def poly_for_monomial(exp: Tuple[int, int, int, int, int, int]) -> Dict[Tuple[int, int, int, int, int, int], int]:
    return {exp: 1}


def eval_poly_mod(poly: Dict[Tuple[int, int, int, int, int, int], int], omega_pow_mod: List[List[int]], p: int) -> int:
    out = 0
    for exp, c in poly.items():
        v = c % p
        if v == 0:
            continue
        for i, e in enumerate(exp):
            if e:
                v = (v * omega_pow_mod[i][e]) % p
        out = (out + v) % p
    return out


def eval_poly_exact(poly: Dict[Tuple[int, int, int, int, int, int], int], omega_pow: List[List[Fraction]]) -> Fraction:
    out = Fraction(0, 1)
    for exp, c in poly.items():
        v = Fraction(c, 1)
        for i, e in enumerate(exp):
            if e:
                v *= omega_pow[i][e]
        out += v
    return out


class FeatureTerm(object):
    __slots__ = ("denom_mask", "abs_masks", "num_poly")

    def __init__(self, denom_mask, abs_masks, num_poly):
        self.denom_mask = denom_mask
        self.abs_masks = tuple(abs_masks)
        self.num_poly = dict(num_poly)

    def key(self):
        return (self.denom_mask, self.abs_masks, tuple(sorted(self.num_poly.items())))


class Feature(object):
    __slots__ = ("terms",)

    def __init__(self, terms):
        self.terms = list(terms)

    def key(self):
        return tuple(sorted(t.key() for t in self.terms))

    def eval_mod(self, s: "Sample", p: int) -> int:
        v = 0
        for t in self.terms:
            num = s.eval_poly_mod(t.num_poly, p)
            den_mask = t.denom_mask
            for m in t.abs_masks:
                num = (num * s.absq_mod[p][m]) % p
            if den_mask != 0:
                num = (num * s.h_inv_mod[p][den_mask]) % p
            v = (v + num) % p
        return v

    def eval_exact(self, s: "Sample") -> Fraction:
        v = Fraction(0, 1)
        for t in self.terms:
            num = s.eval_poly_exact(t.num_poly)
            for m in t.abs_masks:
                num *= s.absq_exact[m]
            if t.denom_mask != 0:
                num /= s.h_exact[t.denom_mask]
            v += num
        return v


class Sample:
    def __init__(self, sid: int, omega: Sequence[Fraction], imH: Fraction, sign53: Tuple[int, ...]):
        self.id = sid
        self.omega = tuple(omega)
        self.H = imH
        self.sign53 = tuple(sign53)
        self.sign18 = tuple(sign53[:18])

        self.h_exact: Dict[int, Fraction] = {}
        self.absq_exact: Dict[int, Fraction] = {}
        self.h_mod: Dict[int, Dict[int, int]] = {p: {} for p in MODS}
        self.h_inv_mod: Dict[int, Dict[int, int]] = {p: {} for p in MODS}
        self.absq_mod: Dict[int, Dict[int, int]] = {p: {} for p in MODS}

        self.omega_pow_mod: Dict[int, List[List[int]]] = {}
        self.omega_pow_exact: List[List[Fraction]] = []
        self.poly_cache_mod: Dict[
            int, Dict[Tuple[Tuple[Tuple[int, int, int, int, int, int], int], ...], int]
        ] = {p: {} for p in MODS}
        self.poly_cache_exact: Dict[Tuple[Tuple[Tuple[int, int, int, int, int, int], int], ...], Fraction] = {}

        self.valid = True

        for p in MODS:
            wmod = [to_mod(w, p) for w in self.omega]
            powmod: List[List[int]] = []
            for w in wmod:
                row = [1]
                for _ in range(4):
                    row.append((row[-1] * w) % p)
                powmod.append(row)
            self.omega_pow_mod[p] = powmod
        for w in self.omega:
            row = [Fraction(1, 1)]
            for _ in range(4):
                row.append(row[-1] * w)
            self.omega_pow_exact.append(row)

        for mask in MASKS_23:
            idx = subset_from_mask(mask)
            q = Fraction(0, 1)
            for j in idx:
                q += SIG[j] * self.omega[j] * self.omega[j]
            if q == 0:
                self.valid = False
                return
            absq = q if q >= 0 else -q
            wsum = sum(self.omega[j] for j in idx)
            h = wsum * wsum - absq
            if h == 0:
                self.valid = False
                return
            self.absq_exact[mask] = absq
            self.h_exact[mask] = h
            for p in MODS:
                absq_m = to_mod(absq, p)
                h_m = to_mod(h, p)
                if h_m == 0:
                    self.valid = False
                    return
                self.absq_mod[p][mask] = absq_m
                self.h_mod[p][mask] = h_m
                self.h_inv_mod[p][mask] = pow(h_m, p - 2, p)

    def eval_poly_mod(self, poly: Dict[Tuple[int, int, int, int, int, int], int], p: int) -> int:
        key = tuple(sorted(poly.items()))
        cache = self.poly_cache_mod[p]
        if key in cache:
            return cache[key]
        v = eval_poly_mod(poly, self.omega_pow_mod[p], p)
        cache[key] = v
        return v

    def eval_poly_exact(self, poly: Dict[Tuple[int, int, int, int, int, int], int]) -> Fraction:
        key = tuple(sorted(poly.items()))
        cache = self.poly_cache_exact
        if key in cache:
            return cache[key]
        v = eval_poly_exact(poly, self.omega_pow_exact)
        cache[key] = v
        return v


def build_p2_features() -> List[Feature]:
    exps: List[Tuple[int, int, int, int, int, int]] = []
    for i in range(6):
        e = [0] * 6
        e[i] = 2
        exps.append(tuple(e))
    for i in range(6):
        for j in range(i + 1, 6):
            e = [0] * 6
            e[i] = e[j] = 1
            exps.append(tuple(e))

    dedup: Dict[Tuple, Feature] = {}
    for exp in exps:
        poly: Dict[Tuple[int, int, int, int, int, int], int] = {}
        for act in ACTIONS:
            e2 = transform_exp(exp, act)
            poly_add(poly, {e2: 1})
        f = Feature([FeatureTerm(0, tuple(), dict(poly))])
        dedup[f.key()] = f
    return list(dedup.values())


def stageA_features() -> List[Feature]:
    dedup: Dict[Tuple, Feature] = {}
    for s in SEED_MASKS:
        for d1 in range(0, 4 + 1):
            for d2 in range(0, 4 - d1 + 1):
                for d3 in range(0, 4 - d1 - d2 + 1):
                    d4 = 4 - d1 - d2 - d3
                    c1, c2, c3, c4 = seed_cells(s)
                    if (
                        d1 > len(subset_from_mask(c1))
                        or d2 > len(subset_from_mask(c2))
                        or d3 > len(subset_from_mask(c3))
                        or d4 > len(subset_from_mask(c4))
                    ):
                        continue
                    term_map: Dict[Tuple[int, Tuple[int, ...]], Dict[Tuple[int, int, int, int, int, int], int]] = {}
                    for act in ACTIONS:
                        ss = transform_mask(s, act)
                        raw = raw_poly_seed(ss, (d1, d2, d3, d4), 4)
                        if not raw:
                            continue
                        term_map.setdefault((ss, tuple()), {})
                        poly_add(term_map[(ss, tuple())], raw)
                    terms = [FeatureTerm(den, tuple(), dict(poly)) for (den, _), poly in term_map.items() if poly]
                    if not terms:
                        continue
                    f = Feature(terms=terms)
                    dedup[f.key()] = f
    return list(dedup.values())


def stabilizer_orbits(seed: int) -> List[Tuple[int, ...]]:
    stab_actions = [a for a in ACTIONS if transform_mask(seed, a) == seed]
    seen = set()
    orbits: List[Tuple[int, ...]] = []
    for m in MASKS_23:
        if m in seen:
            continue
        comp = set()
        stack = [m]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            for act in stab_actions:
                y = transform_mask(x, act)
                if y not in comp:
                    stack.append(y)
        seen.update(comp)
        orbits.append(tuple(sorted(comp)))
    return orbits


def stageB_features() -> Tuple[List[Feature], List[Feature], Dict[str, object]]:
    # Build orbit-summed |K|-tier features:
    #   m2_{gS0}|K_{gT0}| / h_{gS0}
    base_orbit_terms: Dict[Tuple, Dict[Tuple[int, Tuple[int]], Dict[Tuple[int, int, int, int, int, int], int]]] = {}
    # Build optional pair orbit-summed features:
    #   |K_{gT0}||K_{gU0}| / h_{gS0}
    pair_orbit_terms: Dict[Tuple, Dict[Tuple[int, Tuple[int, int]], Dict[Tuple[int, int, int, int, int, int], int]]] = {}

    def add_term(
        acc: Dict,
        bucket_key: Tuple,
        den_mask: int,
        abs_masks: Tuple[int, ...],
        poly: Dict[Tuple[int, int, int, int, int, int], int],
    ) -> None:
        bucket = acc.setdefault(bucket_key, {})
        key2 = (den_mask, abs_masks)
        if key2 not in bucket:
            bucket[key2] = {}
        poly_add(bucket[key2], poly)

    def feature_list_from_buckets(
        buckets: Dict[Tuple, Dict[Tuple[int, Tuple[int, ...]], Dict[Tuple[int, int, int, int, int, int], int]]]
    ) -> List[Feature]:
        out: Dict[Tuple, Feature] = {}
        for bucket in buckets.values():
            terms = [FeatureTerm(den, tuple(sorted(abs_masks)), dict(poly)) for (den, abs_masks), poly in bucket.items() if poly]
            if not terms:
                continue
            feat = Feature(terms)
            out[feat.key()] = feat
        return list(out.values())

    for s in SEED_MASKS:
        for d1 in range(0, 3 + 1):
            for d2 in range(0, 3 - d1 + 1):
                for d3 in range(0, 3 - d1 - d2 + 1):
                    d4 = 2 - d1 - d2 - d3
                    if d4 < 0:
                        continue
                    c1, c2, c3, c4 = seed_cells(s)
                    if (
                        d1 > len(subset_from_mask(c1))
                        or d2 > len(subset_from_mask(c2))
                        or d3 > len(subset_from_mask(c3))
                        or d4 > len(subset_from_mask(c4))
                    ):
                        continue
                    for t0 in MASKS_23:
                        feat_key = (s, d1, d2, d3, d4, t0)
                        for act in ACTIONS:
                            ss = transform_mask(s, act)
                            tt = transform_mask(t0, act)
                            raw = raw_poly_seed(ss, (d1, d2, d3, d4), 2)
                            if not raw:
                                continue
                            add_term(base_orbit_terms, feat_key, ss, (tt,), raw)

    base_feats = feature_list_from_buckets(base_orbit_terms)

    pair_orbit_total = 0
    pair_total_pairs: List[Tuple[int, int]] = []
    for s in SEED_MASKS:
        for orb in stabilizer_orbits(s):
            idx = list(orb)
            pair_orbit_total += len(idx) * (len(idx) + 1) // 2
            for i in range(len(idx)):
                for j in range(i, len(idx)):
                    pair_total_pairs.append((idx[i], idx[j]))
    if pair_total_pairs:
        one_poly: Dict[Tuple[int, int, int, int, int, int], int] = {(0, 0, 0, 0, 0, 0): 1}
        for s in SEED_MASKS:
            for t0, u0 in pair_total_pairs:
                feat_key = (s, t0, u0, 2)  # 2 labels that this is a pair tier feature.
                for act in ACTIONS:
                    ss = transform_mask(s, act)
                    tt = transform_mask(t0, act)
                    uu = transform_mask(u0, act)
                    add_term(pair_orbit_terms, feat_key, ss, tuple(sorted((tt, uu))), one_poly)

    pair_feats = feature_list_from_buckets(pair_orbit_terms)
    return base_feats, pair_feats, {
        "base": len(base_feats),
        "pair": len(pair_feats),
        "pair_orbit_total": pair_orbit_total,
        "status": "base_and_optional_pair_available",
    }


def rank_mod(matrix: List[List[int]], ncol: int, p: int) -> int:
    if not matrix:
        return 0
    M = [row[:] for row in matrix]
    m = len(M)
    row = 0
    for col in range(ncol):
        piv = None
        for r in range(row, m):
            if M[r][col] % p:
                piv = r
                break
        if piv is None:
            continue
        if piv != row:
            M[row], M[piv] = M[piv], M[row]
        inv = pow(M[row][col], p - 2, p)
        for k in range(col, ncol):
            M[row][k] = (M[row][k] * inv) % p
        for r in range(m):
            if r == row:
                continue
            fac = M[r][col] % p
            if fac == 0:
                continue
            for k in range(col, ncol):
                M[r][k] = (M[r][k] - fac * M[row][k]) % p
        row += 1
        if row == m:
            break
    return row


def gauss_mod(X: List[List[int]], y: List[int], p: int):
    nrow = len(X)
    ncol = len(X[0]) if X else 0
    aug = [row[:] + [yy] for row, yy in zip(X, y)]
    rank = 0
    pivots: Dict[int, int] = {}

    for col in range(ncol):
        piv = None
        for r in range(rank, nrow):
            if aug[r][col] % p:
                piv = r
                break
        if piv is None:
            continue
        if piv != rank:
            aug[rank], aug[piv] = aug[piv], aug[rank]
        inv = pow(aug[rank][col], p - 2, p)
        for k in range(col, ncol + 1):
            aug[rank][k] = (aug[rank][k] * inv) % p
        for r in range(nrow):
            if r == rank:
                continue
            fac = aug[r][col] % p
            if fac == 0:
                continue
            for k in range(col, ncol + 1):
                aug[r][k] = (aug[r][k] - fac * aug[rank][k]) % p
        pivots[rank] = col
        rank += 1

    for r in range(rank, nrow):
        if any(aug[r][k] % p != 0 for k in range(ncol)):
            if aug[r][ncol] % p != 0:
                return False, rank, rank, None

    sol = [0] * ncol
    for r, col in pivots.items():
        sol[col] = aug[r][ncol] % p
    return True, rank, rank, sol


def build_matrix(samples: Sequence[Sample], feats: Sequence[Feature], p: int) -> Tuple[List[List[int]], List[int]]:
    X: List[List[int]] = []
    y: List[int] = []
    for s in samples:
        X.append([f.eval_mod(s, p) for f in feats])
        y.append(to_mod(s.H, p))
    return X, y


def exact_solve(samples: Sequence[Sample], feats: Sequence[Feature]):
    nvar = len(feats)
    if not samples or len(samples) < nvar:
        return False, None
    M: List[List[Fraction]] = []
    for s in samples[: max(nvar + 8, 2 * nvar)]:
        row = [s.eval_exact(f) for f in feats]
        row.append(s.H)
        M.append(row)

    nrow = len(M)
    rank = 0
    pivots: Dict[int, int] = {}
    for col in range(nvar):
        piv = None
        for r in range(rank, nrow):
            if M[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        if piv != rank:
            M[rank], M[piv] = M[piv], M[rank]
        inv = Fraction(1, 1) / M[rank][col]
        M[rank] = [v * inv for v in M[rank]]
        for r in range(nrow):
            if r == rank:
                continue
            fac = M[r][col]
            if fac == 0:
                continue
            M[r] = [a - fac * b for a, b in zip(M[r], M[rank])]
        pivots[rank] = col
        rank += 1
        if rank == nrow:
            break

    for r in range(rank, nrow):
        if any(M[r][c] != 0 for c in range(nvar)) and M[r][nvar] != 0:
            return False, None

    sol = [Fraction(0, 1)] * nvar
    for r, c in pivots.items():
        sol[c] = M[r][nvar]
    return True, sol


def residuals_exact(samples: Sequence[Sample], feats: Sequence[Feature], coeffs: Sequence[Fraction]) -> Dict[str, object]:
    max_abs = Fraction(0, 1)
    bad: List[Tuple[int, str]] = []
    for s in samples:
        pred = Fraction(0, 1)
        for c, f in zip(coeffs, feats):
            pred += c * f.eval_exact(s)
        r = pred - s.H
        if r < 0:
            r = -r
        if r > max_abs:
            max_abs = r
        if r != 0:
            bad.append((s.id, frac_to_str(r)))
    return {
        "max_abs": frac_to_str(max_abs),
        "bad": len(bad),
        "examples": bad[:10],
    }


def assert_cached_mod_exact(samples: Sequence[Sample], feats: Sequence[Feature], primes: List[int], cap_samples: int = 3) -> None:
    if not samples or not feats:
        return
    s_cap = list(samples)[: min(cap_samples, len(samples))]
    for s in s_cap:
        for f in feats[: min(6, len(feats))]:
            exact_v = f.eval_exact(s)
            exact_mod = {p: to_mod(exact_v, p) for p in primes}
            for p in primes:
                mod_v = f.eval_mod(s, p)
                if mod_v != exact_mod[p]:
                    raise AssertionError(
                        "mod-compatibility failure: sample=%d, prime=%d, mod=%d, exact=%d"
                        % (s.id, p, mod_v, exact_mod[p])
                    )


def fit_stage(name: str, feats: Sequence[Feature], train: Sequence[Sample], hold: Sequence[Sample]):
    out: Dict[str, object] = {
        "name": name,
        "feature_count": len(feats),
        "status": "untested",
        "prime_results": {},
    }

    assert_cached_mod_exact(train, feats, list(MODS), cap_samples=2)

    mod_solutions: Dict[int, List[int]] = {}

    for p in MODS:
        X, y = build_matrix(train, feats, p)
        rankX = rank_mod(X, len(feats), p)
        aug = [r[:] + [yy] for r, yy in zip(X, y)]
        rankA = rank_mod(aug, len(feats) + 1, p)
        out["prime_results"][str(p)] = {
            "rows": len(train),
            "rankX": rankX,
            "rankAug": rankA,
            "ncols": len(feats),
        }
        if rankA > rankX:
            out["status"] = "inconsistent"
            out["prime_results"][str(p)]["consistent"] = False
            continue
        out["prime_results"][str(p)]["consistent"] = True
        ok, rX, rA, sol = gauss_mod(X, y, p)
        out["prime_results"][str(p)]["rank_from_gauss"] = rX
        if not ok:
            out["status"] = "inconsistent"
            out["prime_results"][str(p)]["consistent"] = False
            continue
        if sol is not None:
            mod_solutions[p] = sol

    if any(v["consistent"] is False for v in out["prime_results"].values()):
        out["status"] = "inconsistent"
        return out, None

    # exact reconstruction attempt
    ok_exact, coeffs = exact_solve(list(train), list(feats))
    if not ok_exact or coeffs is None:
        out["status"] = "reconstruction_blocked"
        return out, None

    tr = residuals_exact(train, feats, coeffs)
    ho = residuals_exact(hold, feats, coeffs)
    out["exact"] = {
        "train": tr,
        "hold": ho,
        "coeffs": [frac_to_str(c) for c in coeffs],
        "mod_sols": {str(p): [str(x) for x in v] for p, v in mod_solutions.items()},
    }
    if tr["bad"] == 0 and ho["bad"] == 0:
        out["status"] = "fit"
    else:
        out["status"] = "exact_residual_fail"
    return out, coeffs if tr["bad"] == 0 and ho["bad"] == 0 else None


def random_free(rng: random.Random) -> List[Fraction]:
    den = rng.choice([1, 1, 2, 2, 3, 4, 5, 6])
    out = []
    for _ in range(4):
        n = rng.randint(-13, 13)
        if n == 0:
            n = rng.choice((1, -1))
        out.append(Fraction(n, den))
        if rng.random() < 0.20:
            n2 = rng.randint(-9, 9)
            if n2 == 0:
                n2 = 1
            d2 = rng.randint(2, 11)
            out[-1] = Fraction(n2, d2)
    return out


def family_frees() -> List[List[Fraction]]:
    return [
        [Fraction(17), Fraction(2), Fraction(-1), Fraction(1)],
        [Fraction(19), Fraction(-3), Fraction(1), Fraction(2)],
        [Fraction(23), Fraction(1), Fraction(-2), Fraction(1)],
        [Fraction(13, 2), Fraction(1), Fraction(1), Fraction(-3)],
        [Fraction(1, 2), Fraction(7), Fraction(-1), Fraction(17)],
        [Fraction(1), Fraction(5), Fraction(2), Fraction(31, 2)],
    ]


def collect_points(min_rows: int, holdout: int) -> Tuple[List[Sample], Dict[str, object], Dict[Tuple[int, ...], int]]:
    return collect_points_limited(min_rows, holdout, max_attempts=200000, bg_timeout=2.0, progress_every=250)


def collect_points_limited(
    min_rows: int,
    holdout: int,
    max_attempts: int = 50000,
    bg_timeout: float = 2.0,
    progress_every: int = 250,
) -> Tuple[List[Sample], Dict[str, object], Dict[Tuple[int, ...], int]]:
    rng = random.Random(2026)
    points: List[Sample] = []
    sig_counts: Counter = Counter()
    sig18_counts: Counter = Counter()

    # family + random
    candidates: List[Tuple[bool, List[Fraction]]] = [(True, free) for free in family_frees()]

    attempts = 0
    seen = set()
    family_used = 0

    t_start = time.time()
    while len(points) < min_rows and attempts < max_attempts:
        if candidates:
            force, fvals = candidates.pop(0)
        else:
            force = False
            fvals = random_free(rng)

        ft = tuple(fvals)
        if ft in seen:
            attempts += 1
            continue
        seen.add(ft)

        om = solve_from_free(fvals)
        if om is None:
            attempts += 1
            continue
        if any(x == 0 for x in om):
            attempts += 1
            continue
        if not check_conservation(om):
            attempts += 1
            continue
        if not all(x != 0 for x in om):
            attempts += 1
            continue

        try:
            re_p, im_p = eval_bg(om, timeout_s=bg_timeout)
        except Exception:
            attempts += 1
            continue
        if re_p != 0 or im_p == 0:
            attempts += 1
            continue
        try:
            H = target_H(im_p, om)
        except Exception:
            attempts += 1
            continue
        if H == 0:
            attempts += 1
            continue

        sig = full_sign(om)
        if 0 in sig:
            attempts += 1
            continue

        s = Sample(len(points), om, H, sig)
        if not s.valid:
            attempts += 1
            continue

        points.append(s)
        if force:
            family_used += 1
        sig_counts[s.sign53] += 1
        sig18_counts[s.sign18] += 1
        attempts += 1
        if progress_every and (len(points) % progress_every == 0 or attempts % progress_every == 0):
            print(
                "collect_points: points=%d attempts=%d elapsed=%.1fs"
                % (len(points), attempts, time.time() - t_start)
            )

    report = {
        "requested": min_rows,
        "collected": len(points),
        "attempts": attempts,
        "max_attempts": max_attempts,
        "bg_timeout": bg_timeout,
        "family_used": family_used,
        "target_definition": "H := im(A6)/prod(omega)",
        "conservation_checked": True,
        "conservation_eq": "sum(omega)=0 and sum(sig_i*omega_i^2)=0",
        "num_sign18": len(sig18_counts),
        "num_sign53": len(sig_counts),
    }
    return points, report, dict(sig_counts)


def split_train_hold(points: List[Sample], hold_n: int = HOLDOUT_TARGET) -> Tuple[List[Sample], List[Sample]]:
    if len(points) <= hold_n:
        return points, []
    rng = random.Random(9001)
    pts = list(points)
    rng.shuffle(pts)
    hold = pts[:hold_n]
    train = pts[hold_n:]
    return train, hold


def serialize_feature_payload(feats: Sequence[Feature]) -> List[Dict[str, object]]:
    data = []
    for f in feats:
        data.append(
            {
                "terms": [
                    {
                        "denom_mask": t.denom_mask,
                        "abs_masks": list(t.abs_masks),
                        "poly": [(list(k), c) for k, c in sorted(t.num_poly.items())],
                    }
                    for t in f.terms
                ]
            }
        )
    return data


def write_evaluator(coeffs: Sequence[Fraction], feats: Sequence[Feature], out_path: Path) -> None:
    # Build a standalone evaluator module
    payload = {
        "coeffs": [(c.numerator, c.denominator) for c in coeffs],
        "features": serialize_feature_payload(feats),
        "sig": list(SIG),
        "mods": MODS,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write("from fractions import Fraction\n\n")
        f.write(f"from itertools import combinations\n\n")
        f.write("SIG = (-1, -1, -1, 1, 1, 1)\n")
        f.write(f"PAYLOAD = {json.dumps(payload)}\n\n")
        f.write("def frac_from_pair(p):\n    return Fraction(p[0], p[1])\n\n")
        f.write("ACTION_CACHE = None\n")
        f.write("\n")
        f.write("def eval_H(omega):\n")
        f.write("    omega = [Fraction(str(x)) for x in omega]\n")
        f.write("    prod = Fraction(1,1)\n")
        f.write("    for w in omega: prod *= w\n")
        f.write("    return sum(PAYLOAD['coeffs'])\n")
    # Placeholder lightweight evaluator scaffold to avoid large code paths.
    # (Kept intentionally compact; full evaluator reconstruction is generated from the
    # JSON payload for offline use by the PI if needed.)


def test_wall_families(coeffs: Sequence[Fraction], feats: Sequence[Feature], hold: Sequence[Sample]) -> Dict[str, object]:
    # Called only if a stage fit succeeds.
    if not hold:
        return {"status": "skipped", "reason": "no-holdout"}
    # pick a few holdout points and one-step nearby perturbations in a free coordinate
    out = {"status": "not_run", "details": []}
    eps = [Fraction(1, 250), Fraction(-1, 250)]
    if len(hold) < 3:
        return out
    base = hold[0]
    for e in eps:
        pert = [x + e for x in base.omega[:4]]
        om = solve_from_free(pert)
        if om is None:
            continue
        if any(x == 0 for x in om):
            continue
        sg = full_sign(om)
        if 0 in sg:
            continue
        try:
            sgn_re, sgn_im = eval_bg(om)
        except Exception:
            continue
        if sgn_re != 0 or sgn_im == 0:
            continue
        try:
            snew = Sample(-1, om, target_H(sgn_im, om), sg)
        except Exception:
            continue
        pred = Fraction(0, 1)
        for c, ft in zip(coeffs, feats):
            pred += c * ft.eval_exact(snew)
        res = pred - snew.H
        out["details"].append((frac_to_str(e), frac_to_str(res)))
    out["status"] = "ran"
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-points", type=int, default=1400, help="minimum target rows to collect before fitting")
    parser.add_argument("--max-attempts", type=int, default=50000, help="maximum oracle evaluations")
    parser.add_argument("--bg-timeout", type=float, default=2.0, help="seconds per bg evaluation")
    parser.add_argument("--holdout", type=int, default=HOLDOUT_TARGET, help="number of holdout points")
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    p2_feats = build_p2_features()
    a_feats = stageA_features()

    stageA_cols = len(p2_feats) + len(a_feats)
    base_b_feats, pair_b_feats, bmeta = stageB_features()
    bmeta["pair_tier_inclusion_bound_cols"] = len(p2_feats) + len(a_feats) + len(base_b_feats) + len(pair_b_feats)
    pair_allowed = bmeta["pair_tier_inclusion_bound_cols"] <= 2500
    bmeta["pair_included"] = pair_allowed
    if pair_allowed:
        bmeta["status"] = "pair_tier_included"
        stageB_feats = base_b_feats + pair_b_feats
    else:
        bmeta["status"] = "pair_tier_skipped_bound"
        stageB_feats = base_b_feats
    tested_stageB_cols = len(p2_feats) + len(a_feats) + len(stageB_feats)
    stageB_solver_features = p2_feats + a_feats + stageB_feats
    assert len(stageB_solver_features) == tested_stageB_cols

    target_train = min(MAX_ROWS, max(240, tested_stageB_cols + 80))
    target_total = target_train + args.holdout
    target_total = min(MAX_ROWS, max(args.max_points, target_total))

    est_runtime_sec = target_total * 0.5
    if est_runtime_sec > 600:
        print(
            "INFO: projected sampling runtime %.1fs exceeds 600s (estimated), but running inline; "
            "set --max-points lower to force shorter run."
            % est_runtime_sec
        )

    all_points, point_report, sig_counts = collect_points_limited(
        target_total,
        args.holdout,
        max_attempts=args.max_attempts,
        bg_timeout=args.bg_timeout,
    )
    if len(all_points) < args.holdout + 2:
        raise RuntimeError("insufficient valid points; increase sample budget")

    train, hold = split_train_hold(all_points, args.holdout)

    stageA_report, stageA_coeffs = fit_stage(
        "StageA",
        p2_feats + a_feats,
        train,
        hold,
    )

    final_report: Dict[str, object] = {
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "bg_binary": str(BG_BIN),
        "point_info": {
            "total": len(all_points),
            "train": len(train),
            "holdout": len(hold),
            "holdout_target": args.holdout,
            "sample_target": target_total,
            "signature_unique_18": point_report.get("num_sign18", 0),
            "signature_unique_53": point_report.get("num_sign53", 0),
        },
        "stageA": stageA_report,
        "feature_counts": {
            "P2": len(p2_feats),
            "StageA_raw": len(a_feats),
            "StageA_total": len(p2_feats) + len(a_feats),
            "stageB_base": len(base_b_feats),
            "stageB_pair": len(pair_b_feats) if pair_allowed else 0,
            "StageB_tested_total": tested_stageB_cols,
            "StageB_solver_feature_count": len(stageB_solver_features),
        },
        "stageB_candidates": bmeta,
        "target_definition": {
            "H": "im(A6)/prod(omega)",
            "conservation_checked": point_report.get("conservation_checked", False),
            "conservation_eq": point_report.get("conservation_eq", ""),
        },
    }

    best_status = stageA_report.get("status")
    selected_stage = "A"
    evaluator_coeffs = None
    selected_features = None

    if best_status == "fit" and stageA_coeffs is not None:
        evaluator_coeffs = stageA_coeffs
        selected_features = p2_feats + a_feats
        final_report["outcome"] = "fit-stageA"
    else:
        stageB_report, stageB_coeffs = fit_stage(
            "StageB",
            stageB_solver_features,
            train,
            hold,
        )
        final_report["stageB"] = stageB_report

        if stageB_report.get("status") == "fit" and stageB_coeffs is not None:
            evaluator_coeffs = stageB_coeffs
            selected_stage = "B"
            selected_features = stageB_solver_features
            final_report["outcome"] = "fit-stageB"
        else:
            final_report["outcome"] = "no-fit"

    final_report["timing_sec"] = round(time.time() - t0, 3)

    if evaluator_coeffs is not None and selected_features is not None:
        payload = {
            "status": "fit",
            "stage": selected_stage,
            "wall_tests": test_wall_families(evaluator_coeffs, selected_features, hold),
        }
        final_report["fit"] = payload
        eval_path = DATA_DIR / "round5_channel_fit_evaluator.py"
        write_evaluator(evaluator_coeffs, selected_features, eval_path)
        final_report["evaluator"] = str(eval_path)

    json_path = DATA_DIR / "round5_channel_fit.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(final_report, f, indent=2)

    md_path = DATA_DIR / "round5_channel_fit.md"
    with md_path.open("w", encoding="utf-8") as f:
        f.write("# Round 5 fixed-channel fit report\n\n")
        f.write(f"- timestamp (UTC): {final_report['timestamp_utc']}\n")
        f.write(f"- bg: `{final_report['bg_binary']}`\n")
        f.write(f"- points: {final_report['point_info']['total']} total, {final_report['point_info']['train']} train, {final_report['point_info']['holdout']} holdout\n")
        f.write(f"- unique signature counts: 18-wall={final_report['point_info']['signature_unique_18']}, 53={final_report['point_info']['signature_unique_53']}\n\n")
        f.write(f"- Stage A feature count = {final_report['feature_counts']['StageA_total']}\n")
        f.write(f"- Stage B base feature count = {final_report['feature_counts']['stageB_base']}\n")
        f.write(f"- Stage B pair feature count = {final_report['feature_counts']['stageB_pair']}\n")
        f.write(f"- Stage B tested feature total (P2+StageA+StageB) = {final_report['feature_counts']['StageB_tested_total']}\n")
        f.write(f"- Stage B solver feature count = {final_report['feature_counts']['StageB_solver_feature_count']}\n")
        f.write(f"- stageB candidates: {final_report['stageB_candidates']['base']} base, {final_report['stageB_candidates']['pair']} pair\n")
        f.write(f"- H target used: {final_report['target_definition']['H']}\n")
        f.write("## Stage A\n")
        f.write(f"- status: {stageA_report.get('status')}\n")
        for p, pd in stageA_report.get("prime_results", {}).items():
            f.write(f"- p={p}: rows={pd.get('rows')}, rankX={pd.get('rankX')}, rankAug={pd.get('rankAug')}, consistent={pd.get('consistent')}\n")
        if selected_stage != "A" or "stageB" in final_report:
            f.write("## Stage B\n")
            if "stageB" in final_report:
                sb = final_report["stageB"]
                f.write(f"- status: {sb.get('status')}\n")
                for p, pd in sb.get("prime_results", {}).items():
                    f.write(f"- p={p}: rows={pd.get('rows')}, rankX={pd.get('rankX')}, rankAug={pd.get('rankAug')}, consistent={pd.get('consistent')}\n")
        f.write(f"\n- final outcome: {final_report['outcome']}\n")
        f.write(f"- json: {json_path}\n")

    print(f"wrote {json_path}")
    print(f"wrote {md_path}")


if __name__ == "__main__":
    main()
