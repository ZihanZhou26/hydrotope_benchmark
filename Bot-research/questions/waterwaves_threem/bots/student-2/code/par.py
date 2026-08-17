#!/usr/bin/env python3
"""Parallel exact oracle batch (64 cores). on_shell_batch(queries) -> list of
(im or None, oms or None) preserving order. None on SIGFPE/wall."""
import subprocess, re, os
from fractions import Fraction as F
from concurrent.futures import ProcessPoolExecutor
HERE=os.path.dirname(os.path.abspath(__file__)); BG=os.path.join(HERE,"bg")

def _one(arg):
    free,signs=arg
    n=len(signs)
    cmd=[BG,"-n",str(n),"-w",",".join(str(x) for x in free),
         "-s",",".join(str(int(s)) for s in signs),"-g","1"]
    try:
        out=subprocess.check_output(cmd,stderr=subprocess.DEVNULL).decode()
    except Exception:
        return (None,None)
    m=re.search(rf"A_{n} = i \* \(([-0-9/]+)\)",out)
    if m: im=F(m.group(1))
    else:
        m2=re.search(rf"A_{n} = \(([-0-9/]+)\) \+ i \* \(([-0-9/]+)\)",out)
        if not m2: return (None,None)
        im=F(m2.group(2))
    oms=[F(x.strip()) for x in re.search(r"omega = \{([^}]+)\}",out).group(1).split(",")]
    return (im,oms)

def on_shell_batch(queries, workers=48):
    with ProcessPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(_one,queries,chunksize=1))
