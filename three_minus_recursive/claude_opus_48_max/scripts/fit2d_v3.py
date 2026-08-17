import sympy as sp
from fractions import Fraction as Fr
import harness
sigma=[-1,-1,-1,1,1,1]
def Bval(w4,w5):
    r=harness.onshell(6,[Fr(2),Fr(3),w4,w5],sigma); return r['A_im']
def solve_exact(A,b):
    rows=[row[:]+[b[i]] for i,row in enumerate(A)]; m=len(A[0]); piv=[]; r=0
    for c in range(m):
        sel=next((i for i in range(r,len(rows)) if rows[i][c]!=0),None)
        if sel is None: continue
        rows[r],rows[sel]=rows[sel],rows[r]
        inv=Fr(1)/rows[r][c]; rows[r]=[v*inv for v in rows[r]]
        for i in range(len(rows)):
            if i!=r and rows[i][c]!=0:
                f=rows[i][c]; rows[i]=[a-f*b2 for a,b2 in zip(rows[i],rows[r])]
        piv.append(c); r+=1
        if r==m: break
    for i in range(r,len(rows)):
        if rows[i][m]!=0 and all(v==0 for v in rows[i][:m]): return None,'inconsistent'
    sol={c:rows[i][m] for i,c in enumerate(piv)}
    return [sol.get(c,Fr(0)) for c in range(m)],'ok'
# verified single-chamber box w4 in [4.7,5.3], w5 in [3.7,4.3]
g4=[Fr(47,10)+Fr(k,40) for k in range(0,25)]
g5=[Fr(37,10)+Fr(k,40) for k in range(0,25)]
pts=[]
for a in g4:
    for b in g5:
        try: pts.append((a,b,Bval(a,b)))
        except: pass
print('points',len(pts))
x,y=sp.symbols('w4 w5')
def test_denom(name,Dfun,maxdeg):
    monos=[(i,j) for i in range(maxdeg+1) for j in range(maxdeg+1) if i+j<=maxdeg]
    A=[];bb=[]
    for (a,b,B) in pts:
        A.append([a**i*b**j for (i,j) in monos]); bb.append(B*Dfun(a,b))
    sol,stat=solve_exact(A,bb)
    if sol:
        N=sum(sol[k]*x**monos[k][0]*y**monos[k][1] for k in range(len(monos)))
        print(f'{name}: {stat}  C=B*D = {sp.factor(N)}')
    else:
        print(f'{name}: {stat}')
s=lambda a,b:5+a+b
test_denom('D4=s(w4+2)(w4+3)(w5+2)(w5+3)', lambda a,b: s(a,b)*(a+2)*(a+3)*(b+2)*(b+3), 9)
