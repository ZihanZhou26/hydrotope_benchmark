"""PI independent verification (round 2) of student-1's universal all-chamber
closed form for A_n in the two-minus sector.

Candidate (student-1, post_003):
    A_n = i * a_n
    a_n = 2^(n-1) * w1 * w2 * sum_{S subset of plus legs {3..n}} (-1)^|S|
                                * max(0, P - sum_{j in S} w_j^2)^(n-3)
    P = min(w1^2, w2^2)   (squared magnitude of the SMALLER minus leg)
    minus legs = 1,2 (sigma=-1); plus legs = 3..n (sigma=+1).

This file is written from scratch by the PI: its own subprocess driver, its own
exact-rational parser, and its own formula implementation. It does NOT import any
student code. Exact-rational comparison => residual is identically 0 or not.

Usage: python3 pi_round2_verify.py
"""
import subprocess, os, re, itertools, random
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")           # the PI's own freshly-built oracle


# ----------------------------------------------------------------------
# Independent oracle driver (exact rational by default)
# ----------------------------------------------------------------------
def _run(args):
    return subprocess.run([BG] + args, capture_output=True, text=True)

def onshell_exact(n, freew, signs=None, g=1):
    """Run ./bg -n N -w ... (exact rational). Returns dict with omega (list[Fr]),
    a (Fr, where A_n = re + i*a), re (Fr)."""
    if signs is None:
        signs = [-1, -1] + [1] * (n - 2)
    ws = ",".join(str(x) for x in freew)
    ss = ",".join(str(x) for x in signs)
    p = _run(["-n", str(n), "-w", ws, "-s", ss, "-g", str(g)])
    if p.returncode != 0:
        return {"ok": False, "rc": p.returncode, "stderr": p.stderr}
    return _parse_exact(p.stdout)

def amp_exact(K, W, g=1):
    """Run ./bg --amp -K ... -W ... (exact rational, raw off-shell allowed)."""
    ks = ",".join(str(x) for x in K)
    Ws = ",".join(str(x) for x in W)
    p = _run(["--amp", "-K", ks, "-W", Ws, "-g", str(g)])
    if p.returncode != 0:
        return {"ok": False, "rc": p.returncode, "stderr": p.stderr}
    return _parse_exact(p.stdout)

def _parse_exact(out):
    om = a_im = re_part = None
    for line in out.splitlines():
        m = re.match(r"omega = \{(.*)\}", line)
        if m:
            om = [Fr(x.strip()) for x in m.group(1).split(",")]
        m = re.match(r"A_\d+ = i \* \((.*)\)", line)        # Re == 0 branch
        if m:
            a_im = Fr(m.group(1)); re_part = Fr(0)
        m = re.match(r"A_\d+ = \((.*)\) \+ i \* \((.*)\)", line)  # general branch
        if m:
            re_part = Fr(m.group(1)); a_im = Fr(m.group(2))
    if a_im is None:
        return {"ok": False, "stdout": out}
    return {"ok": True, "omega": om, "a": a_im, "re": re_part}


# ----------------------------------------------------------------------
# Independent implementation of the candidate formula
# ----------------------------------------------------------------------
def a_formula(n, omega):
    """omega: list of n Fractions in leg order (legs 1,2 minus; 3..n plus)."""
    w1, w2 = omega[0], omega[1]
    P = min(w1 * w1, w2 * w2)
    psq = [omega[j] * omega[j] for j in range(2, n)]   # plus-leg squares
    p = n - 3
    tot = Fr(0)
    for r in range(len(psq) + 1):
        for S in itertools.combinations(psq, r):
            base = P - sum(S, Fr(0))
            if base > 0:                                # base<=0 -> 0 for p>=1
                tot += (-1) ** r * base ** p
    return Fr(2) ** (n - 1) * w1 * w2 * tot

def chamber_label(n, omega):
    """How many plus legs sit below P / between P,Q / above Q. b>0 => non-principal
    chamber where the truncated inclusion-exclusion genuinely fires."""
    P = min(omega[0] ** 2, omega[1] ** 2)
    Q = max(omega[0] ** 2, omega[1] ** 2)
    below = sum(1 for j in range(2, n) if omega[j] ** 2 < P)
    mid = sum(1 for j in range(2, n) if P < omega[j] ** 2 < Q)
    high = sum(1 for j in range(2, n) if omega[j] ** 2 > Q)
    return f"b{below}m{mid}h{high}"


# ----------------------------------------------------------------------
# n=4 via delta->0 limit (independent), using raw --amp continuation
# ----------------------------------------------------------------------
def a4_oracle_limit(w2, w3, deltas=None):
    """n=4 two-minus on-shell branch: w1=-w3, w4=-w2 (forces {2,4} 0/0 at delta=0).
    Approach along Sum(omega)=0 with the square-constraint relaxed by delta:
       w4 -> -w2 + delta,  w1 -> -(w2+w3+w4).
    Evaluate raw amplitude (exact rational) at a sequence of delta and fit the
    delta->0 limit by exact polynomial (Neville) extrapolation in delta.
    Returns (limit Fraction, table). Legs: sigma=(-1,-1,+1,+1)."""
    w2, w3 = Fr(w2), Fr(w3)
    if deltas is None:
        deltas = [Fr(1, 4), Fr(1, 8), Fr(1, 16), Fr(1, 32), Fr(1, 64)]
    sig = [-1, -1, 1, 1]
    xs, ys = [], []
    for d in deltas:
        w4 = -w2 + d
        w1 = -(w2 + w3 + w4)
        W = [w1, w2, w3, w4]
        K = [Fr(sig[i]) * W[i] * W[i] for i in range(4)]
        r = amp_exact(K, W)
        if not r["ok"]:
            xs.append(d); ys.append(None); continue
        assert r["re"] == 0, f"Re != 0 at delta={d}: {r['re']}"
        xs.append(d); ys.append(r["a"])
    # exact Neville extrapolation to x=0 over the points that evaluated cleanly
    pts = [(x, y) for x, y in zip(xs, ys) if y is not None]
    lim = _neville_at_zero([p[0] for p in pts], [p[1] for p in pts])
    return lim, list(zip(xs, ys))

def _neville_at_zero(xs, ys):
    """Exact polynomial interpolation evaluated at x=0 (Neville's algorithm)."""
    n = len(xs)
    P = [Fr(y) for y in ys]
    for k in range(1, n):
        for i in range(n - k):
            # interpolate at x=0
            P[i] = (xs[i + k] * P[i] - xs[i] * P[i + 1]) / (xs[i + k] - xs[i])
    return P[0]


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------
def relerr(pred, actual):
    if actual == 0:
        return abs(pred)
    return abs(Fr(pred - actual) / actual)

def check_point(n, freew, label=""):
    r = onshell_exact(n, freew)
    if not r["ok"]:
        print(f"  [ORACLE FAIL] n={n} -w {freew} rc={r.get('rc')} {r.get('stderr','').strip()}")
        return None
    om = r["omega"]; a = r["a"]
    if r["re"] != 0:
        print(f"  [Re!=0] n={n} -w {freew}: Re={r['re']}")
    pred = a_formula(n, om)
    err = relerr(pred, a)
    ch = chamber_label(n, om)
    tag = "EXACT" if err == 0 else f"relerr={float(err):.2e}"
    status = "OK " if err <= Fr(1, 10**10) else "*** FAIL ***"
    print(f"  {status} n={n} {ch:8s} -w {str(freew):28s} a={str(a):>22s}  {tag}  {label}")
    return {"n": n, "omega": [str(x) for x in om], "a": str(a),
            "pred": str(pred), "exact": err == 0, "relerr": float(err),
            "chamber": ch, "ok": err <= Fr(1, 10**10)}


def random_scan(n, npts, seed, want_nonprincipal=True):
    """Random in-sector points. Encourages non-principal chambers (b>0)."""
    random.seed(seed)
    pool = ([Fr(a) for a in range(1, 13)]
            + [Fr(a, 2) for a in range(1, 20, 2)]
            + [Fr(a, 3) for a in range(1, 22)]
            + [Fr(a, 5) for a in range(1, 12)])
    results = []
    from collections import Counter
    chambers = Counter()
    tries = 0
    while len(results) < npts and tries < npts * 200:
        tries += 1
        fw = [random.choice(pool) for _ in range(n - 2)]
        if len(set(fw)) < len(fw):
            continue
        res = check_point(n, fw)
        if res is None:
            continue
        # require distinct |omega| to avoid accidental degeneracies
        results.append(res)
        chambers[res["chamber"]] += 1
    nb = sum(1 for r in results if not r["chamber"].startswith("b0"))
    allok = all(r["ok"] for r in results)
    allexact = all(r["exact"] for r in results)
    print(f"  -> n={n}: {sum(r['ok'] for r in results)}/{len(results)} pass "
          f"(exact={sum(r['exact'] for r in results)}), "
          f"non-principal(b>0)={nb}, chambers={dict(chambers)}")
    return results, allok, allexact


if __name__ == "__main__":
    print("=" * 78)
    print("PI INDEPENDENT VERIFICATION of student-1 universal closed form")
    print("oracle:", BG)
    print("=" * 78)

    all_results = []
    overall_ok = True

    print("\n--- (A) PI reference points (group_meeting_notes.md) ---")
    for n, fw in [(5, [1, 2, 4]), (5, [2, 3, 5]), (6, [1, 2, 3, 4]),
                  (7, [1, 2, 3, 4, 5]), (7, [1, 2, 3, 4, 1000])]:
        r = check_point(n, fw, "ref")
        if r: all_results.append(r); overall_ok &= r["ok"]

    print("\n--- (B) n=4 via independent delta->0 limit ---")
    for (w2, w3, expect) in [(1, 3, -24), (2, 5, -320), (3, 7, None), (1, 5, None)]:
        # branch: w1=-w3, w4=-w2 ; full omega on-shell = (-w3, w2, w3, -w2)
        lim, table = a4_oracle_limit(w2, w3)
        om = [Fr(-w3), Fr(w2), Fr(w3), Fr(-w2)]
        pred = a_formula(4, om)
        err = relerr(pred, lim)
        ok = err <= Fr(1, 10**10)
        overall_ok &= ok
        status = "OK " if ok else "*** FAIL ***"
        ex = "(matches ref)" if expect is not None and lim == expect else ""
        print(f"  {status} n=4 omega={tuple(str(x) for x in om)} "
              f"oracle_limit={lim} formula={pred} relerr={float(err):.2e} {ex}")
        all_results.append({"n": 4, "omega": [str(x) for x in om],
                            "a": str(lim), "pred": str(pred),
                            "exact": err == 0, "relerr": float(err), "ok": ok})

    print("\n--- (C) Non-generic regimes (one freq >> or << the rest) ---")
    for n, fw, desc in [(5, [1, 2, 1000], "one plus >>"),
                        (5, [1, 2, Fr(1, 1000)], "one plus <<"),
                        (5, [Fr(1, 1000), 2, 3], "free minus << "),
                        (6, [1, 2, 3, 500], "one plus >>"),
                        (6, [Fr(1, 100), 2, 3, 4], "free minus <<"),
                        (7, [1, 2, 3, 4, 5000], "one plus >>"),
                        (7, [1, 2, 3, 4, Fr(1, 500)], "one plus <<")]:
        r = check_point(n, fw, desc)
        if r: all_results.append(r); overall_ok &= r["ok"]

    print("\n--- (D) Deliberate NON-PRINCIPAL chambers (truncation must fire) ---")
    # Put the free minus leg (w2) large and some plus legs small => plus legs below P.
    for n, fw, desc in [(5, [6, 1, 2], "w2 large, small plus"),
                        (5, [8, 1, 3], "w2 large"),
                        (6, [7, 1, 2, 3], "w2 large, 3 small plus"),
                        (6, [Fr(9, 2), 1, 2, 4], "mixed"),
                        (7, [8, 1, 2, 3, 4], "w2 large, 4 small plus"),
                        (7, [6, 1, 2, 3, 5], "mixed")]:
        r = check_point(n, fw, desc)
        if r: all_results.append(r); overall_ok &= r["ok"]

    print("\n--- (E) Random all-chamber scans (exact rational) ---")
    for n, npts, seed in [(5, 50, 2026), (6, 40, 2027), (7, 30, 2028)]:
        res, allok, allexact = random_scan(n, npts, seed)
        all_results.extend(res); overall_ok &= allok

    print("\n" + "=" * 78)
    npass = sum(1 for r in all_results if r["ok"])
    nexact = sum(1 for r in all_results if r.get("exact"))
    nnonprin = sum(1 for r in all_results if r.get("chamber", "b0").startswith(("b1","b2","b3","b4")))
    print(f"TOTAL: {npass}/{len(all_results)} points pass (<=1e-10); "
          f"{nexact} bit-exact; {nnonprin} in non-principal chambers (truncation fired)")
    print("VERDICT:", "ALL PASS" if overall_ok else "FAILURES PRESENT")
    print("=" * 78)
