import time
from fractions import Fraction as F
import r5_walls as W
t0=time.time()
crs=W.find_crossings(F(5,2),F(33,10),F(9,2),F(61,10),F(1,40),F(6))
print('find_crossings:',round(time.time()-t0,3),'s, crossings:',[(k) for (lo,hi,k) in crs])
for (lo,hi,key) in crs:
    if key[0]!='2': continue
    t0=time.time()
    r=W.extract_bracket(F(5,2),F(33,10),F(9,2),F(61,10),lo,hi,key,F(1,120),14)
    ok = (r[0]!='fitfail') and r[4]
    print('extract',key,':',round(time.time()-t0,3),'s ok=',ok)
