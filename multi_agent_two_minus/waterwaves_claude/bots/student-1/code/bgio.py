"""Harness to drive the local oracle copy ./bg (student-1).

Two-minus sector helpers. All exact-rational unless double=True.
Returns a_n where A_n = i * a_n (Re A_n is verified == 0 in exact mode).
"""
import subprocess, re, os
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BG = os.path.join(HERE, "bg")

def _run(args):
    p = subprocess.run([BG]+args, capture_output=True, text=True)
    return p

def _parse_exact(out):
    """Parse exact-rational stdout -> (omega list[Fraction], a_n Fraction, re_zero bool)."""
    om = None
    a_im = None
    re_zero = None
    for line in out.splitlines():
        m = re.match(r"omega = \{(.*)\}", line)
        if m:
            om = [Fr(x.strip()) for x in m.group(1).split(",")]
        m = re.match(r"A_\d+ = i \* \((.*)\)", line)
        if m:
            a_im = Fr(m.group(1)); re_zero = True
        m = re.match(r"A_\d+ = \((.*)\) \+ i \* \((.*)\)", line)
        if m:
            a_im = Fr(m.group(2)); re_zero = (Fr(m.group(1))==0)
    return om, a_im, re_zero

def _parse_double(out):
    om=None; rev=None; im=None
    for line in out.splitlines():
        m = re.match(r"omega = \{(.*)\}", line)
        if m:
            om=[float(x) for x in m.group(1).split(",")]
        m = re.match(r"A_\d+ \(double\) = (\S+) \+ (\S+) i", line)
        if m:
            rev=float(m.group(1)); im=float(m.group(2))
    return om, rev, im

def onshell(n, freew, signs=None, double=False, g=1):
    """-n mode. freew: list of n-2 free freqs (str/Fraction/int). signs default two-minus."""
    if signs is None:
        signs = [-1,-1]+[1]*(n-2)
    ws = ",".join(str(x) for x in freew)
    ss = ",".join(str(x) for x in signs)
    args = (["--double"] if double else [])+["-n",str(n),"-w",ws,"-s",ss,"-g",str(g)]
    p=_run(args)
    if p.returncode!=0:
        return {"ok":False,"rc":p.returncode,"stderr":p.stderr,"stdout":p.stdout}
    if double:
        om,re,im=_parse_double(p.stdout)
        return {"ok":True,"omega":om,"re":re,"im":im}
    om,a,rz=_parse_exact(p.stdout)
    return {"ok":True,"omega":om,"a":a,"re_zero":rz}

def amp(K, W, double=False, g=1):
    """--amp raw mode. K,W: lists length n (str/Fraction/int)."""
    ks=",".join(str(x) for x in K); Ws=",".join(str(x) for x in W)
    args=(["--double"] if double else [])+["--amp","-K",ks,"-W",Ws,"-g",str(g)]
    p=_run(args)
    if p.returncode!=0:
        return {"ok":False,"rc":p.returncode,"stderr":p.stderr,"stdout":p.stdout}
    if double:
        om,re,im=_parse_double(p.stdout)
        return {"ok":True,"omega":om,"re":re,"im":im}
    om,a,rz=_parse_exact(p.stdout)
    return {"ok":True,"omega":om,"a":a,"re_zero":rz}

def amp_twominus(omega, double=False, g=1):
    """Two-minus raw amplitude for an arbitrary omega vector (NOT necessarily on-shell).
    K_i = sigma_i * omega_i^2 / g with sigma=(-1,-1,+1,...)."""
    n=len(omega)
    sig=[-1,-1]+[1]*(n-2)
    K=[Fr(sig[i])*Fr(omega[i])*Fr(omega[i])/Fr(g) for i in range(n)] if not double \
        else [sig[i]*float(omega[i])*float(omega[i])/g for i in range(n)]
    return amp(K, omega, double=double, g=g)

if __name__=="__main__":
    print("n=5 (2,3,5):", onshell(5,[2,3,5]).get("a"))
    print("n=6 (1,2,3,4):", onshell(6,[1,2,3,4]).get("a"))
