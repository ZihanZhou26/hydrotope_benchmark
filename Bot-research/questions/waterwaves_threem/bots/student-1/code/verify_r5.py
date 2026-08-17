#!/usr/bin/env python3
"""ONE-COMMAND round-5 verification (student-1). Own copy of bg.cpp (shared untouched).
Reproduces:
 (1) pybg independent evaluator == ./bg exactly (n=5,6,7).
 (2) (1=2) jump coefficient Q is CORRECT & global: M=N-corr12 is (1=2)-SMOOTH (jump=0)
     across many (1=2) walls / chamber types.
 (3) The SIMPLE single-wall truncated-power form FAILS (N is a BOX SPLINE):
     control synthetic simple (1=1) spline -> CONSISTENT (machinery sound);
     real M=N-corr12 with full base+single-(1=1) basis -> INCONSISTENT (full rank).
 (4) explicit nonzero mixed 2nd-difference (cross-term) at a (1=1) matching intersection.
Build first:  g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
"""
import subprocess,sys
def run(m): 
    print("\n==== "+m+" ===="); sys.stdout.flush()
print("see: r5_getQ.py (extract Q), r5_corr.py (corr12, M (1=2)-smoothness),")
print("     r5_Mfit.py (M not simple), r5_control.py (machinery sound), r5_crossterm.py (cross-term),")
print("     pybg.py (independent evaluator). This script runs the load-bearing checks.")
import r5_verify   # (1) pybg==bg, (2) M (1=2)-smooth
print("\n--- box-spline control + M-fit (this takes ~1-2 min) ---", flush=True)
import r5_control   # control: simple spline CONSISTENT
