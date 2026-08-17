#!/usr/bin/env python3
"""Round-8 shared toolkit: fast modular (F_p) slice fits / jump extraction for n=7, built on
modbg (fast exact-mod-p BG evaluator) + n7lib. EXACT-in-F_p (no float), rational-reconstructed.

N_7 = im(A_7) * D_7 / 64 ,  D_7 = prod_{i in M, j in P}(w_i+w_j).
Mixed walls: (1=1) a_i=b_j; (1=2) a_i=b_j+b_k; (1=3) a_i=b_j+b_k+b_l.  a=w^2(minus),b=w^2(plus).
"""
from fractions import Fraction as F
import itertools
import modbg, n7lib as L

P = modbg.P
SIG = L.SIG7
def fp(fr): return modbg.fp(fr)
def minv(a): return pow(a % P, P-2, P)

# ---------- modular amplitude / numerator ----------
def N7_modp(free):
    """N_7 mod P at on-shell point given by free=(w2..w6); None if degenerate."""
    o = L.solve_squares(free)
    if o is None or any(w == 0 for w in o): return None
    im, _ = modbg.amp_onshell_modp(free, SIG)
    return (im * fp(L.D7(o))) % P, o

# ---------- modular polynomial fit in one variable ----------
def fit_poly_modp(pts, dmax):
    """pts=[(t_frac, y_modp)] -> coeff list mod P (low->high) of minimal degree consistent,
    else None. t reduced mod P. Held-out check on remaining points."""
    if not pts: return None
    ts = [fp(t) for (t, _) in pts]; ys = [y % P for (_, y) in pts]
    nseen = len(pts)
    for d in range(0, dmax+1):
        if nseen < d+1+3: continue
        n = d+1
        # Gaussian elimination on first n rows
        A = [[pow(ts[i], j, P) for j in range(n)] + [ys[i]] for i in range(n)]
        ok = True
        for c in range(n):
            piv = next((r for r in range(c, n) if A[r][c] % P), None)
            if piv is None: ok = False; break
            A[c], A[piv] = A[piv], A[c]; iv = minv(A[c][c])
            A[c] = [(x*iv) % P for x in A[c]]
            for r in range(n):
                if r != c and A[r][c]:
                    f = A[r][c]; A[r] = [(A[r][k]-f*A[c][k]) % P for k in range(n+1)]
        if not ok: continue
        coeffs = [A[i][n] for i in range(n)]
        # held-out
        good = all((sum(coeffs[j]*pow(ts[i], j, P) for j in range(n)) % P) == ys[i]
                   for i in range(n, nseen))
        if good:
            return coeffs
    return None

def poly_sub(a, b):
    n = max(len(a), len(b)); r = []
    for i in range(n):
        r.append(((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % P)
    while len(r) > 1 and r[-1] == 0: r.pop()
    return r

def poly_order(c):
    """order of vanishing at t=0 (index of first nonzero coeff)."""
    for i, v in enumerate(c):
        if v % P: return i
    return None

def poly_divexact(num, den):
    """exact polynomial division num/den mod P; return (quo, ok). ok=False if remainder!=0."""
    num = num[:];
    if all(x == 0 for x in num): return [0], True
    dd = len(den)-1
    while len(den) > 1 and den[-1] == 0: den = den[:-1];
    dd = len(den)-1
    if dd < 0: return None, False
    lead_inv = minv(den[-1])
    quo = [0]*(max(0, len(num)-len(den))+1)
    work = num[:]
    while len(work)-1 >= dd and any(x % P for x in work):
        deg = len(work)-1
        if work[-1] % P == 0:
            work.pop(); continue
        co = (work[-1]*lead_inv) % P; pos = deg-dd
        quo[pos] = co
        for i in range(len(den)):
            work[pos+i] = (work[pos+i] - co*den[i]) % P
        while len(work) > 1 and work[-1] % P == 0: work.pop()
        if len(work)-1 < dd: break
    ok = all(x % P == 0 for x in work)
    while len(quo) > 1 and quo[-1] == 0: quo.pop()
    return quo, ok

# ---------- exact polynomial fit (Fractions) for cheap non-oracle quantities (wall fn) ----------
def fit_exact(pts, dmax=8):
    import r5lib as RL
    return RL.fit_poly(pts, dmax)

# ---------- slice machinery ----------
def fc_free(base, p, q, A, B, tt):
    fr = [F(x) for x in base]; fr[p] = F(A)+tt; fr[q] = F(B)-tt
    return fr

def sig42(o):
    """tuple of the 42 mixed-wall signs (no orderings); None if on a wall."""
    return L.signature(o, with_orderings=True)

def collect_side(base, p, q, A, B, direction, step, maxn, ref):
    """[(t, N7_modp, oms)] contiguous in-chamber on one side."""
    out = []
    for k in range(1, maxn+1):
        tt = direction*step*k
        fr = fc_free(base, p, q, A, B, tt)
        o = L.solve_squares(fr)
        if o is None or any(w == 0 for w in o): break
        s = sig42(o)
        if s is None or s != ref: break
        im, _ = modbg.amp_onshell_modp(fr, SIG)
        out.append((tt, (im*fp(L.D7(o))) % P, o))
    return out

def wall_value_slice(side_pts, sm, sp_):
    """exact wall fn f(t) = sum_{j in sp_} b_j - sum_{i in sm} a_i along slice -> exact coeffs."""
    pts = []
    for (tt, _, o) in side_pts[:9]:
        sq = [w*w for w in o]
        f = sum(sq[j] for j in sp_) - sum(sq[i] for i in sm)
        pts.append((tt, f))
    return fit_exact(pts, 8)

def chamber_sig_off(base, p, q, A, B, eps):
    o = L.solve_squares(fc_free(base, p, q, A, B, eps))
    if o is None or any(w == 0 for w in o): return None
    return sig42(o)

def jump_extract(name, base, p, q, A, B, wall_sm, wall_sp, step=F(1,90), maxn=90, dmax=46):
    """Measure single-wall jump exponent and S|slice via J/f^e (mod P). wall fn f = sum_sp b - sum_sm a.
    Returns dict with order, divides flags."""
    sL = chamber_sig_off(base, p, q, A, B, -step/3)
    sR = chamber_sig_off(base, p, q, A, B, +step/3)
    if sL is None or sR is None: return {'name': name, 'err': 'degenerate'}
    sd = sum(1 for a, b in zip(sL[:42], sR[:42]) if a != b)
    ptsL = collect_side(base, p, q, A, B, -1, step, maxn, sL)
    ptsR = collect_side(base, p, q, A, B, +1, step, maxn, sR)
    cL = fit_poly_modp([(t, y) for (t, y, _) in ptsL], dmax)
    cR = fit_poly_modp([(t, y) for (t, y, _) in ptsR], dmax)
    if cL is None or cR is None:
        return {'name': name, 'err': f'fitfail nL={len(ptsL)} nR={len(ptsR)} L={cL is not None} R={cR is not None}', 'sd': sd}
    J = poly_sub(cR, cL)
    order = poly_order(J)
    # wall fn f(t) exact -> mod p coeffs
    fex = wall_value_slice(ptsR if len(ptsR) >= len(ptsL) else ptsL, wall_sm, wall_sp)
    fmod = [fp(c) for c in fex]
    res = {'name': name, 'sd': sd, 'nL': len(ptsL), 'nR': len(ptsR), 'order': order}
    for e in (1, 2, 3, 4):
        fe = [1]
        for _ in range(e): fe = poly_mul(fe, fmod)
        quo, ok = poly_divexact(J, fe)
        res[f'div{e}'] = ok
        if ok and order == e:
            res['Sslice0'] = quo[0] if quo else 0   # S at the wall point (t=0)
    return res

def poly_mul(a, b):
    r = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                r[i+j] = (r[i+j] + x*y) % P
    return r

if __name__ == "__main__":
    # smoke: N7_modp matches n7lib exact reduced mod p
    free = [F(2), F(3), F(5), F(7), F(11,2)]
    nm, o = N7_modp(free)
    im_exact = L.amp_one(free)
    n_exact = L.N7_from_im(o, im_exact)
    print("N7 modp =", nm, " exact%P =", fp(n_exact), " match:", nm == fp(n_exact))
