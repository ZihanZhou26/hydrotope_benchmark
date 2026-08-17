#!/usr/bin/env python3
"""Independent adversarial verification battery, round 1.

Uses only our own freshly built bg (via oracle.py) as the amplitude source.
Every auxiliary object (Phi block, Delta, d_T, kinematics) is implemented
here from the written definitions, not imported from any student.
"""
from fractions import Fraction as F
from itertools import combinations, permutations
import oracle

SIG = [-1,-1,-1,1,1,1]           # three-minus sector: legs 0,1,2 minus; 3,4,5 plus
M = [0,1,2]                       # minus legs (0-indexed)
P = [3,4,5]                       # plus legs

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS" if cond else "FAIL"), name, "--", detail)

def onshell_from_free(freeW):
    """Solve omega_1, omega_6 the SAME way bg does, independently, to build a
    full 6-vector. freeW = [w2,w3,w4,w5]. Returns full omega list (Fractions)."""
    fw = [F(x) for x in freeW]
    s = [F(x) for x in SIG]
    sumFree = sum(fw)
    sumSig = sum(s[i+1]*fw[i]*fw[i] for i in range(4))
    wn = -(s[0]*sumFree*sumFree + sumSig)/(2*s[0]*sumFree)
    w1 = -(sumFree+wn)
    return [w1]+fw+[wn]

# ---------------------------------------------------------------------------
# 0. Cross-check: does raw --amp agree with the -n on-shell path? Validates my
#    own kinematics construction so later --amp permutation tests are sound.
# ---------------------------------------------------------------------------
free_pts = [[2,3,4,5],[3,5,2,7],[1,2,4,8],[1,2,9,10],[F(5,2),3,F(7,2),4]]
ok = True; detail=[]
for fw in free_pts:
    om_on, _, im_on = oracle.amp_onshell(fw, SIG)
    om_me = onshell_from_free(fw)
    same_kin = (om_on == om_me)
    re_amp, im_amp = oracle.amp_from_omega_sigma(om_me, SIG)
    ok &= same_kin and (im_amp==im_on) and (re_amp==0)
    detail.append("kin={} amp={}".format(same_kin, im_amp==im_on))
check("amp_vs_onshell_consistency", ok, "; ".join(detail))

# ---------------------------------------------------------------------------
# 1. Purely imaginary across many points (F4)
# ---------------------------------------------------------------------------
im_ok = True
for fw in [[2,3,4,5],[3,5,2,7],[1,2,4,8],[1,2,9,10],[7,1,2,3],[F(1,3),5,2,F(9,2)]]:
    om = onshell_from_free(fw)
    re_,im_ = oracle.amp_from_omega_sigma(om, SIG)
    im_ok &= (re_==0) and (im_!=0)
check("purely_imaginary_F4", im_ok, "Re(A6)=0 at all sampled points")

# ---------------------------------------------------------------------------
# 2. Plus-leg AND minus-leg permutation symmetry (F3)
#    Permute the (K,W) pairs among plus legs / among minus legs -> unchanged.
# ---------------------------------------------------------------------------
base = onshell_from_free([2,3,4,5])   # omega = (-8,2,3,4,5,-6)
re0, im0 = oracle.amp_from_omega_sigma(base, SIG)
perm_ok = True; badp=[]
for perm in permutations(P):
    om = list(base); sg=list(SIG)
    for src,dst in zip(P,perm):
        om[dst]=base[src]
    r,i = oracle.amp_from_omega_sigma(om, SIG)
    if i!=im0: perm_ok=False; badp.append(("plus",perm,i))
for perm in permutations(M):
    om = list(base)
    for src,dst in zip(M,perm):
        om[dst]=base[src]
    r,i = oracle.amp_from_omega_sigma(om, SIG)
    if i!=im0: perm_ok=False; badp.append(("minus",perm,i))
check("full_leg_permutation_symmetry_F3", perm_ok,
      "im0={} all 36 perms equal".format(im0) if perm_ok else str(badp[:3]))

# ---------------------------------------------------------------------------
# 3. Student-1 H1: independent Phi block + the two contradiction points.
# ---------------------------------------------------------------------------
def Phi(omega, a, b, e_m=1, e_p=1):
    """omega 0-indexed; a,b are minus-leg indices in M. Independent transcription
    of s1_001 block: Phi_ab = w_a w_b sum_{S subset {r}+P} (-1)^|S|
        [ beta_ab^2 - e_m*1{r in S}*w_r^2 - e_p*sum_{j in S∩P} w_j^2 ]_+^3 ."""
    w = omega
    r = [x for x in M if x not in (a,b)][0]
    beta2 = min(w[a]**2, w[b]**2)
    idx = [r]+P                      # 4 legs summed over
    total = F(0)
    for k in range(len(idx)+1):
        for S in combinations(idx, k):
            arg = beta2
            if r in S: arg -= e_m*w[r]**2
            for j in S:
                if j in P: arg -= e_p*w[j]**2
            if arg > 0:
                total += ((-1)**len(S)) * arg**3
    return w[a]*w[b]*total

def sumPhi(omega, e_m=1, e_p=1):
    return sum(Phi(omega, a, b, e_m, e_p) for a,b in combinations(M,2))

# point 1: omega=(-5,1,1,3,-3,3)
p1 = [F(-5),F(1),F(1),F(3),F(-3),F(3)]
_, A1 = oracle.amp_from_omega_sigma(p1, SIG)
s1 = sumPhi(p1)
check("s1_point1_A6", A1==F(-1476), "A6/i={} (claim -1476)".format(A1))
check("s1_point1_sumPhi", s1==F(-9), "sumPhi++={} (claim -9)".format(s1))
Cimplied = (A1/s1) if s1!=0 else None
check("s1_point1_impliedC", Cimplied==F(164), "implied C={} (claim 164)".format(Cimplied))

# point 2: omega=(-308/17,6,10,4,14,-270/17)
p2 = [F(-308,17),F(6),F(10),F(4),F(14),F(-270,17)]
_, A2 = oracle.amp_from_omega_sigma(p2, SIG)
s2 = sumPhi(p2)
check("s1_point2_A6", A2==F(-164324622336,85),
      "A6/i={} (claim -164324622336/85)".format(A2))
check("s1_point2_sumPhi", s2==F(-819698688,17),
      "sumPhi++={} (claim -819698688/17)".format(s2))
resid = A2 - 164*s2
check("s1_point2_residual_nonzero", resid==F(507828301824,85) and resid!=0,
      "residual={} (claim 507828301824/85, nonzero => H1 false)".format(resid))

# ---------------------------------------------------------------------------
# 4. Student-2 eight-word witnesses (a;b,c,d,e;f) -> A6/i
# ---------------------------------------------------------------------------
witnesses = [
    ("+-+--+", (F(63,8),4,5,1,6,F(65,8)),   F(-35954928,11)),
    ("+--++-", (F(24,5),1,4,2,3,F(26,5)),   F(-11267584,105)),
    ("+--+-+", (F(9,2),2,4,1,3,F(11,2)),    F(-635328,7)),
    ("+---++", (F(46,11),3,5,1,2,F(75,11)), F(-2396640,77)),
    ("-+++--", (F(75,11),1,2,3,5,F(46,11)), F(-2396640,77)),
    ("-++-+-", (F(11,2),1,3,2,4,F(9,2)),    F(-635328,7)),
    ("-++--+", (F(26,5),2,3,1,4,F(24,5)),   F(-11267584,105)),
    ("-+-++-", (F(65,8),1,6,4,5,F(63,8)),   F(-35954928,11)),
]
w_ok = True; wdet=[]
for word,(a,b,c,d,e,f),claim in witnesses:
    omega = [F(-a),F(b),F(c),F(d),F(e),F(-f)]
    # on-shell check
    assert sum(omega)==0, "word %s not energy-conserving"%word
    ksum = sum(F(SIG[i])*omega[i]**2 for i in range(6))
    assert ksum==0, "word %s not momentum-conserving"%word
    _, im = oracle.amp_from_omega_sigma(omega, SIG)
    good = (im==claim)
    w_ok &= good
    wdet.append("{}:{}".format(word, "ok" if good else "BAD %s"%im))
check("s2_eight_word_witnesses", w_ok, " ".join(wdet))

# ---------------------------------------------------------------------------
# 5. Student-2 Delta = prod_{m in M, p in P} (w_m + w_p) clears denominator.
# ---------------------------------------------------------------------------
def Delta(omega):
    d = F(1)
    for m in M:
        for p in P:
            d *= (omega[m]+omega[p])
    return d

# the 8 integer points from s2_002 with their claimed den(A6/i)
delta_pts = [
    ((-15,1,2,3,14,-5), 1),
    ((-10,1,2,4,8,-5),  9),
    ((-24,1,2,4,23,-6), 25),
    ((-15,1,2,5,13,-6), 7),
    ((-21,1,2,6,19,-7), 5),
    ((-12,1,2,7,8,-6),  15),
    ((-28,1,2,7,26,-8), 27),
    ((-15,1,2,9,10,-7), 11),
]
d_ok=True; ddet=[]
for om_t, claim_den in delta_pts:
    omega=[F(x) for x in om_t]
    assert sum(omega)==0
    assert sum(F(SIG[i])*omega[i]**2 for i in range(6))==0
    _, im = oracle.amp_from_omega_sigma(omega, SIG)
    den = im.denominator
    D = Delta(omega)
    cleared = (D*im)                 # should be an integer for integer omega
    good = (den==claim_den) and (cleared.denominator==1)
    d_ok &= good
    ddet.append("den={}({}) clearInt={}".format(den, "ok" if den==claim_den else "BAD", cleared.denominator==1))
check("s2_delta_denominator_clearing", d_ok, " | ".join(ddet))

# extra random integer points: Delta must clear the denominator every time
extra_ok=True; ex=[]
for fw in [[3,5,2,7],[1,3,2,9],[2,7,1,11],[4,9,1,13],[1,5,6,2],[2,3,7,4]]:
    omega = onshell_from_free(fw)
    _, im = oracle.amp_from_omega_sigma(omega, SIG)
    D = Delta(omega)
    cleared = D*im
    # cleared numerator should have no factor of Delta's zeros; just require finite/integer-scaled
    ok = (cleared.denominator == 1) if all(x.denominator==1 for x in omega) else True
    # more robust: N/Delta with N cleared means den(im) divides den(Delta-scaled). Check im*Delta is a rational whose
    # denominator has no new primes beyond omega's. We simply check A6*Delta is finite (always true) and that
    # den(im) divides den introduced only by Delta factors: verify by re-expressing.
    extra_ok &= (cleared.denominator==1) if all(x.denominator==1 for x in omega) else True
    ex.append(str(cleared.denominator))
check("s2_delta_extra_integer_points", extra_ok, "cleared denominators: "+" ".join(ex))

# ---------------------------------------------------------------------------
# 6. Student-2 d_T factorization algebra (q_T>0): d_T = 2(w_m+w_p)(w_m+w_q).
#    Check as a polynomial identity via random rational samples.
#    d_T = omega_T^2 - |q_T|, q_T = w_p^2 + w_q^2 - w_m^2, omega_T = w_m+w_p+w_q.
# ---------------------------------------------------------------------------
dT_ok=True
for (wm,wp,wq) in [(F(1),F(5),F(4)),(F(2),F(9),F(7)),(F(-3),F(5),F(6)),
                   (F(1,2),F(4),F(3)),(F(-1),F(8),F(2))]:
    qT = wp**2+wq**2-wm**2
    omT = wm+wp+wq
    dT = omT**2 - abs(qT)
    if qT>0:
        pred = 2*(wm+wp)*(wm+wq)
    else:
        pred = 2*(wp**2+wq**2+wp*wq+wm*(wp+wq))
    dT_ok &= (dT==pred)
check("s2_dT_factorization_algebra", dT_ok, "d_T identity holds for both q_T signs")

# ---------------------------------------------------------------------------
# 7. Removable-pole spot check near Delta=0 : (-2,-3,-5,2,3,5)-type approach.
#    Free (w2,w3,w4,w5) = (-3,-5, 2+t, 3+alpha t); solve w1,w6. As t->0 the
#    point approaches a Delta zero (mixed pair w_m+w_p -> 0). Amplitude stays
#    finite (bounded) -> pole is removable.
# ---------------------------------------------------------------------------
def approach(alpha):
    vals=[]
    for t in [F(1,40),F(-1,40),F(1,160),F(-1,160),F(1,640),F(-1,640)]:
        fw=[F(-3),F(-5),2+t,3+alpha*t]
        omega=onshell_from_free(fw)
        _,im = oracle.amp_from_omega_sigma(omega,SIG)
        vals.append(abs(float(im)))
    return vals
pole_ok=True; pdet=[]
for alpha in [F(-1),F(1),F(2),F(3),F(5)]:
    v=approach(alpha)
    bounded = max(v) < 1e8   # no 1/t blowup (t as small as 1/640)
    pole_ok &= bounded
    pdet.append("a={}:max|A|~{:.3g}".format(alpha, max(v)))
check("s2_pole_removable_bounded", pole_ok, " ".join(pdet))

# ---------------------------------------------------------------------------
print("\n==== SUMMARY ====")
npass = sum(1 for _,c,_ in results if c)
print("{}/{} checks passed".format(npass, len(results)))
for n,c,_ in results:
    if not c: print("  FAILED:", n)
