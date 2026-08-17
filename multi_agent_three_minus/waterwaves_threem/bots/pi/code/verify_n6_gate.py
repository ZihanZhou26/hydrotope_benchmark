#!/usr/bin/env python3
"""PI independent verification of student-2's n=6 gate claims:
  (1) NO factorization poles: drive D_S = omega_S^2/|k_S| - g -> 0, A_6 stays finite, A_6*D_S -> 0.
  (2) homogeneous degree 2n-4 = 8.
  (3) symmetry S_3(minus 1,2,3) x S_3(plus 4,5,6) x Z_2(swap triples).
All in EXACT rational mode against my OWN copy of bg.cpp (bots/pi/code/bg).
"""
import subprocess, re, sys
from fractions import Fraction as F

BG = "./bg"
SIG = "-1,-1,-1,1,1,1"  # three-minus n=6

def run_amp(K, W, g=1):
    """raw --amp: full control of all 6 momenta and frequencies. Returns (re,im) as Fractions or None on SIGFPE."""
    Ks = ",".join(str(F(k)) for k in K)
    Ws = ",".join(str(F(w)) for w in W)
    try:
        out = subprocess.run([BG, "--amp", "-K", Ks, "-W", Ws, "-g", str(g)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if out.returncode != 0:
        return None  # SIGFPE on a wall/channel
    return parse(out.stdout)

def run_onshell(freeW, g=1):
    """on-shell -n 6 -w <4 free> -s SIG. freeW = (w2,w3,w4,w5). Returns (re,im,full_omega) or None."""
    ws = ",".join(str(F(w)) for w in freeW)
    try:
        out = subprocess.run([BG, "-n", "6", "-w", ws, "-s", SIG, "-g", str(g)],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60)
    except subprocess.TimeoutExpired:
        return None
    if out.returncode != 0:
        return None
    ri = parse(out.stdout)
    om = parse_omega(out.stdout)
    return (ri[0], ri[1], om) if ri else None

def parse(text):
    m = re.search(r"A_\d+ = i \* \(([-0-9/]+)\)", text)
    if m: return (F(0), F(m.group(1)))
    m = re.search(r"A_\d+ = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)", text)
    if m: return (F(m.group(1)), F(m.group(2)))
    return None

def parse_omega(text):
    m = re.search(r"omega = \{([^}]*)\}", text)
    if not m: return None
    return [F(x.strip()) for x in m.group(1).split(",")]

def onshell_from_free(freeW):
    """Reproduce bg.cpp's on-shell solve for legs 1,6 from free legs 2..5, signs SIG."""
    w2,w3,w4,w5 = (F(x) for x in freeW)
    free = [w2,w3,w4,w5]
    sig = [F(-1),F(-1),F(-1),F(1),F(1),F(1)]
    sumFree = sum(free)
    sumSig = sum(sig[i+1]*free[i]*free[i] for i in range(4))  # sig index 1..4
    s0 = sig[0]
    w6 = -(s0*sumFree*sumFree + sumSig)/(2*s0*sumFree)
    w1 = -(sumFree + w6)
    W = [w1,w2,w3,w4,w5,w6]
    K = [sig[i]*W[i]*W[i] for i in range(6)]  # g=1
    return W, K

print("="*70)
print("GATE CLAIM (1): NO POLES -- drive channel D_S -> 0, A_6 must stay finite")
print("="*70)
# channel S = {2,3,4} (free legs). D_S = omega_S^2/|k_S| - g, root at w4 = -19/5 (w2=2,w3=3).
# Approach from both sides; A_6 should stay finite, A_6*D_S -> 0.
w2, w3, w5 = F(2), F(3), F(5)
def D_S(Sidx, W, K, g=1):
    wS = sum(W[i] for i in Sidx)
    kS = sum(K[i] for i in Sidx)
    return wS*wS/abs(kS) - g
print("channel S={2,3,4}, root at w4=-19/5; w2=2,w3=3,w5=5")
print(f"{'eps':>12} {'w4':>14} {'D_S':>16} {'A_6/i':>22} {'(A_6/i)*D_S':>16}")
for eps in [F(1,10), F(1,100), F(1,1000), F(1,10000)]:
    for sgn in (+1,-1):
        w4 = F(-19,5) + sgn*eps
        W,K = onshell_from_free((w2,w3,w4,w5))
        ds = D_S([2,3,4], [None]+W, [None]+K)  # legs {2,3,4}: 1-indexed indices 2,3,4
        r = run_onshell((w2,w3,w4,w5))
        if r is None:
            print(f"{float(sgn*eps):>12} {float(w4):>14} {'SIGFPE':>16}")
            continue
        im = r[1]
        print(f"{float(sgn*eps):>12.6g} {float(w4):>14.8f} {float(ds):>16.8f} {float(im):>22.4f} {float(im*ds):>16.6e}")

print()
print("="*70)
print("GATE CLAIM (2): homogeneous degree 8  (A_6(t*omega) = t^8 A_6(omega))")
print("="*70)
base = (F(2),F(3),F(5),F(7))  # free legs w2,w3,w4,w5 generic
r1 = run_onshell(base)
W,K = onshell_from_free(base)
# scaling all free freqs by t scales the solved w1,w6 by t too (homogeneous solve) -> scale full omega
for t in (F(2), F(3), F(5,2)):
    rt = run_onshell(tuple(t*x for x in base))
    ratio = rt[1]/r1[1]
    print(f"t={t}:  A_6(t*w)/A_6(w) = {ratio} ; t^8 = {t**8} ; match={ratio==t**8}")

print()
print("="*70)
print("GATE CLAIM (3): S_3 x S_3 x Z_2 symmetry  (via --amp, exact)")
print("="*70)
# Build a generic on-shell point, then permute legs at the --amp level (momenta+freqs together).
W,K = onshell_from_free((F(2),F(3),F(5),F(7)))
base_amp = run_amp(K, W)
print(f"base A_6 = i*({base_amp[1]})")
import itertools
def perm_amp(perm):
    Kp = [K[i] for i in perm]; Wp = [W[i] for i in perm]
    return run_amp(Kp, Wp)
# S_3 on minus legs {0,1,2}, identity on plus {3,4,5}
checks = []
for p in itertools.permutations([0,1,2]):
    perm = list(p)+[3,4,5]
    checks.append(("minus-perm "+str(p), perm_amp(perm)))
# S_3 on plus legs {3,4,5}
for p in itertools.permutations([3,4,5]):
    perm = [0,1,2]+list(p)
    checks.append(("plus-perm "+str(p), perm_amp(perm)))
# Z_2 swap triples (1,2,3)<->(4,5,6): perm = [3,4,5,0,1,2]
checks.append(("Z2 swap triples", perm_amp([3,4,5,0,1,2])))
allok = True
for name,val in checks:
    ok = (val is not None and val[1]==base_amp[1] and val[0]==base_amp[0])
    if not ok: allok=False
    print(f"  {name:<22} A_6=i*({val[1] if val else 'None'})  match={ok}")
print(f"\nALL S_3 wr Z_2 invariances exact: {allok}")
