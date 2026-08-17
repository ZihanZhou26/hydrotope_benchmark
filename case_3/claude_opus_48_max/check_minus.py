import re
from fractions import Fraction as Fr
def parse(path):
    rows=[]
    for line in open(path):
        line=line.strip()
        if '|' not in line: continue
        n_s,w_s,a_s=[x.strip() for x in line.split('|')]
        n=int(n_s)
        ws=[Fr(x) for x in re.findall(r'-?\d+(?:/\d+)?', w_s)]
        ac=a_s.replace('*I','').replace('I','').replace('(','').replace(')','')
        coeff=Fr(ac)
        rows.append((n,ws,coeff))
    return rows
rows=parse('data.txt')
print("Testing R5 = -16 * w1 * w2^5  (w1,w2 = the two minus legs):")
for n,ws,c in rows:
    if n!=5: continue
    w1,w2=ws[0],ws[1]
    pred=-16*w1*w2**5
    ok = pred==c
    if not ok:
        print(f"  MISMATCH w={ws} actual={c} pred={pred}")
print("  n=5 all match:", all((-16*ws[0]*ws[1]**5==c) for n,ws,c in rows if n==5))

# n=6,7: see if c / (w1) or similar reveals structure; print c and minus legs & ratios
print("\nn=6 rows: w1,w2 (minus), c=A/I, and c/w1, c/(w1*w2):")
for n,ws,c in rows:
    if n!=6: continue
    w1,w2=ws[0],ws[1]
    print(f"  w={[str(x) for x in ws]}  c={c}")
