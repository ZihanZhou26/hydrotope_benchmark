"""Modular test: is P9 = B * prod_{all 9 minus-plus pairs}(w_i+w_j) a single global
symmetric polynomial in invariants (a=e1m, b=e2m=e2p, c=e3m, d=e3p)?
Solve the fit mod a large prime; validate on held-out points mod p."""
import random
from fractions import Fraction as Fr
import harness

P = 2147483647  # 2^31 - 1, prime
sg = [-1, -1, -1, 1, 1, 1]


def modinv(x):
    return pow(x % P, P - 2, P)


def fr_mod(q):
    q = Fr(q)
    return (q.numerator % P) * modinv(q.denominator) % P


def prod_all(om):
    p = Fr(1)
    for i in range(3):
        for j in range(3, 6):
            p *= (om[i] + om[j])
    return p


def invs(om):
    m = om[:3]; pl = om[3:]
    a = sum(m)
    b = m[0] * m[1] + m[0] * m[2] + m[1] * m[2]
    c = m[0] * m[1] * m[2]
    d = pl[0] * pl[1] * pl[2]
    return a, b, c, d


def gather(npts, seed=31):
    rng = random.Random(seed)
    pts = []
    while len(pts) < npts:
        fw = [Fr(rng.randint(-20, 20), rng.randint(1, 3)) for _ in range(4)]
        try:
            r = harness.onshell(6, fw, sg)
            om = r["omega"]; B = r["A_im"]
            pa = prod_all(om)
            if pa == 0:
                continue
            a, b, c, d = invs(om)
            pts.append((fr_mod(a), fr_mod(b), fr_mod(c), fr_mod(d), fr_mod(B * pa)))
        except Exception:
            continue
    return pts


def solve_modp(A, b):
    n = len(A); m = len(A[0])
    rows = [A[i][:] + [b[i]] for i in range(n)]
    piv = []; r = 0
    for c in range(m):
        sel = next((i for i in range(r, n) if rows[i][c] % P != 0), None)
        if sel is None:
            continue
        rows[r], rows[sel] = rows[sel], rows[r]
        inv = modinv(rows[r][c])
        rows[r] = [(v * inv) % P for v in rows[r]]
        for i in range(n):
            if i != r and rows[i][c] % P != 0:
                f = rows[i][c]
                rows[i] = [(rows[i][t] - f * rows[r][t]) % P for t in range(m + 1)]
        piv.append(c); r += 1
        if r == m:
            break
    for i in range(r, n):
        if rows[i][m] % P != 0 and all(rows[i][t] % P == 0 for t in range(m)):
            return None, "INCONSISTENT", r
    sol = {c: rows[i][m] for i, c in enumerate(piv)}
    return [sol.get(c, 0) for c in range(m)], "ok", r


def run(wdeg):
    monos = [(i, j, k, l) for i in range(wdeg + 1) for j in range(wdeg // 2 + 1)
             for k in range(wdeg // 3 + 1) for l in range(wdeg // 3 + 1)
             if i + 2 * j + 3 * k + 3 * l == wdeg]
    pts = gather(len(monos) + 80)
    ntr = len(monos) + 40
    def feat(a, b, c, d):
        return [(pow(a, i, P) * pow(b, j, P) % P * pow(c, k, P) % P * pow(d, l, P)) % P
                for (i, j, k, l) in monos]
    A = [feat(*p[:4]) for p in pts[:ntr]]
    bb = [p[4] for p in pts[:ntr]]
    sol, stat, rank = solve_modp(A, bb)
    print(f"wdeg={wdeg}: monomials={len(monos)} rank={rank} fit={stat}")
    if sol is None:
        print("   -> P9 is NOT a global polynomial at this degree (inconsistent mod p)")
        return False
    bad = 0
    for p in pts[ntr:]:
        val = sum(sol[t] * feat(*p[:4])[t] for t in range(len(monos))) % P
        if val != p[4] % P:
            bad += 1
    print(f"   held-out: {bad}/{len(pts)-ntr} mismatches mod p",
          "=> GLOBAL POLYNOMIAL" if bad == 0 else "=> NOT global")
    return bad == 0


if __name__ == "__main__":
    for wd in [17, 16, 18, 15, 19, 13, 14, 20]:
        try:
            if run(wd):
                print(f"*** P9 is a global symmetric polynomial of weighted degree {wd} ***")
                break
        except Exception as e:
            print(f"wdeg={wd}: error {e}")
