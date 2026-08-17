"""Shared: contiguous in-chamber slice collection + exact rational reconstruction."""
from fractions import Fraction as F
import sympy as sp
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]; t=sp.Symbol('t')
def full_sig(oms):
    sq=[w*w for w in oms]; ws=cn.wall_signs(sq)
    if ws is None: return None
    a,b=sq[0:3],sq[3:6]
    if 0 in [a[0]-a[1],a[0]-a[2],a[1]-a[2],b[0]-b[1],b[0]-b[2],b[1]-b[2]]: return None
    sa=tuple(1 if a[i]>a[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    sb=tuple(1 if b[i]>b[j] else -1 for i,j in [(0,1),(0,2),(1,2)])
    return ws+(sa,sb)
def solve_exact(A,b):
    n=len(A); M=[[F(A[i][j]) for j in range(n)]+[F(b[i])] for i in range(n)]
    for col in range(n):
        piv=next((r for r in range(col,n) if M[r][col]!=0),None)
        if piv is None: return None
        M[col],M[piv]=M[piv],M[col]; pv=M[col][col]; M[col]=[x/pv for x in M[col]]
        for r in range(n):
            if r!=col and M[r][col]!=0:
                f=M[r][col]; M[r]=[M[r][k]-f*M[col][k] for k in range(n+1)]
    return [M[i][n] for i in range(n)]
def reconstruct(pts,cap=30):
    nP=len(pts)
    for total in range(0,cap):
        for dD in range(0,total+1):
            dN=total-dD; nun=(dN+1)+dD
            if nP<nun+5: continue
            rows,rhs=[],[]
            for (x,G) in pts[:nun]:
                rows.append([x**j for j in range(dN+1)]+[-G*x**k for k in range(1,dD+1)]); rhs.append(G)
            sol=solve_exact(rows,rhs)
            if sol is None: continue
            Nc=sol[:dN+1]; Dc=[F(1)]+sol[dN+1:]
            if all((sum(c*x**k for k,c in enumerate(Dc))!=0 and
                    sum(c*x**j for j,c in enumerate(Nc))==G*sum(c*x**k for k,c in enumerate(Dc)))
                   for (x,G) in pts[nun:]):
                return dN,dD,Nc,Dc
    return None
def collect_contig(base, vary, fn, step=F(1,60), maxsteps=200):
    """Collect CONTIGUOUS in-chamber points scanning outward from t=0 both ways."""
    s0=full_sig(cn.solve_squares(base))
    pts=[]
    def take(tt):
        free=list(base); free[vary-2]=base[vary-2]+tt
        oms=cn.solve_squares(free)
        if oms is None or any(w==0 for w in oms): return None
        if full_sig(oms)!=s0: return None
        try: im,_,_=h.on_shell(free,SIG)
        except Exception: return None
        return (tt, fn(tt,oms,im))
    p=take(F(0))
    if p: pts.append(p)
    for direction in (1,-1):
        for k in range(1,maxsteps+1):
            tt=direction*step*k
            p=take(tt)
            if p is None: break   # left chamber -> stop this direction (contiguous)
            pts.append(p)
    return pts,s0
def poly(coeffs): return sum(sp.Rational(c.numerator,c.denominator)*t**j for j,c in enumerate(coeffs))
