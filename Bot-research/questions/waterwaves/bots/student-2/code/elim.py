"""elim.py — express the (exact, derived) build_onshell-branch a_n in terms of the
symmetric blocks S=w1+w2, P=w1 w2, and plus-leg elementary symmetric polys, by
Groebner elimination. Conclusive test of whether a_n is a rational function of those.
"""
import sympy as sp

def n5():
    w2,w3,w4 = sp.symbols('w2 w3 w4', positive=True)
    # build_onshell n=5 solved legs (from analyze.py output)
    den = (w2+w3+w4)
    w1 = (-w2*w3 - w2*w4 - w3**2 - w3*w4 - w4**2)/den
    w5 = (-w2**2 - w2*w3 - w2*w4 - w3*w4)/den
    a = 16*w1*w2**5   # exact derived branch form
    # symmetric blocks
    S = w1 + w2
    P = w1 * w2
    E3 = w3*w4*w5
    # sanity: E1plus=-S, E2plus=P
    E1p = w3+w4+w5; E2p = w3*w4+w3*w5+w4*w5
    print("check E1plus + S =", sp.simplify(E1p + S))
    print("check E2plus - P =", sp.simplify(E2p - P))
    Ssym, Psym, Tsym, Asym = sp.symbols('S P T A')
    # clear denominators, eliminate w2,w3,w4
    eqs = [sp.numer(sp.together(Ssym - S)),
           sp.numer(sp.together(Psym - P)),
           sp.numer(sp.together(Tsym - E3)),
           sp.numer(sp.together(Asym - a))]
    print("eliminating w2,w3,w4 ...")
    G = sp.groebner(eqs, w2, w3, w4, Ssym, Psym, Tsym, Asym, order='lex')
    # find generators free of w2,w3,w4
    rel = [g for g in G.polys if not (set([w2,w3,w4]) & g.free_symbols)]
    for g in rel:
        e = g.as_expr()
        if Asym in e.free_symbols:
            print("\nrelation in (A,S,P,T):")
            sp.pprint(sp.factor(e))
            sol = sp.solve(e, Asym)
            for s_ in sol:
                print("\nA =")
                sp.pprint(sp.factor(s_))
            return

if __name__ == '__main__':
    n5()
