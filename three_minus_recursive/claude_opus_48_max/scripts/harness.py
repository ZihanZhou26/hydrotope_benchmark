"""harness.py — thin wrapper around the bg.cpp oracle.

Provides exact (GMP rational) and fast (long double) amplitude queries, parses
the oracle's output into exact fractions, and replicates the on-shell kinematic
solver so we always know the full frequency vector.

Sector under study: three-minus, sigma = (-1,-1,-1,+1,...,+1) (legs 1,2,3 minus).
But the harness is sector-agnostic; pass any sigma with sigma_1 + sigma_n = 0.
"""
import os, re, subprocess
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "..", "bg")
BG = os.path.abspath(BG)


def _run(args):
    out = subprocess.run([BG] + args, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"bg failed: {out.stderr}\nargs={args}")
    return out.stdout


def _parse_exact(text):
    """Parse exact-mode output -> (omega_list[Fraction], A_re Fraction, A_im Fraction)."""
    om = None
    Are = Fr(0)
    Aim = Fr(0)
    for line in text.splitlines():
        m = re.match(r"omega = \{(.*)\}", line)
        if m:
            om = [Fr(x.strip()) for x in m.group(1).split(",")]
        m = re.match(r"A_\d+ = (.*)", line)
        if m and "numeric" not in line:
            rhs = m.group(1)
            # forms: "i * (X)"  or  "(R) + i * (I)"
            mi = re.match(r"i \* \((.*)\)$", rhs)
            if mi:
                Aim = Fr(mi.group(1))
                Are = Fr(0)
            else:
                mr = re.match(r"\((.*)\) \+ i \* \((.*)\)$", rhs)
                if mr:
                    Are = Fr(mr.group(1))
                    Aim = Fr(mr.group(2))
                else:
                    raise ValueError(f"cannot parse A line: {rhs}")
    return om, Are, Aim


def _parse_double(text):
    om = None
    Are = Aim = 0.0
    for line in text.splitlines():
        m = re.match(r"omega = \{(.*)\}", line)
        if m:
            om = [float(eval_frac(x.strip())) for x in m.group(1).split(",")]
        m = re.match(r"A_\d+ \(double\) = (.*) \+ (.*) i", line)
        if m:
            Are = float(m.group(1))
            Aim = float(m.group(2))
    return om, Are, Aim


def eval_frac(s):
    return float(Fr(s))


def onshell(n, free_w, sigma, g=1, double=False):
    """On-shell query. free_w: n-2 free freqs (omega_2..omega_{n-1}).
    sigma: list of n signs. Returns dict with omega, A_re, A_im (Fraction or float)."""
    ws = ",".join(str(x) for x in free_w)
    ss = ",".join(str(int(s)) for s in sigma)
    args = ["-n", str(n), "-w", ws, "-s", ss, "-g", str(g)]
    if double:
        args = ["--double"] + args
        om, Are, Aim = _parse_double(_run(args))
    else:
        om, Are, Aim = _parse_exact(_run(args))
    return {"omega": om, "A_re": Are, "A_im": Aim}


def rawamp(K, W, g=1, double=False):
    """Raw amplitude for arbitrary kinematics. K, W: lists of n momenta/freqs."""
    ks = ",".join(str(x) for x in K)
    Ws = ",".join(str(x) for x in W)
    args = ["--amp", "-K", ks, "-W", Ws, "-g", str(g)]
    if double:
        args = ["--double"] + args
        om, Are, Aim = _parse_double(_run(args))
    else:
        om, Are, Aim = _parse_exact(_run(args))
    return {"omega": om, "A_re": Are, "A_im": Aim}


def solve_kinematics(n, free_w, sigma, g=1):
    """Replicate bg.cpp's on-shell solver in exact arithmetic.
    free_w are omega_2..omega_{n-1}; returns full omega list (Fractions)."""
    fw = [Fr(x) for x in free_w]
    sg = [Fr(int(s)) for s in sigma]
    s0 = sg[0]
    sumFree = sum(fw)
    sumSig = sum(sg[i + 1] * fw[i] * fw[i] for i in range(n - 2))
    wn = -(s0 * sumFree * sumFree + sumSig) / (Fr(2) * s0 * sumFree)
    w1 = -(sumFree + wn)
    W = [w1] + fw + [wn]
    K = [sg[i] * W[i] * W[i] / Fr(g) for i in range(n)]
    return W, K


if __name__ == "__main__":
    # smoke test: reproduce the two documented checks
    r = onshell(5, [2, 3, 5], [-1, 1, 1, 1, 1])
    print("one-minus n=5:", r["A_re"], "+ i*", r["A_im"], " (expect 0)")
    r = onshell(5, [2, 3, 5], [-1, -1, -1, 1, 1])
    print("three-minus n=5:", r["A_re"], "+ i*", r["A_im"], " (expect -25344 i)")
    W, K = solve_kinematics(5, [2, 3, 5], [-1, -1, -1, 1, 1])
    print("solved omega:", W)
    print("solved K   :", K)
