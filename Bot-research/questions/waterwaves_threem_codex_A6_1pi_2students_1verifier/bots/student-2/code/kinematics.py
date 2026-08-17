
from collections import namedtuple
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Dict, List, Sequence, Tuple
import re
import subprocess

SIGMA = (-1, -1, -1, 1, 1, 1)
MINUS_IDX = (0, 1, 2)
PLUS_IDX = (3, 4, 5)


def parse_fraction(text: str) -> Fraction:
    t = text.strip()
    if not t:
        raise ValueError("empty rational token")
    if t[0] == "+":
        t = t[1:]
    if "/" in t:
        num, den = t.split("/")
        return Fraction(int(num), int(den))
    return Fraction(int(t), 1)


def fraction_to_str(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _fmt_list(values: Sequence[Fraction]) -> str:
    return ",".join(fraction_to_str(v) for v in values)


class KinematicsPoint:
    """Immutable exact kinematics point in the fixed ordering
    (-a, b, c, d, e, -f) with sigma=(-,-,-,+,+,+)."""

    def __init__(self, b, c, d, e):
        self.b = Fraction(b)
        self.c = Fraction(c)
        self.d = Fraction(d)
        self.e = Fraction(e)

        S = self.b + self.c + self.d + self.e
        if S == 0:
            raise ValueError("degenerate S=0")
        r = self.b * self.c - self.d * self.e
        self.a = self.d + self.e + r / S
        self.f = self.b + self.c - r / S

        self.omega = (-self.a, self.b, self.c, self.d, self.e, -self.f)

        self.pair_q: Dict[str, Fraction] = {}
        for m in MINUS_IDX:
            for p in PLUS_IDX:
                self.pair_q[f"q_{m+1}_{p+1}"] = self.omega[p] * self.omega[p] - self.omega[m] * self.omega[m]

        self.triple_q: Dict[str, Fraction] = {}
        for m in MINUS_IDX:
            for p, q in combinations(PLUS_IDX, 2):
                self.triple_q[f"q_{m+1}_{p+1}{q+1}"] = (
                    self.omega[p] * self.omega[p] + self.omega[q] * self.omega[q] - self.omega[m] * self.omega[m]
                )

        self.delta = Fraction(1, 1)
        for m in MINUS_IDX:
            for p in PLUS_IDX:
                self.delta *= self.omega[m] + self.omega[p]

    def sorted_magnitude_word(self) -> Tuple[str, bool, List[int]]:
        entries = [(i, abs(w * w)) for i, w in enumerate(self.omega)]
        sorted_entries = sorted(entries, key=lambda t: (t[1], t[0]), reverse=True)
        strict = all(
            sorted_entries[i][1] != sorted_entries[i + 1][1]
            for i in range(len(sorted_entries) - 1)
        )
        signs = ["+" if SIGMA[i] > 0 else "-" for i, _ in sorted_entries]
        order = [i for i, _ in sorted_entries]
        return "".join(signs), strict, order

    def momentum_subset_signs(self) -> str:
        terms = [Fraction(si, 1) * w * w for si, w in zip(SIGMA, self.omega)]
        bits: List[str] = []
        for mask in range(1, (1 << len(terms)) - 1):
            s = Fraction(0, 1)
            for i, v in enumerate(terms):
                if mask & (1 << i):
                    s += v
            if s == 0:
                bits.append("0")
            else:
                bits.append("+" if s > 0 else "-")
        return "".join(bits)

    def conservation_checks(self) -> Dict[str, object]:
        sum_omega = sum(self.omega)
        sum_momentum = sum(si * w * w for si, w in zip(SIGMA, self.omega))
        return {
            "sum_omega": sum_omega,
            "sum_omega_ok": sum_omega == 0,
            "sum_momentum": sum_momentum,
            "sum_momentum_ok": sum_momentum == 0,
        }

    def pair_sign_pattern(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        keys: List[str] = []
        signs: List[str] = []
        for m in MINUS_IDX:
            for p in PLUS_IDX:
                key = f"q_{m+1}_{p+1}"
                value = self.pair_q[key]
                keys.append(key)
                signs.append("0" if value == 0 else "+" if value > 0 else "-")
        return tuple(signs), tuple(keys)

    def triple_sign_pattern(self) -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
        keys: List[str] = []
        signs: List[str] = []
        for m in MINUS_IDX:
            for p, q in combinations(PLUS_IDX, 2):
                key = f"q_{m+1}_{p+1}{q+1}"
                value = self.triple_q[key]
                keys.append(key)
                signs.append("0" if value == 0 else "+" if value > 0 else "-")
        return tuple(signs), tuple(keys)

    def is_generic(self, require_nonzero=True) -> bool:
        checks = self.conservation_checks()
        if not checks["sum_omega_ok"] or not checks["sum_momentum_ok"]:
            return False
        if require_nonzero and not self.sorted_magnitude_word()[1]:
            return False
        if require_nonzero:
            if any(v == 0 for v in self.pair_q.values()):
                return False
            if any(v == 0 for v in self.triple_q.values()):
                return False
        return True

    def as_json_record(self) -> Dict[str, object]:
        pair_signs, pair_keys = self.pair_sign_pattern()
        triple_signs, triple_keys = self.triple_sign_pattern()
        word, strict, order = self.sorted_magnitude_word()
        checks = self.conservation_checks()
        return {
            "b": fraction_to_str(self.b),
            "c": fraction_to_str(self.c),
            "d": fraction_to_str(self.d),
            "e": fraction_to_str(self.e),
            "S": fraction_to_str(self.b + self.c + self.d + self.e),
            "r": fraction_to_str(self.b * self.c - self.d * self.e),
            "a": fraction_to_str(self.a),
            "f": fraction_to_str(self.f),
            "omega": [fraction_to_str(x) for x in self.omega],
            "sorted_word": word,
            "sorted_word_strict": strict,
            "sorted_order": order,
            "pair_keys": list(pair_keys),
            "pair_signs": list(pair_signs),
            "pair_q": {k: fraction_to_str(v) for k, v in self.pair_q.items()},
            "triple_keys": list(triple_keys),
            "triple_signs": list(triple_signs),
            "triple_q": {k: fraction_to_str(v) for k, v in self.triple_q.items()},
            "delta": fraction_to_str(self.delta),
            "subset_signature": self.momentum_subset_signs(),
            "sum_omega": fraction_to_str(checks["sum_omega"]),
            "sum_momentum": fraction_to_str(checks["sum_momentum"]),
            "is_strict": strict,
        }


BGResult = namedtuple("BGResult", ["n", "sigma", "omega", "amp_re", "amp_im", "command", "stdout"])


class BGOracleError(RuntimeError):
    pass


class BGOracle:
    """Wrapper for the local exact bg.cpp binary."""

    OMEGA_RE = re.compile(r"omega\s*=\s*\{([^}]*)\}")
    AMP_RE = re.compile(r"A_(\d+)\s*=\s*\(([^)]*)\)\s*\+\s*i\s*\(([^)]*)\)")
    PURE_IM_RE = re.compile(r"A_(\d+)\s*=\s*i\s*\*\s*\(([^)]*)\)")

    def __init__(self, binary_path: str = "bg", default_sigma=None):
        self.binary_path = str(Path(binary_path))
        self.default_sigma = tuple(int(x) for x in (default_sigma if default_sigma is not None else SIGMA))
        self._cache: Dict[tuple, BGResult] = {}

    @staticmethod
    def _fmt(vals: Sequence[Fraction]) -> str:
        return _fmt_list(vals)

    def _run(self, args: Sequence[str], timeout: int = 20) -> str:
        cmd = [self.binary_path] + list(args)
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        except FileNotFoundError as exc:
            raise BGOracleError(f"bg executable not found: {self.binary_path}") from exc
        except subprocess.TimeoutExpired as exc:
            raise BGOracleError(f"bg timed out after {timeout}s") from exc
        if proc.returncode != 0:
            raise BGOracleError(f"bg failed ({proc.returncode}): {proc.stderr.strip()}")
        return proc.stdout

    @classmethod
    def _parse_fraction(cls, token: str) -> Fraction:
        return parse_fraction(token)

    def _parse_output(self, text: str, n: int) -> BGResult:
        m_omega = self.OMEGA_RE.search(text)
        if not m_omega:
            raise BGOracleError("failed parsing omega from BG output")
        omega_raw = [part.strip() for part in m_omega.group(1).split(",") if part.strip()]
        if len(omega_raw) != n:
            raise BGOracleError(f"expected {n} omegas, got {len(omega_raw)}")
        omega = tuple(self._parse_fraction(v) for v in omega_raw)

        m_complex = self.AMP_RE.search(text)
        m_pure = self.PURE_IM_RE.search(text)
        amp_re = Fraction(0, 1)
        amp_im = Fraction(0, 1)
        if m_complex:
            got_n = int(m_complex.group(1))
            if got_n != n:
                raise BGOracleError("amplitude index mismatch in BG output")
            amp_re = self._parse_fraction(m_complex.group(2))
            amp_im = self._parse_fraction(m_complex.group(3))
        elif m_pure:
            got_n = int(m_pure.group(1))
            if got_n != n:
                raise BGOracleError("amplitude index mismatch in BG output")
            amp_im = self._parse_fraction(m_pure.group(2))
        else:
            raise BGOracleError("failed parsing amplitude from BG output")
        return BGResult(n=n, sigma=self.default_sigma, omega=omega, amp_re=amp_re, amp_im=amp_im, command=tuple(), stdout=text)

    def solve_on_shell(self, free_w, sigma=None, g: int = 1, n: int = 6):
        if n != 6:
            raise BGOracleError("this implementation is configured for n=6")
        if len(free_w) != n - 2:
            raise BGOracleError(f"expected {n-2} free frequencies, got {len(free_w)}")

        sigma_tuple = tuple(int(x) for x in (sigma if sigma is not None else self.default_sigma))
        if len(sigma_tuple) != n:
            raise BGOracleError("sigma length mismatch")

        key = (
            "shell",
            tuple(self._normalize_token(x) for x in free_w),
            sigma_tuple,
            n,
            g,
        )
        if key in self._cache:
            return self._cache[key]

        args = [
            "-n",
            str(n),
            "-w",
            self._fmt([Fraction(x) for x in free_w]),
            "-s",
            ",".join(str(int(x)) for x in sigma_tuple),
            "-g",
            str(g),
        ]
        out = self._run(args)
        parsed = self._parse_output(out, n)
        result = BGResult(
            n=n,
            sigma=sigma_tuple,
            omega=parsed.omega,
            amp_re=parsed.amp_re,
            amp_im=parsed.amp_im,
            command=(self.binary_path,) + tuple(args),
            stdout=out,
        )
        self._cache[key] = result
        return result

    @staticmethod
    def _normalize_token(x) -> str:
        if isinstance(x, Fraction):
            return fraction_to_str(x)
        return fraction_to_str(Fraction(x))

    def eval_with_omega(self, omega, sigma=None, g: int = 1):
        omega_tuple = tuple(Fraction(x) for x in omega)
        sigma_tuple = tuple(int(x) for x in (sigma if sigma is not None else self.default_sigma))
        if len(omega_tuple) != len(sigma_tuple):
            raise BGOracleError("omega and sigma length mismatch")

        key = (
            "amp",
            tuple(self._normalize_token(x) for x in omega_tuple),
            sigma_tuple,
            g,
        )
        if key in self._cache:
            return self._cache[key]

        ks: List[Fraction] = [Fraction(si, 1) * w * w / Fraction(g, 1) for si, w in zip(sigma_tuple, omega_tuple)]
        args = [
            "--amp",
            "-K",
            self._fmt(ks),
            "-W",
            self._fmt(omega_tuple),
            "-g",
            str(g),
        ]
        out = self._run(args)
        parsed = self._parse_output(out, len(omega_tuple))
        result = BGResult(
            n=len(omega_tuple),
            sigma=sigma_tuple,
            omega=omega_tuple,
            amp_re=parsed.amp_re,
            amp_im=parsed.amp_im,
            command=(self.binary_path,) + tuple(args),
            stdout=out,
        )
        self._cache[key] = result
        return result


def all_20_words_3plus3() -> List[str]:
    words = []
    for bits in range(1 << 6):
        if bin(bits).count("1") == 3:
            words.append("".join("+" if (bits >> i) & 1 else "-" for i in range(6)))
    return sorted(words)


def expected_pairwall_words() -> List[str]:
    return ["+-+--+", "+--++-", "+--+-+", "+---++", "-+++--", "-++-+-", "-++--+"]


def standard_point_from_params(b, c, d, e) -> KinematicsPoint:
    return KinematicsPoint(b, c, d, e)
