"""analyze.py — reduce symbolic off-shell a_n onto the on-shell surface and study structure."""
import sys
import sympy as sp
from fractions import Fraction
from symbolic import symbolic_amp


def onshell_subs(N, w):
    """Return substitution dict imposing Sum omega=0 and Sum sigma omega^2=0,
    solving for w1, wN in terms of frees w2..w_{N-1} (mirrors build_onshell)."""
    free = [w[i] for i in range(2, N)]
    sigma = [-1, -1] + [1]*(N-2)
    sumFree = sum(free)
    sumSig = sum(sp.Integer(sigma[i]) * w[i+1]**2 for i in range(0, N-2))  # i->w[i+? ] careful
    # sumSig over free legs 2..N-1: sigma indices 1..N-2 (0-indexed sigma[1..N-2])
    sumSig = sum(sp.Integer(sigma[j-1]) * w[j]**2 for j in range(2, N))
    s1 = sp.Integer(sigma[0])  # -1
    wn = -(s1*sumFree**2 + sumSig)/(2*s1*sumFree)
    w1 = -(sumFree + wn)
    return {w[1]: sp.simplify(w1), w[N]: sp.simplify(wn)}


if __name__ == '__main__':
    N = int(sys.argv[1])
    sigma = [-1, -1] + [1]*(N-2)
    if N == 4:
        ref = {1: Fraction(-5), 2: Fraction(1), 3: Fraction(2), 4: Fraction(-3)}
    elif N == 5:
        ref = {1: Fraction(-7), 2: Fraction(1), 3: Fraction(2), 4: Fraction(4), 5: Fraction(-5)}
    elif N == 6:
        ref = {1: Fraction(-11), 2: Fraction(1), 3: Fraction(2), 4: Fraction(4), 5: Fraction(8), 6: Fraction(-7)}

    re, im, w = symbolic_amp(N, sigma, ref)
    print(f"n={N}: Re={re}")
    print("off-shell a_n (all omega independent):")
    print("  ", sp.expand(im))
    print()

    sub = onshell_subs(N, w)
    print("on-shell solve: w1 =", sub[w[1]], " ; wN =", sub[w[N]])
    a_on = sp.cancel(im.subs(sub))
    a_on = sp.simplify(a_on)
    print("\non-shell a_n (free vars w2..w_{N-1}):")
    sp.pprint(a_on)
    print("\nfactored:")
    sp.pprint(sp.factor(a_on))

    # numeric sanity at reference free values
    if N == 4:
        chk = {w[2]: 1, w[3]: 3}; expect = -24
        chk2 = {w[2]: 2, w[3]: 5}; expect2 = -320
        print("\ncheck (w2,w3)=(1,3):", a_on.subs(chk), " expect", expect)
        print("check (w2,w3)=(2,5):", a_on.subs(chk2), " expect", expect2)
    if N == 5:
        chk = {w[2]: 1, w[3]: 2, w[4]: 4}; expect = sp.Rational(-544,7)
        chk2 = {w[2]: 2, w[3]: 3, w[4]: 5}; expect2 = -3328
        print("\ncheck (1,2,4):", a_on.subs(chk), " expect", expect)
        print("check (2,3,5):", a_on.subs(chk2), " expect", expect2)
    if N == 6:
        chk = {w[2]: 1, w[3]: 2, w[4]: 3, w[5]: 4}; expect = sp.Rational(-1024,5)
        print("\ncheck (1,2,3,4):", a_on.subs(chk), " expect", expect)
