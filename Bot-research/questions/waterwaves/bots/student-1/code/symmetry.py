"""Test the symmetry group of a_n in the two-minus sector.
Expected: S_2 on minus legs {1,2} x S_{n-2} on plus legs {3..n}.
We get an on-shell omega via -w, then evaluate a_n on permuted omega via --amp.
"""
import itertools, sympy as sp
import bgio

def get_onshell(n, freew):
    r=bgio.onshell(n, freew)
    assert r["ok"], r
    return [sp.Rational(x.numerator,x.denominator) for x in r["omega"]], sp.Rational(r["a"].numerator,r["a"].denominator)

def a_of(omega):
    """a_n for an explicit omega vector via raw --amp two-minus."""
    from fractions import Fraction as Fr
    om=[Fr(int(sp.numer(x)),int(sp.denom(x))) for x in omega]
    r=bgio.amp_twominus(om)
    assert r["ok"], r
    assert r["re_zero"], "Re!=0"
    return sp.Rational(r["a"].numerator,r["a"].denominator)

def test(n, freew):
    omega, a0 = get_onshell(n, freew)
    print(f"n={n} freew={freew}: omega={omega}, a_n={a0}")
    # baseline via --amp (should match -w)
    print("  --amp baseline matches -w:", a_of(omega)==a0)
    minus=[0,1]; plus=list(range(2,n))
    # swap minus legs
    sw=omega[:]; sw[0],sw[1]=sw[1],sw[0]
    print("  swap minus {1,2}:", a_of(sw)==a0)
    # all permutations of plus legs (sample)
    cnt=0; allok=True
    for perm in itertools.permutations(plus):
        new=omega[:]
        for i,pidx in zip(plus,perm): new[i]=omega[pidx]
        if a_of(new)!=a0: allok=False; print("   plus-perm FAIL", perm)
        cnt+=1
        if cnt>=24: break
    print(f"  plus-leg perms invariant ({cnt} tested):", allok)
    # cross perm (swap a minus and a plus) should generally FAIL
    cr=omega[:]; cr[0],cr[2]=cr[2],cr[0]
    print("  swap minus<->plus (expect change):", a_of(cr)!=a0)

if __name__=="__main__":
    test(5,[2,3,5])
    test(5,[1,2,4])
    test(6,[1,2,3,4])
