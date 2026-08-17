#!/usr/bin/env python3
"""Closed-form probe for N = A_6*(e3m+e3p)/(i 2^5). Test structured ansatze that
respect: deg 11, S3xS3xZ2 sym, odd, (1=1) jump order 1, (1=2) jump order 3.
Strategy: subtract the soft-determined leading structure; inspect remainder.
Quick exact evaluations of N/i at symmetric special points to look for patterns."""
import sys
from fractions import Fraction as F
import harness as h, chambers_n6 as cn, inv
SIG=[-1,-1,-1,1,1,1]
def pr(*a): print(*a,flush=True)
def N_over_i(free):
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms): return None,None
    im,_,_=h.on_shell(free,SIG)
    e1,e2,e3m,e3p=inv.invariants(oms)
    return im*(e3m+e3p), oms   # N/i (times 2^5; structure only)

# Evaluate C_6/i = (A_6/i) and N/i at points; print invariants to look for a pattern.
pr("point : A_6/i , (e3m+e3p) , N/i=(A_6/i)(e3m+e3p) , invariants (e1,e2,e3m,e3p)")
for free in [[F(2),F(3),F(5),F(7)],[F(1),F(2),F(3),F(4)],[F(2),F(2),F(3),F(3)],
             [F(1),F(1),F(1),F(5)],[F(-2),F(3),F(4),F(-5)]]:
    oms=cn.solve_squares(free)
    if oms is None or any(w==0 for w in oms):
        pr(f"  {free}: degenerate"); continue
    try: im,_,_=h.on_shell(free,SIG)
    except Exception as e: pr(f"  {free}: SIGFPE/wall"); continue
    e1,e2,e3m,e3p=inv.invariants(oms)
    pr(f"  free={[str(x) for x in free]}: A_6/i={im}, e3m+e3p={e3m+e3p}, N/i={im*(e3m+e3p)}")
    pr(f"        e1={e1} e2={e2} e3m={e3m} e3p={e3p}")
