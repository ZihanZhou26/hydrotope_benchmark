#!/usr/bin/env python3
"""MODULAR rational reconstruction of A_6 on the in-chamber F-const slice (FAST:
GF(P) linear algebra, no big-integer blowup).  Determine deg D, reconstruct
D(t) mod P, then identify its factors by testing which candidate polynomials
|k_S|(t), e2(t), S_F(t) divide D(t) (mod P) and to what multiplicity.

Slice: w4=5+s, w5=7-s, w2=2, w3=3, shift s=p/H, integer param p.  Chamber
shift-range ~ (-1.4,3.4).  H=20 -> ~90 nodes."""
from fractions import Fraction as Fr
from itertools import combinations
import harness as h

P=2147483647   # 2^31-1 prime
H=20
SIG=[-1,-1,-1,1,1,1]

def inv(a): return pow(a%P, P-2, P)
def fr_mod(fr): return (fr.numerator%P)*inv(fr.denominator)%P

def mixsig(oms):
    w=[None]+[Fr(x) for x in oms]; s=[]
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            mns=[i for i in S if SIG[i-1]<0]; pls=[i for i in S if SIG[i-1]>0]
            if mns and pls:
                v=sum(Fr(SIG[i-1])*w[i]**2 for i in S)
                s.append(0 if v==0 else (1 if v>0 else -1))
    return tuple(s)

# collect in-chamber nodes
ref=mixsig(h.on_shell([Fr(2),Fr(3),Fr(5),Fr(7)],SIG)[1])
nodes=[]
for p in list(range(1,68))+list(range(-1,-28,-1)):
    sh=Fr(p,H)
    try:
        oim,oms,_=h.on_shell([Fr(2),Fr(3),Fr(5)+sh,Fr(7)-sh],SIG)
    except Exception:
        continue
    if mixsig(oms)!=ref: continue
    nodes.append((p%P, fr_mod(oim)))
print("nodes:", len(nodes), flush=True)
NP=len(nodes); xs=[x for x,_ in nodes]; ys=[y for _,y in nodes]

def nullspace_mod(rows, ncol):
    """return one nonzero null vector of the matrix rows (mod P), or None."""
    M=[r[:] for r in rows]; nr=len(M)
    pivots=[]; col=0; r=0
    where=[-1]*ncol
    for col in range(ncol):
        piv=None
        for i in range(r,nr):
            if M[i][col]%P!=0: piv=i; break
        if piv is None: continue
        M[r],M[piv]=M[piv],M[r]
        iv=inv(M[r][col])
        M[r]=[(x*iv)%P for x in M[r]]
        for i in range(nr):
            if i!=r and M[i][col]%P!=0:
                f=M[i][col]
                M[i]=[(M[i][c]-f*M[r][c])%P for c in range(ncol)]
        where[col]=r; r+=1
        if r==nr: break
    free=[c for c in range(ncol) if where[c]==-1]
    if not free: return None
    fc=free[0]
    vec=[0]*ncol; vec[fc]=1
    for c in range(ncol):
        if where[c]!=-1:
            vec[c]=(-M[where[c]][fc])%P
    return vec

def reconstruct(b):
    a=NP-b-3                      # max numerator degree given node budget
    need=a+b+1
    if need>NP: a=NP-b-1; need=a+b+1
    rows=[[pow(xs[k],i,P) for i in range(a+1)]+[(-ys[k]*pow(xs[k],j,P))%P for j in range(b+1)]
          for k in range(need)]
    vec=nullspace_mod(rows, a+b+2)
    if vec is None: return None
    nco=vec[:a+1]; dco=vec[a+1:]
    if all(c==0 for c in dco): return None
    # verify on all nodes
    for k in range(NP):
        Nv=sum(nco[i]*pow(xs[k],i,P) for i in range(a+1))%P
        Dv=sum(dco[j]*pow(xs[k],j,P) for j in range(b+1))%P
        if (Nv-ys[k]*Dv)%P!=0: return None
    return nco,dco,a

found=None
for b in range(0,30):
    r=reconstruct(b)
    print(f"  b={b}: {'CONSISTENT' if r else 'no'}", flush=True)
    if r: found=(b,)+r; break

if not found:
    print("no consistent b<=29", flush=True)
else:
    b,nco,dco,a=found
    # trim trailing zeros
    while len(dco)>1 and dco[-1]%P==0: dco.pop()
    while len(nco)>1 and nco[-1]%P==0: nco.pop()
    degD=len(dco)-1; degN=len(nco)-1
    print(f"\nMINIMAL: degD={degD} degN={degN}  (mod P)", flush=True)
    # candidate factor polynomials in param p (shift=p/H): clear denominators -> integer poly
    import sympy as sp
    t=sp.Symbol('t')
    sh=t/H
    w2,w3=sp.Integer(2),sp.Integer(3); w4=sp.Integer(5)+sh; w5=sp.Integer(7)-sh
    F=w2+w3+w4+w5; R=-w2**2-w3**2+w4**2+w5**2
    w1=-(F**2+R)/(2*F); w6=-(F**2-R)/(2*F)
    W={1:w1,2:w2,3:w3,4:w4,5:w5,6:w6}
    cands={}
    for r in range(1,6):
        for S in combinations(range(1,7),r):
            cands[('k',S)]=sp.together(sum(sp.Integer(SIG[i-1])*W[i]**2 for i in S))
    cands[('e2+',0)]=sp.together(w4*w5+w4*w6+w5*w6)
    cands[('e2-',0)]=sp.together(w1*w2+w1*w3+w2*w3)
    cands[('Sf',0)]=w2+w3+w4+w5
    cands[('w1+w6',0)]=w1+w6
    # turn each into a primitive integer poly in t, reduce mod P as coeff list
    def to_int_poly(expr):
        nexpr=sp.numer(sp.together(expr))
        pol=sp.Poly(sp.expand(nexpr), t)
        return [int(c) for c in pol.all_coeffs()[::-1]]  # low->high
    def divides_modP(num_coeffs, den_coeffs):
        """does poly `fac`(num_coeffs low->high) divide D (den) mod P? return multiplicity."""
        # polynomial division mod P
        D=den_coeffs[:]
        f=num_coeffs[:]
        while len(f)>1 and f[-1]%P==0: f.pop()
        if len(f)<=1: return 0
        mult=0
        while True:
            q,rem=polydivmod(D,f)
            if rem is None: break
            if any(c%P!=0 for c in rem): break
            mult+=1; D=q
        return mult
    def polydivmod(A,B):
        A=[c%P for c in A]; B=[c%P for c in B]
        while len(B)>1 and B[-1]%P==0: B.pop()
        if len(A)<len(B): return A,[c for c in A]  # remainder=A
        binv=inv(B[-1]); q=[0]*(len(A)-len(B)+1); A=A[:]
        for i in range(len(A)-len(B),-1,-1):
            c=(A[i+len(B)-1]*binv)%P; q[i]=c
            for j in range(len(B)):
                A[i+j]=(A[i+j]-c*B[j])%P
        rem=A[:len(B)-1]
        return q, rem
    dco_modP=[c%P for c in dco]
    print("--- which candidates divide D (mod P) ---", flush=True)
    leftover=dco_modP[:]
    for key,expr in cands.items():
        ip=to_int_poly(expr)
        m=divides_modP([c%P for c in ip], leftover)
        if m>0:
            print(f"  {key}: multiplicity {m}", flush=True)
            for _ in range(m):
                q,rem=polydivmod(leftover,[c%P for c in ip]); leftover=q
    # whatever remains
    while len(leftover)>1 and leftover[-1]%P==0: leftover.pop()
    print("UNEXPLAINED leftover degree:", len(leftover)-1, flush=True)
