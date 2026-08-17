from bg import amp_two_minus, make_kinematics, two_minus_sigma, BG
from fractions import Fraction as Q

print("=== (1) Is A a function of plus-freqs only / symmetric in w1<->w2 ? ===")
# Build a sector point directly: choose plus freqs x=(x1,x2,x3); minus w1,w2 = roots of t^2+e1 t+e2.
def build_point(xs):
    e1=sum(xs); e2=sum(xs[i]*xs[j] for i in range(len(xs)) for j in range(i+1,len(xs)))
    disc=e1*e1-4*e2  # (w1-w2)^2 ; need perfect square for rational
    return e1,e2,disc

# choose plus freqs with rational roots: pick w1,w2 first, then we need e1=-(w1+w2), e2=w1 w2.
# Direct: pick w1,w2 (minus, sigma=-1) and plus freqs satisfying sum and sumsq.
# Easiest: use make_kinematics to get a valid point, then rebuild with swapped w1,w2.
sig=two_minus_sigma(5)
kL,wL=make_kinematics(5,[Q(2),Q(5,2),Q(3)],sig,1)
print("point wL=",wL,"  k=",kL)
A0=BG(kL,wL,1).amplitude()
print("A (as given):", A0)
# swap w1,w2 -> also swap k1,k2
wL2=(wL[1],wL[0])+tuple(wL[2:])
kL2=(kL[1],kL[0])+tuple(kL[2:])
A1=BG(kL2,wL2,1).amplitude()
print("A (w1<->w2 swapped):", A1, " equal:", A0.im==A1.im)
# permute plus legs (3,4,5)->(5,3,4)
perm=[0,1,4,2,3]
wL3=tuple(wL[i] for i in perm); kL3=tuple(kL[i] for i in perm)
A2=BG(kL3,wL3,1).amplitude()
print("A (plus legs permuted):", A2, " equal:", A0.im==A2.im)

print()
print("=== (2) A/e2 across different slices (vary w3 too) ===")
for (b2,a3,t) in [(2,Q(5,2),3),(2,Q(5,2),4),(2,2,3),(3,2,Q(5,2)),(Q(3,2),Q(7,2),2),(1,3,5)]:
    A,kL,wL=amp_two_minus(5,[Q(b2),Q(a3),Q(t)])
    x=wL[2:]
    e2=x[0]*x[1]+x[0]*x[2]+x[1]*x[2]
    print(f"  free=({b2},{a3},{t})  plus={tuple(str(v) for v in x)}  A={A.im}  e2={e2}  A/e2={A.im/e2}")

print()
print("=== (3) sanity-check reconstruction solver on synthetic symmetric rational F ===")
# F = (p2)^3 / e2  where p2=x1^2+x2^2+x3^2 ; deg = 6-2=... let's make deg 6 over deg 2
import recon
from fractions import Fraction as Q
def Fsyn(x):
    p2=sum(xi*xi for xi in x)
    e2=x[0]*x[1]+x[0]*x[2]+x[1]*x[2]
    return p2*p2*p2/(e2*e2)   # deg 6 / deg4 -> homog deg ... 6-4=2? we want test
grid=[Q(1),Q(2),Q(3),Q(5,2),Q(7,2),Q(4),Q(5),Q(3,2),Q(-1),Q(-2),Q(6),Q(-3)]
import itertools
pts=[]
for combo in itertools.product(grid,repeat=3):
    x=tuple(combo)
    e2=x[0]*x[1]+x[0]*x[2]+x[1]*x[2]
    if e2==0 or any(v==0 for v in x): continue
    pts.append((x,Fsyn(x)))
    if len(pts)>=200: break
# Fsyn is degree 2 homogeneous; recon expects dA=2(n-2). Let's just directly test nullspace at right degrees.
from recon import parts,msym,rref_nullspace
dA=2  # Fsyn homog degree 2
for dD in range(0,6):
    DB=parts(dD,3); NB=parts(dD+dA,3)
    rows=[]
    for (x,Av) in pts:
        row=[Av*msym(l,x) for l in DB]+[-msym(l,x) for l in NB]
        rows.append(row)
    basis,piv=rref_nullspace(rows)
    print(f"  synthetic dD={dD}: vars={len(DB)+len(NB)} nullspace dim={len(basis)}")
    if basis:
        break
