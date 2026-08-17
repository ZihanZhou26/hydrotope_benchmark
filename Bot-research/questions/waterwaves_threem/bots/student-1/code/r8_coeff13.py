#!/usr/bin/env python3
"""ROUND 8 deliverable-1: extract the EXACT (1=3) coefficient S of N_7 (the clean, chamber-
independent subset-sum coefficient; n=7 analog of n=6's Q). Uses the fast modular oracle bgmod.

Reference (1=3) wall: a_2 = b_4+b_5+b_6  (minus leg w2=idx1; plus legs w4,w5,w6=idx3,4,5 in wall;
excluded plus w7=idx6; other minus w1=idx0(solved), w3=idx2). Jump across it:
   N_R - N_L = (k)_+^4 * S,   k = a_2 - b_4 - b_5 - b_6  (the (1=3) wall fn),  deg S = 14, EVEN.

Method: many transversal single-(1=3) slices; on each fit N(t) mod p both sides (deg up to 44),
J(t)=N_R-N_L, v(t)=k(t) exact (low deg) -> S_slice(t)=J/v^4 (poly mod p, EXACT division check).
Sample S_slice(t) at several t -> (leg-vector, S mod p). Fit a stabilizer
S_2(minus 1,3) x S_3(plus 4,5,6)-symmetric, EVEN, weighted-deg-14 template basis; rational-reconstruct.
"""
from fractions import Fraction as F
import itertools, random, subprocess, os, sys
import n7lib as L, r5lib as RL
import r8lib as R8

PR = R8.P
HERE = os.path.dirname(os.path.abspath(__file__)); BGMOD = os.path.join(HERE, "bgmod")
SIG = L.SIG7
def fp(fr): return R8.fp(fr)
def minv(a): return pow(a % PR, PR-2, PR)

def batchmod(frees):
    lines = ["7|" + ",".join(str(F(x)) for x in fr) + "|" + ",".join(str(s) for s in SIG) for fr in frees]
    out = subprocess.run([BGMOD, "--batchmod"], input="\n".join(lines).encode(),
                         stdout=subprocess.PIPE).stdout.decode()
    return [None if ln == "ERR" or ln == "" else int(ln) for ln in out.strip().split("\n")]

def N7mod_batch(frees):
    res = []
    ims = batchmod(frees)
    for fr, im in zip(frees, ims):
        if im is None: res.append((None, None)); continue
        o = L.solve_squares(fr)
        res.append(((im * fp(L.D7(o))) % PR, o))
    return res

# ---- slice collection (modular) ----
def sig_at(bf, p, q, A, B, tt):
    o = L.solve_squares(L.fc_free(bf, p, q, A, B, tt))
    if o is None or any(w == 0 for w in o): return None
    return L.signature(o, with_orderings=True)

def collect_side(bf, p, q, A, B, direction, step, maxn, ref):
    tvals, frees = [], []
    for k in range(1, maxn+1):
        tt = direction*step*k
        fr = L.fc_free(bf, p, q, A, B, tt)
        o = L.solve_squares(fr)
        if o is None or any(w == 0 for w in o): break
        s = L.signature(o, with_orderings=True)
        if s is None or s != ref: break
        tvals.append(tt); frees.append(fr)
    if not frees: return [], []
    nb = N7mod_batch(frees)
    out_t, out_n, out_o = [], [], []
    for tt, (nm, o) in zip(tvals, nb):
        if nm is None: continue
        out_t.append(tt); out_n.append(nm); out_o.append(o)
    return list(zip(out_t, out_n)), out_o

def slice_Spoly(bf, p, q, A, B, wall_sm, wall_sp, step=F(1,140), maxn=130, dmax=48):
    """Return (S_slice coeffs mod p (low->high), oms_func(t)) or None. wall fn v=sum_sp b - sum_sm a."""
    sL = sig_at(bf, p, q, A, B, -step/3); sR = sig_at(bf, p, q, A, B, +step/3)
    if sL is None or sR is None: return None
    sd = sum(1 for a, b in zip(sL[:42], sR[:42]) if a != b)
    if sd != 1: return None
    ptsL, _ = collect_side(bf, p, q, A, B, -1, step, maxn, sL)
    ptsR, omsR = collect_side(bf, p, q, A, B, +1, step, maxn, sR)
    cL = R8.fit_poly_modp(ptsL, dmax); cR = R8.fit_poly_modp(ptsR, dmax)
    if cL is None or cR is None: return None
    J = R8.poly_sub(cR, cL)
    if R8.poly_order(J) != 4: return None
    # wall fn v(t) exact -> mod p
    vex = []
    for (tt, _), o in zip(ptsR[:10], omsR[:10]):
        sq = [w*w for w in o]
        vex.append((tt, sum(sq[j] for j in wall_sp) - sum(sq[i] for i in wall_sm)))
    cv = RL.fit_poly(vex, 8)
    vmod = [fp(c) for c in cv]
    v4 = [1]
    for _ in range(4): v4 = R8.poly_mul(v4, vmod)
    S, ok = R8.poly_divexact(J, v4)
    if not ok: return None
    # return S as a function: evaluate S(t) and oms(t) at sample t
    return S, (bf, p, q, A, B)

# ---- template basis: stabilizer S_2(minus other:idx0,2) x S_3(plus:3,4,5)-sym, EVEN, wdeg 14 ----
# Variables built from leg values (idx): minus-in-wall=1(w2); other minus {0,2}; plus-in-wall {3,4,5}; excl plus 6.
# We use symmetric combos; redundancy on manifold is absorbed by the fit (we just need a spanning set).
def stab_invariants(o):
    """elementary symmetric pieces respecting S_2(minus 0,2) x S_3(plus 3,4,5); plus the singled-out
    legs w2 (idx1, in wall) and w7 (idx6, excluded plus)."""
    w = o
    A1 = w[0]+w[2]; A2 = w[0]*w[2]                       # other-minus pair {1,3}
    C1 = w[3]+w[4]+w[5]
    C2 = w[3]*w[4]+w[3]*w[5]+w[4]*w[5]
    C3 = w[3]*w[4]*w[5]
    x = w[1]   # minus in wall (w2)
    y = w[6]   # excluded plus (w7)
    return A1, A2, C1, C2, C3, x, y   # weights 1,2,1,2,3,1,1

def gen_templates(wdeg=14):
    """monomials A1^a A2^b C1^c C2^d C3^e x^f y^g, weighted deg = a+2b+c+2d+3e+f+g = wdeg,
    EVEN under global flip: (a+c+e+f+g) even (A2,C2 even; A1,C1,C3,x,y odd)."""
    T = []
    for a in range(wdeg+1):
     for b in range((wdeg-a)//2+1):
      for c in range(wdeg+1):
       for d in range((wdeg)//2+1):
        for e in range(wdeg//3+1):
         base = a+2*b+c+2*d+3*e
         if base > wdeg: continue
         rem = wdeg - base
         for f in range(rem+1):
          g = rem - f
          if (a+c+e+f+g) % 2 == 0:
           T.append((a, b, c, d, e, f, g))
    return T

def eval_template(tpl, inv):
    A1, A2, C1, C2, C3, x, y = inv
    a, b, c, d, e, f, g = tpl
    return (A1**a)*(A2**b)*(C1**c)*(C2**d)*(C3**e)*(x**f)*(y**g)

if __name__ == "__main__":
    # build slices that cross ONLY the (1=3) wall a_2=b_4+b_5+b_6 (idx minus 1; plus 3,4,5).
    # near-equal plus triple => far from (1=2) walls. vary w2(idx0 free) comp w3(idx1 free).
    seeds = [
        ([F(9), F(7,2), F(6), F(6), F(3)], 0, 1, F(9), F(7,2)),
        ([F(7), F(9,2), F(6), F(3), F(2)], 0, 1, F(7), F(9,2)),
        ([F(11), F(7,2), F(9), F(6), F(2)], 0, 1, F(11), F(7,2)),
        ([F(9), F(5), F(7), F(4), F(4)], 0, 1, F(9), F(5)),       # 49+16+16=81
        ([F(7), F(11,3), F(2), F(6), F(3)], 0, 1, F(7), F(11,3)),
        ([F(13), F(9,2), F(12), F(4), F(3)], 0, 1, F(13), F(9,2)),
        ([F(11), F(13,3), F(6), F(9), F(2)], 0, 1, F(11), F(13,3)),
        ([F(9), F(7,3), F(8), F(4), F(1)], 0, 1, F(9), F(7,3)),    # 64+16+1=81
    ]
    samples = []  # (inv-tuple-as-Fraction-leg-eval mod p, S mod p)
    nslice = 0
    import sympy as sp
    t = sp.Symbol('t')
    for (bf, p, q, A, B) in seeds:
        r = slice_Spoly(bf, p, q, A, B, wall_sm=[1], wall_sp=[3, 4, 5])
        if r is None:
            print(f"slice {bf}: SKIP (sd!=1, fitfail, order!=4, or v^4 nondivide)", flush=True); continue
        S, meta = r; nslice += 1
        # sample S_slice at several in-chamber t (rational), get oms and S value mod p
        for kk in [3, 7, 11, 15, 19, 23, 27, 31, 35, 40]:
            tt = F(1,140)*kk
            o = L.solve_squares(L.fc_free(bf, p, q, A, B, tt))
            if o is None or any(w == 0 for w in o): continue
            # S value mod p = sum S[j]*tt^j
            ttm = fp(tt); Sval = 0
            for j, cj in enumerate(S): Sval = (Sval + cj*pow(ttm, j, PR)) % PR
            inv = stab_invariants([fp(w) for w in o])
            samples.append((inv, Sval))
        print(f"slice {bf}: order-4 OK, S deg={len(S)-1}, samples so far {len(samples)}", flush=True)
    print(f"\nslices used: {nslice}, samples: {len(samples)}", flush=True)
    tpls = gen_templates(14)
    print(f"templates (stab-sym, even, wdeg14): {len(tpls)}", flush=True)
    # build modular matrix
    rows = [[eval_template(tp, inv) % PR for tp in tpls] for (inv, _) in samples]
    rhs = [Sv for (_, Sv) in samples]
    # rank + consistency (greedy)
    import pickle
    basis = []; piv = []; ncol = len(tpls); nrow = len(rows)
    # solve via Gaussian elimination on rows
    M = [rows[i][:] + [rhs[i]] for i in range(nrow)]
    pr = 0; pivcols = []
    for c in range(ncol):
        p_ = next((i for i in range(pr, nrow) if M[i][c] % PR), None)
        if p_ is None: continue
        M[pr], M[p_] = M[p_], M[pr]; iv = minv(M[pr][c]); M[pr] = [(x*iv) % PR for x in M[pr]]
        for i in range(nrow):
            if i != pr and M[i][c]: f_ = M[i][c]; M[i] = [(M[i][k]-f_*M[pr][k]) % PR for k in range(ncol+1)]
        pivcols.append(c); pr += 1
        if pr == nrow: break
    incons = any(M[i][ncol] % PR and all(M[i][k] % PR == 0 for k in range(ncol)) for i in range(pr, nrow))
    print(f"rank={pr} ncol={ncol} nrow={nrow}  CONSISTENT(S is a wdeg-14 stab-sym poly)={not incons}", flush=True)
