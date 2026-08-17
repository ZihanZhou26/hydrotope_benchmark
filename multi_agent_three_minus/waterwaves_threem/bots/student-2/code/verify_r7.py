#!/usr/bin/env python3
"""ONE-COMMAND check of student-2 round-7 results (own ./bg, exact where stated).

  (A) Soft recursion EXACT at n=7, both legs: lim A_7/(i w_p^2) = 8 * A_6(surviving),
      surviving = 6pt three-minus (soft plus leg) / 6pt two-minus (soft minus leg).
  (B) Single-pair residue (n>=7) is rational in the merged scale with poles ONLY at
      the sub-collision loci: Res*(5 sub-collision factors) is a degree-7 polynomial
      (mod p, cross-validated against exact Res values).
Run: python3 verify_r7.py
"""
import subprocess, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
def run(mod):
    print(f"\n########## {mod} ##########")
    r=subprocess.run([sys.executable,os.path.join(HERE,mod)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,timeout=600)
    print(r.stdout[-2000:]);
    if r.returncode!=0: print("STDERR:",r.stderr[-800:])
    return r.stdout

if __name__=="__main__":
    o1=run("r7_soft.py")
    o2=run("r7_resid_mod.py")
    okA = o1.count("EXACT match: True")>=2
    okB = ("POLYNOMIAL of degree 7" in o2) or ("polynomial degree (mod p) = 7" in o2)
    print("\n==================== SUMMARY ====================")
    print(f"(A) soft recursion exact at n=7 (both legs): {'PASS' if okA else 'FAIL'}")
    print(f"(B) residue poles = sub-collisions only (deg-7 numerator): {'PASS' if okB else 'FAIL'}")
