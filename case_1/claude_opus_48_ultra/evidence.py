"""Generate the explicit numerical-evidence table for REPORT.md."""
from bg import amp_two_minus, BG
from closed_form import A_principal, A5_complete, softest_is_minus
from fractions import Fraction as Q

def row(n, free, complete=False):
    A,kL,wL=amp_two_minus(n,free)
    pred = A5_complete(wL) if (complete and n==5) else A_principal(n,wL)
    err = 0 if pred==A.im else abs(float(pred-A.im))/abs(float(A.im)) if A.im!=0 else float('inf')
    tag = "complete" if (complete and n==5) else "principal"
    return n, [str(c) for c in free], str(A.im)+" i", str(pred)+" i", err, tag, softest_is_minus(wL)

print("| n | free freqs | BGAmplitude | closed form | rel.err | which |")
print("|---|------------|-------------|-------------|---------|-------|")

# n=5 complete formula across different chambers (softest leg varies)
for free in [[Q(2),Q(5,2),Q(3)], [Q(2),Q(5,2),Q(3,2)], [Q(2),Q(5,2),Q(1)],
             [Q(-3),Q(5,2),Q(7,2)], [Q(7,3),Q(-11,5),Q(13,4)]]:
    n,fr,bg,cf,err,tag,sm=row(5,free,complete=True)
    print(f"| 5 | {fr} | {bg} | {cf} | {err:.0e} | {tag} |")

# n=6,7,8 principal regime (reference-style increasing positive free freqs)
for free in [[Q(3,2),Q(2),Q(5,2),Q(3)], [Q(2),Q(3),Q(7,2),Q(11,3)]]:
    n,fr,bg,cf,err,tag,sm=row(6,free)
    print(f"| 6 | {fr} | {bg} | {cf} | {err:.0e} | {tag} |")
for free in [[Q(3,2),Q(2),Q(5,2),Q(3),Q(7,2)]]:
    n,fr,bg,cf,err,tag,sm=row(7,free)
    print(f"| 7 | {fr} | {bg} | {cf} | {err:.0e} | {tag} |")
print("(n=8 row appended separately due to runtime.)")
