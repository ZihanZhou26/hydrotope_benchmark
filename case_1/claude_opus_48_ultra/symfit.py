"""Fit A_n as a symmetric rational function of the plus-frequencies x=(w3,...,wn).

Strategy: collect exact rational points (plus-freq vector, A_im) from MakeKinematics.
For a candidate denominator D(x) (a symmetric polynomial), compute N = A*D at each point
and fit N as a symmetric homogeneous polynomial of degree (deg A + deg D) in the
monomial-symmetric basis.  Exact rational linear solve; verify on held-out points.
"""
from bg import amp_two_minus
from fractions import Fraction as Q
import sympy as sp
from itertools import product as iproduct, permutations
from functools import lru_cache

def collect_points(n, grid):
    """grid: list of candidate rational free-frequency values.
    free = (w2, w3, ..., w_{n-1}); returns list of (xvec, A_im) with xvec=(w3,...,wn)."""
    pts = []
    seen = set()
    import itertools
    freelen = n-2
    # sample free vectors
    for combo in itertools.islice(itertools.product(grid, repeat=freelen), 0, 100000):
        free = [Q(c) for c in combo]
        if len(set(free)) < len(free):  # keep some genericity
            pass
        try:
            A, kL, wL = amp_two_minus(n, free)
        except Exception:
            continue
        x = tuple(wL[2:])  # plus freqs w3..wn  (0-based idx 2..n-1)
        key = tuple(sorted(x))
        if key in seen:
            continue
        seen.add(key)
        pts.append((x, A.im))
        if len(pts) >= 220:
            break
    return pts

@lru_cache(maxsize=None)
def partitions_into_parts(d, maxparts):
    """partitions of d into at most maxparts positive parts (as sorted desc tuples)."""
    res = []
    def rec(remaining, maxpart, cur):
        if remaining == 0:
            res.append(tuple(cur)); return
        if len(cur) == maxparts:
            return
        for p in range(min(maxpart, remaining), 0, -1):
            rec(remaining-p, p, cur+[p])
    rec(d, d, [])
    return res

def msym_value(lam, xvals):
    """monomial symmetric polynomial m_lambda evaluated at xvals (tuple of Fractions).
    lam padded with zeros to len(xvals); sum over distinct permutations of exponent vector."""
    m = len(xvals)
    exps = list(lam) + [0]*(m-len(lam))
    seen = set()
    tot = Q(0)
    for perm in set(permutations(exps)):
        term = Q(1)
        for xi, e in zip(xvals, perm):
            term *= xi**e
        tot += term
    return tot

def Dpoly_value(Dspec, xvals):
    """Dspec: dict {('e',k): power} meaning product of e_k(x)^power. Evaluate at xvals."""
    m = len(xvals)
    # elementary symmetric e_k
    def e_k(k):
        if k==0: return Q(1)
        from itertools import combinations
        s = Q(0)
        for c in combinations(range(m), k):
            t=Q(1)
            for i in c: t*=xvals[i]
            s+=t
        return s
    val = Q(1)
    for (_,k),p in Dspec.items():
        val *= e_k(k)**p
    return val

def deg_of_D(Dspec):
    return sum(k*p for (_,k),p in Dspec.items())

def fit_with_D(n, pts, Dspec):
    """Try to fit N = A*D as symmetric homogeneous poly of degree dN = 2(n-2)+deg(D)."""
    m = n-2
    dN = 2*(n-2) + deg_of_D(Dspec)
    lams = partitions_into_parts(dN, m)   # basis of monomial symmetric polys (<=m parts)
    nb = len(lams)
    # build system: sum_lam c_lam * m_lam(x) = N(x) = A*D
    rows=[]; rhs=[]
    for (x, Aim) in pts:
        Dval = Dpoly_value(Dspec, x)
        Nval = Aim*Dval
        row = [msym_value(lam, x) for lam in lams]
        rows.append(row); rhs.append(Nval)
    nb_use = nb
    if len(pts) < nb_use + 8:
        return ('too_few_points', nb, len(pts))
    M = sp.Matrix([[sp.Rational(v) for v in r] for r in rows])
    b = sp.Matrix([sp.Rational(v) for v in rhs])
    # solve overdetermined exactly: use first nb independent rows then verify
    # find a full-rank square subsystem
    sol = None
    # use sympy lstsq-like exact: solve normal eqs won't be exact integer; instead row-reduce augmented
    aug = M.row_join(b)
    # pick independent rows greedily
    chosen=[]
    Mr = sp.zeros(0, nb)
    for i in range(M.rows):
        cand = Mr.col_join(M[i,:])
        if cand.rank() > Mr.rows:
            Mr = cand
            chosen.append(i)
        if Mr.rows == nb:
            break
    if Mr.rows < nb:
        return ('rank_deficient', nb, Mr.rows)
    Msq = sp.Matrix([[M[i,j] for j in range(nb)] for i in chosen])
    bsq = sp.Matrix([b[i] for i in chosen])
    sol = Msq.LUsolve(bsq)
    # verify ALL points
    bad=0
    for i in range(M.rows):
        lhs = sum(sol[j]*M[i,j] for j in range(nb))
        if sp.nsimplify(lhs-b[i])!=0 and sp.simplify(lhs-b[i])!=0:
            bad+=1
    coeffs = {lams[j]: sol[j] for j in range(nb) if sol[j]!=0}
    return ('ok' if bad==0 else f'fail({bad} bad)', nb, coeffs)

if __name__ == "__main__":
    n=5
    grid = [Q(1),Q(2),Q(3),Q(5,2),Q(7,2),Q(4),Q(5),Q(3,2),Q(7,3),Q(11,5),Q(-1),Q(-2),Q(6)]
    pts = collect_points(n, grid)
    print(f"n={n}: collected {len(pts)} points")
    # candidate denominators (in elementary symmetric polys of plus freqs)
    cands = [
        {},
        {('e',2):1},
        {('e',3):1},
        {('e',2):1,('e',3):1},
        {('e',3):2},
        {('e',2):2},
        {('e',2):1,('e',3):2},
        {('e',2):2,('e',3):1},
        {('e',3):3},
        {('e',2):1,('e',3):3},
    ]
    for D in cands:
        try:
            status, nb, info = fit_with_D(n, pts, D)
        except Exception as ex:
            status, nb, info = ('EXC:'+str(ex)[:60], None, None)
        print(f"  D={D}  degD={deg_of_D(D)}  basis={nb}  -> {status}")
        if status=='ok':
            print("     N coeffs (m_lambda):")
            for lam,c in info.items():
                print(f"        m_{lam}: {c}")
