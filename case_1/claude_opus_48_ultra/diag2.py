from bg import amp_two_minus
from fractions import Fraction as Q
from recon import parts, msym, rref_nullspace, collect
import itertools

print("=== solver sanity on synthetic symmetric rational F = (m_{2}+stuff)/e2 ===")
# build F = P/Q with P symmetric deg 6, Q symmetric deg 4 = e2^2 ; so F homog deg 2
def e2f(x): return x[0]*x[1]+x[0]*x[2]+x[1]*x[2]
def p2f(x): return sum(v*v for v in x)
def e1f(x): return sum(x)
def Fsyn(x):
    P = p2f(x)**3 + 5*e1f(x)**6 - 3*e2f(x)*e1f(x)**4
    Q_ = e2f(x)**2
    return Fraction_safe(P, Q_)
from fractions import Fraction
def Fraction_safe(a,b): return Fraction(a)/Fraction(b)

grid=[Q(1),Q(2),Q(3),Q(5,2),Q(7,2),Q(4),Q(5),Q(3,2),Q(-1),Q(-2),Q(6),Q(-3),Q(8,3),Q(9,2)]
pts=[]
for combo in itertools.product(grid,repeat=3):
    x=tuple(combo)
    if e2f(x)==0 or any(v==0 for v in x): continue
    pts.append((x,Fsyn(x)))
    if len(pts)>=200: break
dA=2
for dD in range(0,6):
    DB=parts(dD,3); NB=parts(dD+dA,3)
    rows=[[Av*msym(l,x) for l in DB]+[-msym(l,x) for l in NB] for (x,Av) in pts]
    basis,_=rref_nullspace(rows)
    print(f"  synthetic dD={dD}: vars={len(DB)+len(NB)} nullspace dim={len(basis)}")
    if basis: print("    -> FOUND (solver works)"); break

print()
print("=== G = A/e2 at varied non-degenerate points ===")
grid2=[Q(2),Q(5,2),Q(3),Q(7,2),Q(4),Q(3,2),Q(5),Q(1),Q(11,5),Q(-2)]
cnt=0
for combo in itertools.product(grid2,repeat=3):
    free=[Q(c) for c in combo]
    try:
        A,kL,wL=amp_two_minus(5,free)
    except Exception:
        continue
    x=wL[2:]
    e2=e2f(x)
    if e2==0: continue
    G=A.im/e2
    print(f"  free={tuple(str(c) for c in free)} plus={tuple(str(v) for v in x)} A={A.im} G=A/e2={G}")
    cnt+=1
    if cnt>=14: break
