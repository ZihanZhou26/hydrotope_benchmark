#!/usr/bin/env python3
"""Test 2 (lean): orbit + selector-branch coverage. Independent."""
import itertools, sys
from fractions import Fraction as F
from r5_lines import gen_int_lines, extract
from r5_core import line, Q_T_val, M, P

def pr(*a): print(*a); sys.stdout.flush()

lines,dirs = gen_int_lines()
seen=set(); uniq=[]
for Pv,dv in lines:
    key=(tuple(Pv),tuple(dv))
    if key in seen: continue
    seen.add(key); uniq.append((Pv,dv))
pr(f"{len(uniq)} unique integer on-shell lines available")

tested=0; ok_all=True; sel_kinds={}; channels_hit=set(); FAILS=[]
TARGET_CH=8; TARGET_WT2=2; MAX_LINES=12
nlines=0
for Pv,dv in uniq:
    if len(channels_hit)>=TARGET_CH and len(sel_kinds.get("wt2",[]))>=TARGET_WT2: break
    if nlines>=MAX_LINES: break
    used_this_line=False
    for m in M:
        for p,q in itertools.combinations(P,2):
            vals=[Q_T_val(line(Pv,dv,F(t,2)),m,p,q) for t in range(-6,7)]
            if not (any(v>0 for v in vals) and any(v<0 for v in vals)): continue
            # prefer NEW channels or a wt2 hunt
            need_wt2 = len(sel_kinds.get("wt2",[]))<TARGET_WT2
            if (m,p,q) in channels_hit and not need_wt2: continue
            out=extract(Pv,dv,m,p,q,verbose=False)
            if not out.get("ok"): continue
            for r in out["results"]:
                if not r.get("ok"): continue
                tested+=1; used_this_line=True; channels_hit.add((m,p,q))
                good=(r["badL"]==0 and r["badR"]==0 and r["rem_zero"] and r["quot_deg"]<=2
                      and r["selector_ok"] and not r["div_by_Q4"] and r["badA"]==0)
                for k in r["sel_kind"]: sel_kinds.setdefault(k,[]).append((Pv,dv,m,p,q,r["t0"]))
                tag=" ".join(r["sel_kind"])
                pr(f"  ch({m+1};{p+1},{q+1}) t0={r['t0']:+.3f} P={Pv} d={dv}: "
                   f"badL={r['badL']} badR={r['badR']} remQ3=0?{r['rem_zero']} qdeg={r['quot_deg']} "
                   f"sel?{r['selector_ok']}[{tag}] divQ4?{r['div_by_Q4']} RmQsmooth_bad={r['badA']} -> {'OK' if good else 'FAIL'}")
                if not good: ok_all=False; FAILS.append((Pv,dv,m,p,q,r))
    if used_this_line: nlines+=1

pr("\n================ SUMMARY ================")
pr("distinct channels:", sorted((m+1,p+1,q+1) for (m,p,q) in channels_hit), f"[{len(channels_hit)}/9]")
pr("total extractions:", tested, " all passed:", ok_all, " fails:", len(FAILS))
pr("selector branches realized:", {k:len(v) for k,v in sel_kinds.items()})
if "wt2" in sel_kinds:
    ex=sel_kinds["wt2"][0]
    pr("example w_t^2 selector: P=%s d=%s ch(%d;%d,%d) t0=%.3f"%(ex[0],ex[1],ex[2]+1,ex[3]+1,ex[4]+1,ex[5]))
