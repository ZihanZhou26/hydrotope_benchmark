import sympy as sp
from fractions import Fraction as Fr
import harness
sigma=[-1,-1,-1,1,1,1]
def Bval(w4,w5):
    r=harness.onshell(6,[Fr(2),Fr(3),w4,w5],sigma); return r['A_im']
def Dhyp(w4,w5):
    return (5+w4+w5)*(w4+2)*(w4+3)*(w5+2)*(w5+3)
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
g4=[Fr(46,10)+Fr(k,20) for k in range(0,17)]
g5=[Fr(36,10)+Fr(k,20) for k in range(0,17)]
pts=[]
for a in g4:
    for b in g5:
        try: pts.append((a,b,Bval(a,b)))
        except: pass
print('points',len(pts))
monos=[(i,j) for i in range(7) for j in range(7) if i+j<=9]
A=[];bb=[]
for (a,b,B) in pts:
    A.append([a**i*b**j for (i,j) in monos]); bb.append(B*Dhyp(a,b))
sol,stat=solve_exact(A,bb)
print('Dhyp test:',stat,'nmono',len(monos))
if sol:
    x,y=sp.symbols('w4 w5')
    N=sum(sol[k]*x**monos[k][0]*y**monos[k][1] for k in range(len(monos)))
    print('C=B*Dhyp =',sp.factor(N))
