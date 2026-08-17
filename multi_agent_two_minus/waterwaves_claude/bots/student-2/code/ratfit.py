"""ratfit.py — reconstruct a_n as a SYMMETRIC RATIONAL function of blocks
   s = w1+w2, p = w1 w2, E3..E_{n-2} = elem. symm. of plus legs.
a_n = Num/Den, both homogeneous; deg(Num)-deg(Den)=2n-4. Search smallest deg(Den).
"""
import sys, itertools, random, math
from fractions import Fraction as F
import sympy as sp
from engine import build_onshell, Engine


def elem_sym(vals, k):
    if k == 0: return F(1)
    tot = F(0)
    for c in itertools.combinations(vals, k):
        pr = F(1)
        for x in c: pr *= x
        tot += pr
    return tot


def block_degs(N):
    return [1, 2] + list(range(3, (N-2)+1))   # s,p,E3,...,E_{N-2}


def block_names(N):
    return ['s', 'p'] + [f'E{k}' for k in range(3, (N-2)+1)]


def eval_blocks(N, omega):
    s = omega[1] + omega[2]
    p = omega[1] * omega[2]
    plus = [omega[i] for i in range(3, N+1)]
    Es = [elem_sym(plus, k) for k in range(3, (N-2)+1)]
    return [s, p] + Es


def monos_of_degree(degs, D):
    ranges = [range(0, D//degs[i] + 1) for i in range(len(degs))]
    out = []
    for exps in itertools.product(*ranges):
        if sum(exps[i]*degs[i] for i in range(len(degs))) == D:
            out.append(exps)
    return out


def amp_value(N, free_w):
    sigma = [-1, -1] + [1]*(N-2)
    W, K = build_onshell(N, free_w, sigma)
    E = Engine('frac'); re, im = E.BGAmplitude(N, K, W)
    assert re == 0, f"Re != 0: {re}"
    return im, {i: W[i] for i in range(1, N+1)}


def gen_points(N, npts, seed):
    rng = random.Random(seed)
    pts = []
    tries = 0
    while len(pts) < npts and tries < 20000:
        tries += 1
        fw = []
        used = set()
        ok = True
        while len(fw) < N-2:
            v = F(rng.randint(1, 40), rng.randint(1, 9))
            if v in used or v == 0: continue
            used.add(v); fw.append(v)
        try:
            a, omega = amp_value(N, fw)
        except Exception:
            continue
        b = eval_blocks(N, omega)
        pts.append((b, a, fw))
    return pts


def reconstruct(N, max_dD=6, seed=2024):
    degs = block_degs(N); names = block_names(N); D = 2*N-4
    for dD in range(0, max_dD+1):
        dN = dD + D
        Bn = monos_of_degree(degs, dN)
        Bd = monos_of_degree(degs, dD)
        nunk = len(Bn) + len(Bd)
        pts = gen_points(N, nunk + 15, seed + dD)
        # build matrix rows: sum c*Bn(pt) - a*sum d*Bd(pt) = 0
        rows = []
        for b, a, fw in pts:
            ar = sp.Rational(a.numerator, a.denominator)
            bb = [sp.Rational(x.numerator, x.denominator) for x in b]
            row = []
            for e in Bn:
                t = sp.Integer(1)
                for i, ee in enumerate(e): t *= bb[i]**ee
                row.append(t)
            for e in Bd:
                t = sp.Integer(1)
                for i, ee in enumerate(e): t *= bb[i]**ee
                row.append(-ar*t)
            rows.append(row)
        M = sp.Matrix(rows)
        ns = M.nullspace()
        if not ns:
            continue
        # prefer a null vector with nonzero denominator part
        for vec in ns:
            cN = vec[:len(Bn)]
            cD = vec[len(Bn):]
            if any(x != 0 for x in cD):
                return dict(dD=dD, Bn=Bn, Bd=Bd, cN=cN, cD=cD, names=names, degs=degs,
                            nullity=len(ns), pts=pts)
        # only polynomial solutions (denominator 0) -> treat as polynomial
        vec = ns[0]
        return dict(dD=dD, Bn=Bn, Bd=Bd, cN=vec[:len(Bn)], cD=vec[len(Bn):],
                    names=names, degs=degs, nullity=len(ns), pts=pts)
    return None


def build_expr(res):
    names = res['names']; syms = sp.symbols(names)
    num = sp.Integer(0)
    for e, c in zip(res['Bn'], res['cN']):
        t = c
        for i, ee in enumerate(e): t *= syms[i]**ee
        num += t
    den = sp.Integer(0)
    for e, c in zip(res['Bd'], res['cD']):
        t = c
        for i, ee in enumerate(e): t *= syms[i]**ee
        den += t
    return num, den, syms


if __name__ == '__main__':
    N = int(sys.argv[1])
    res = reconstruct(N)
    if not res:
        print("no reconstruction found"); sys.exit(1)
    num, den, syms = build_expr(res)
    expr = sp.cancel(num/den) if den != 0 else num
    print(f"n={N}: deg(Den)={res['dD']} nullity={res['nullity']} blocks={res['names']}")
    print("\nNum =", sp.factor(num))
    print("Den =", sp.factor(den))
    print("\na_n = Num/Den =")
    sp.pprint(sp.factor(expr))
    print("\nstring:", expr)

    # holdout verification
    import random
    pts = gen_points(N, 8, seed=77777)
    allok = True
    print("\nholdout:")
    for b, a, fw in pts:
        val = expr.subs({syms[i]: sp.Rational(b[i].numerator, b[i].denominator) for i in range(len(syms))})
        ok = sp.simplify(val - sp.Rational(a.numerator, a.denominator)) == 0
        allok = allok and ok
        print(f"  fw={fw}: oracle={a} fit={val} {'OK' if ok else 'MISMATCH'}")
    print("ALL OK" if allok else "MISMATCH!!")
