#!/usr/bin/env python3
# Confirm bgb --batch == ./bg exactly at random three-minus n=6 points.
import subprocess, re, random
from fractions import Fraction as F
def bg_single(fw):
    ws=",".join(str(x) for x in fw)
    o=subprocess.run(["./bg","-n","6","-w",ws,"-s","-1,-1,-1,1,1,1","-g","1"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    if o.returncode!=0: return None
    m=re.search(r"A_6 = i \* \(([^)]*)\)",o.stdout)
    return F(m.group(1)) if m else None
random.seed(7)
pts=[]
for _ in range(25):
    fw=[F(random.randint(-90,90),random.randint(1,9)) for _ in range(4)]
    if sum(fw)==0: continue
    pts.append(fw)
inp="\n".join(",".join(str(x) for x in fw) for fw in pts)+"\n"
out=subprocess.run(["./bgb","--batch"],input=inp,stdout=subprocess.PIPE,universal_newlines=True).stdout.splitlines()
ok=0; tot=0
for fw,line in zip(pts,out):
    if line.strip()=="SKIP": continue
    tot+=1
    aim=F(line.split()[6])
    ref=bg_single(fw)
    if ref is not None and ref==aim: ok+=1
    else: print("MISMATCH", fw, "batch",aim,"bg",ref)
print(f"batch vs bg: {ok}/{tot} exact matches (non-skip points)")
