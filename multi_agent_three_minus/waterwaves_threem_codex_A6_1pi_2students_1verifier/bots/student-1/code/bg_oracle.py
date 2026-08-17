from collections import namedtuple
from fractions import Fraction
from pathlib import Path
import re
import subprocess


def parse_fraction(text):
    t = text.strip()
    if not t:
        raise ValueError('empty rational token')
    if t[0] == '+':
        t = t[1:]
    if '/' in t:
        num, den = t.split('/')
        return Fraction(int(num), int(den))
    return Fraction(int(t), 1)


def fraction_to_str(q):
    if q.denominator == 1:
        return str(q.numerator)
    return '%d/%d' % (q.numerator, q.denominator)


class BGOracleError(RuntimeError):
    pass


BGResult = namedtuple('BGResult', ['n', 'sigma', 'omega', 'amp_re', 'amp_im', 'command', 'stdout'])


class BGOracle(object):
    """Wrapper for the local exact bg.cpp binary."""

    OMEGA_RE = re.compile(r"omega\s*=\s*\{([^}]*)\}")
    AMP_RE = re.compile(r"A_(\d+)\s*=\s*\(([^)]*)\)\s*\+\s*i\s*\(([^)]*)\)")
    PURE_IM_RE = re.compile(r"A_(\d+)\s*=\s*i\s*\*\s*\(([^)]*)\)")

    def __init__(self, binary_path='bg', default_sigma=None):
        self.binary_path = str(Path(binary_path))
        self.default_sigma = tuple(default_sigma) if default_sigma is not None else (-1, -1, -1, 1, 1, 1)
        self._cache = {}

    def _run(self, args, timeout=15):
        cmd = [self.binary_path] + args
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=timeout)
        except FileNotFoundError:
            raise BGOracleError('bg executable not found: %s' % self.binary_path)
        except subprocess.TimeoutExpired:
            raise BGOracleError('bg timed out after %ss' % timeout)
        if proc.returncode != 0:
            raise BGOracleError('bg failed (%s): %s' % (proc.returncode, proc.stderr.strip()))
        return proc.stdout

    @staticmethod
    def _fmt_list(vals):
        return ','.join(str(v) for v in vals)

    def _parse(self, text, n):
        m_omega = self.OMEGA_RE.search(text)
        if not m_omega:
            raise BGOracleError('Failed parsing omega from output')
        omega_raw = [part.strip() for part in m_omega.group(1).split(',') if part.strip()]
        if len(omega_raw) != n:
            raise BGOracleError('Omega count mismatch: expected %d got %d' % (n, len(omega_raw)))
        omega = tuple(parse_fraction(v) for v in omega_raw)

        m_im = self.AMP_RE.search(text)
        m_im_only = self.PURE_IM_RE.search(text)
        amp_re = Fraction(0, 1)
        amp_im = Fraction(0, 1)
        if m_im:
            g = int(m_im.group(1))
            if g != n:
                raise BGOracleError('Amplitude index mismatch in output')
            amp_re = parse_fraction(m_im.group(2))
            amp_im = parse_fraction(m_im.group(3))
        elif m_im_only:
            g = int(m_im_only.group(1))
            if g != n:
                raise BGOracleError('Amplitude index mismatch in output')
            amp_im = parse_fraction(m_im_only.group(2))
        else:
            raise BGOracleError('Failed parsing amplitude from output')

        return BGResult(n=n, sigma=tuple(), omega=omega, amp_re=amp_re, amp_im=amp_im, command=tuple(), stdout=text)

    def solve_on_shell(self, free_w, n=6, sigma=None, g=1):
        if n != 6:
            raise BGOracleError('This wrapper is configured for n=6')
        if len(free_w) != n - 2:
            raise BGOracleError('n=%d expects %d free frequencies' % (n, n - 2))
        sigma_tuple = tuple(int(x) for x in (sigma if sigma is not None else self.default_sigma))
        if len(sigma_tuple) != n:
            raise BGOracleError('sigma length mismatch')

        key = ('shell', tuple(free_w), n, sigma_tuple, g)
        if key in self._cache:
            return self._cache[key]

        w_str = self._fmt_list([fraction_to_str(Fraction(x)) for x in free_w])
        s_str = self._fmt_list([int(x) for x in sigma_tuple])
        out = self._run(["-n", str(n), "-w", w_str, "-s", s_str, "-g", str(g)])
        res = self._parse(out, n)
        parsed = BGResult(n=n, sigma=sigma_tuple, omega=res.omega, amp_re=res.amp_re, amp_im=res.amp_im,
                          command=(self.binary_path, '-n', str(n), '-w', w_str, '-s', s_str, '-g', str(g)), stdout=out)
        self._cache[key] = parsed
        return parsed

    def eval_with_amp(self, omega, sigma, g=1, n=None):
        if n is None:
            n = len(omega)
        omega_tuple = tuple(omega)
        sigma_tuple = tuple(int(x) for x in sigma)
        if len(omega_tuple) != n or len(sigma_tuple) != n:
            raise BGOracleError('omega/sigma length mismatch')

        key = ('amp', omega_tuple, sigma_tuple, g)
        if key in self._cache:
            return self._cache[key]

        w_str = self._fmt_list([fraction_to_str(Fraction(x)) for x in omega_tuple])
        k = []
        gg = Fraction(g, 1)
        for wi, si in zip(omega_tuple, sigma_tuple):
            k.append(Fraction(si, 1) * wi * wi / gg)
        k_str = self._fmt_list([fraction_to_str(v) for v in k])

        out = self._run(["--amp", "-K", k_str, "-W", w_str, "-g", str(g)])
        res = self._parse(out, n)
        parsed = BGResult(n=n, sigma=sigma_tuple, omega=tuple(omega_tuple), amp_re=res.amp_re, amp_im=res.amp_im,
                          command=(self.binary_path, '--amp', '-K', k_str, '-W', w_str, '-g', str(g)), stdout=out)
        self._cache[key] = parsed
        return parsed
