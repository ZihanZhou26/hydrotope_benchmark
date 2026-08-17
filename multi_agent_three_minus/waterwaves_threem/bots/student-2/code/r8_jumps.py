#!/usr/bin/env python3
"""Exact single-wall jump extractor at n=7 (F-const slice), robust version.
N_7 = A_7 * Dfull is polynomial-per-chamber on an F-const slice. Find a single-wall
crossing, reconstruct N_7 on each side, jump J = N_+ - N_-.  Exponent e = max power
of the (polynomial) wall function f_wall(t) dividing J (exact polynomial division).
Coefficient = J / f_wall^e (polynomial in t)."""
import sympy as sp, itertools
from fractions import Fraction as F
import r8bg

t=sp.Symbol('t')
def Q(x): return sp.Rational(F(x).numerator,F(x).denominator)
MINUS=[0,1,2]; PLUS=[3,4,5,6]

def Dfull(o):
    d=F(1)
    for i in MINUS:
        for j in PLUS: d*=(o[i]+o[j])
    return d

def WALLS():
    W=[]
    for i in MINUS:
        for j in PLUS: W.append(('11',(i,),(j,)))
        for jk in itertools.combinations(PLUS,2): W.append(('12',(i,),jk))
        for jkl in itertools.combinations(PLUS,3): W.append(('13',(i,),jkl))
    return W
WL=WALLS()
def wallf(o,w):
    sq=[x*x for x in o]; _,sm,sp_=w
    return sum(sq[j] for j in sp_)-sum(sq[i] for i in sm)
def signs(o):
    s=[]
    for w in WL:
        v=wallf(o,w)
        if v==0: return None
        s.append(1 if v>0 else -1)
    return tuple(s)
def fc(base,p,q,tv):
    fr=list(base); fr[p]=base[p]+tv; fr[q]=base[q]-tv; return fr

def find_single(base,p,q,lo,hi,nscan=600):
    prev=None;prevt=None
    for k in range(nscan+1):
        tv=lo+(hi-lo)*F(k,nscan)
        fr=fc(base,p,q,tv)
        if sum(F(x) for x in fr)==0: continue
        o=r8bg.solve_legs(fr,7); s=signs(o)
        if s is None: prev=None; continue
        if prev is not None:
            d=[idx for idx in range(len(s)) if s[idx]!=prev[idx]]
            if len(d)==1: return prevt,tv,d[0]
            if len(d)>1: prev=s; prevt=tv; continue
        prev=s;prevt=tv
    return None

def recon(base,p,q,t_start,t_end,npts=30,deg=22):
    frees=[];tvs=[]
    for k in range(1,npts+1):
        tv=t_start+(t_end-t_start)*F(k,npts)
        frees.append(fc(base,p,q,tv)); tvs.append(tv)
    ims=r8bg.batch(frees,7)
    pts=[(tv,F(im)*Dfull(r8bg.solve_legs(fr,7))) for tv,fr,im in zip(tvs,frees,ims) if im is not None]
    if len(pts)<deg+3: return None
    xs=[Q(a[0]) for a in pts]; ys=[Q(a[1]) for a in pts]
    poly=sp.Poly(sp.interpolate(list(zip(xs[:deg+1],ys[:deg+1])),t),t)
    ok=all(poly.eval(xs[i])==ys[i] for i in range(deg+1,len(pts)))
    return poly,ok

def wallpoly(base,p,q,tL,tR,w):
    pts=[]
    for k in range(8):
        tv=tL+(tR-tL)*F(k,7); o=r8bg.solve_legs(fc(base,p,q,tv),7)
        pts.append((Q(tv),Q(wallf(o,w))))
    return sp.Poly(sp.interpolate(pts,t),t)

def analyze(base,p,q,lo,hi,label="",want_coeff=False):
    fs=find_single(base,p,q,lo,hi)
    if fs is None: print(f"  [{label}] no single-wall crossing"); return None
    tL,tR,wi=fs; w=WL[wi]; width=(tR-tL)
    # reconstruct away from crossing on each side, small window
    Lm=recon(base,p,q,tL, tL-8*width)   # toward lo
    Rp=recon(base,p,q,tR, tR+8*width)   # toward hi
    if Lm is None or Rp is None or not Lm[1] or not Rp[1]:
        print(f"  [{label}] recon single-piece failed "
              f"({None if Lm is None else Lm[1]},{None if Rp is None else Rp[1]})"); return None
    J=sp.Poly(Rp[0].as_expr()-Lm[0].as_expr(),t)
    if J.is_zero:
        print(f"  [{label}] wall {w}: JUMP ZERO (smooth)"); return (0,w,None)
    fwp=wallpoly(base,p,q,tL,tR,w)
    # make fwp primitive monic-ish; exponent = max power of fwp dividing J
    e=0; cur=J
    while True:
        quo,rem=sp.div(cur.as_expr(),fwp.as_expr(),t)
        if sp.simplify(rem)==0:
            cur=sp.Poly(quo,t); e+=1
        else: break
    coeff=cur.as_expr() if want_coeff else None
    print(f"  [{label}] wall {w[0]} {w[1]}{w[2]}: exponent={e}"
          + (f"  coeff(t)deg={sp.Poly(cur,t).degree()}" if want_coeff else ""))
    return e,w,coeff

if __name__=="__main__":
    print("n=7 single-wall jump exponents (own oracle, exact). Expect 11->1,12->2,13->4")
    cases=[([F(2),F(3),F(5),F(7),F(11)],3,4,F(-2),F(2),"A"),
           ([F(2),F(3),F(13,2),F(7),F(11)],2,4,F(-3),F(3),"B"),
           ([F(3),F(2),F(5),F(7),F(11)],0,4,F(-2),F(2),"C"),
           ([F(2),F(3),F(5),F(17,2),F(11)],3,1,F(-3),F(3),"D"),
           ([F(2),F(3),F(5),F(7),F(23,2)],4,0,F(-3),F(3),"E"),
           ([F(2),F(3),F(9,2),F(8),F(12)],2,1,F(-3),F(3),"F")]
    seen={}
    for base,p,q,lo,hi,lab in cases:
        r=analyze(base,p,q,lo,hi,lab)
        if r and r[0]>0: seen.setdefault(r[1][0],set()).add(r[0])
    print("exponents by wall type:",{k:sorted(v) for k,v in seen.items()})
