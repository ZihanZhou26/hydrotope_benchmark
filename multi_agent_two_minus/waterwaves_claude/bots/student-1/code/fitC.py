"""Fit C_n = a_n / (2^(n-1) * w1*w2) as a polynomial in the squared magnitudes,
within ONE fine chamber (local perturbation). C_n should be homogeneous degree
(n-3) in the squares t_i = omega_i^2. We fit it as a polynomial in the (n-3)
smallest squares (sorted ascending), labelled by which are plus vs the smaller
minus. Returns the polynomial in symbols u1<=u2<=... (smallest squares) and a
flag for the position of the smaller-minus among them (or 'outside')."""
import sympy as sp, itertools
import bgio
from freefitN import local_points, find_chamber

def Cval(n, om, a):
    w1,w2=om[0],om[1]
    return a/(2**(n-1)*w1*w2)

def chamber_signature(n, om):
    """returns (k = #plus below smaller-minus, position p of smaller minus among sorted squares)."""
    m2=min(om[0]**2,om[1]**2)
    plus_sq=sorted(om[j]**2 for j in range(2,n))
    k=sum(1 for q in plus_sq if q<m2)
    return k

def collect(n, base, steps):
    pts=local_points(n, base, steps)
    out=[]
    for fw,om,a in pts:
        C=Cval(n,om,a)
        # sorted squares ascending, tagged minus/plus
        sq=sorted([(om[i]**2, ('M' if i in (0,1) else 'P')) for i in range(n)], key=lambda z:z[0])
        out.append((om,a,C,sq))
    return out

def smaller_minus_square(om):
    return min(om[0]**2, om[1]**2)

if __name__=="__main__":
    st=[sp.Rational(0),sp.Rational(1,150),sp.Rational(2,150),sp.Rational(3,150),sp.Rational(-1,150),sp.Rational(-2,150),sp.Rational(4,150)]
    for n in (6,):
        for k in range(0,5):
            fw,om=find_chamber(n,k,seed=100+k)
            if fw is None:
                print(f"n={n} k={k}: no chamber"); continue
            data=collect(n,fw,st)
            # describe the value as polynomial in the (n-3) smallest squares of the BASE point
            base=data[0]
            sq=base[3]
            nrel=n-3
            print(f"=== n={n} k={k}: base omega={[str(v) for v in om]}  C={base[2]}")
            print(f"    sorted squares (asc) with tag: {[(str(s),t) for s,t in sq[:nrel+1]]}")
            # show C in terms of the smallest squares numerically for the base
            small=[s for s,t in sq[:nrel]]
            print(f"    {nrel} smallest squares: {[str(s) for s in small]}  product={sp.prod(small)}  C/product={sp.nsimplify(base[2]/sp.prod(small)) if sp.prod(small)!=0 else 'NA'}")
