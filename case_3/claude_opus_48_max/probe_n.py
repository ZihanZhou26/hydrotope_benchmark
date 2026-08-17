import re
from fractions import Fraction as Fr
def parse(path):
    rows=[]
    for line in open(path):
        line=line.strip()
        if '|' not in line: continue
        n_s,w_s,a_s=[x.strip() for x in line.split('|')]
        n=int(n_s); ws=[Fr(x) for x in re.findall(r'-?\d+(?:/\d+)?', w_s)]
        ac=a_s.replace('*I','').replace('I','').replace('(','').replace(')','')
        rows.append((n,ws,Fr(ac)))
    return rows
rows=parse('data.txt')

print("=== n=5: confirm c = 16 * w1 * w2^5 (chamber: w2 = positive small minus leg) ===")
print("  all match:", all(c==16*ws[0]*ws[1]**5 for n,ws,c in rows if n==5))

# n=6: test minus-only hypotheses. degree 2n-4=8.  In chamber, w2 small positive.
# guess c = C * w1 * w2^7 ? or c = C * w1^a w2^b with a+b=8.
print("\n=== n=6: test c = C * w1 * w2^7 ===")
for n,ws,c in rows:
    if n!=6: continue
    w1,w2=ws[0],ws[1]
    print(f"   c/(w1*w2^7) = {c/(w1*w2**7)}   (w1={w1}, w2={w2})")

print("\n=== n=7: test c = 64 * w1 * w2^9 ===")
allok=True
for n,ws,c in rows:
    if n!=7: continue
    w1,w2=ws[0],ws[1]
    r=c/(w1*w2**9)
    if r!=64: allok=False
    print(f"   c/(w1*w2^9) = {r}")
print("  n=7 all give 64:", allok)

print("\n=== UNIFIED symmetric formula test: c = 2^(n-1) * (w1*w2) * min(w1^2,w2^2)^(n-3) ===")
allok=True
for n,ws,c in rows:
    w1,w2=ws[0],ws[1]
    pred = 2**(n-1) * (w1*w2) * min(w1*w1, w2*w2)**(n-3)
    if pred!=c:
        allok=False; print(f"  MISMATCH n={n} w={[str(x) for x in ws]} c={c} pred={pred}")
print("  ALL 64 rows match unified formula:", allok)
