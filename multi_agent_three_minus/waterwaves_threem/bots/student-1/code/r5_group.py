#!/usr/bin/env python3
"""Symmetry group machinery: S3(minus 0,1,2) x S3(plus 3,4,5) x Z2(swap blocks).
Leg permutations as tuples perm where (perm[k]) = image position of leg k.
We act on omega by relabeling: (g.oms)[k] = oms[ginv[k]] (so leg ginv[k] sits at k).
For matching values we use: value at oms of wall W equals reference value at the
relabeled point. We provide relabel_to_ref for (1=2) and (1=1) walls.
"""
import itertools
from fractions import Fraction as F

def s3s3_elements():
    els=[]
    for pm in itertools.permutations([0,1,2]):
        for pp in itertools.permutations([3,4,5]):
            perm=list(pm)+[3+x-3 for x in pp]  # placeholder
            perm=list(pm)+list(pp)
            els.append(tuple(perm))
    return els  # 36 elements; perm[k] = where leg k goes

def z2():
    # swap minus block <-> plus block: leg0<->3,1<->4,2<->5
    return (3,4,5,0,1,2)

def compose(g,h):  # (g after h)[k] = g[h[k]]
    return tuple(g[h[k]] for k in range(6))

def full_group():
    base=s3s3_elements(); zz=z2()
    out=set(base)
    for g in base: out.add(compose(zz,g))
    return [tuple(x) for x in out]

def apply_perm(perm, oms):
    """Return relabeled oms so that leg at position k is oms[j] with perm[j]=k.
    i.e. newoms[perm[j]] = oms[j]."""
    new=[None]*6
    for j in range(6): new[perm[j]]=oms[j]
    return new

def relabel_12_to_ref(i, pair):
    """wall ('2',i,(j,k)): minus leg i, plus pair (j,k), excluded plus l.
    Find S3xS3 perm sending i->0, {j,k}->{3,4}, l->5. Returns perm (no Z2)."""
    others_m=[x for x in (0,1,2) if x!=i]
    pm=[None,None,None]; pm[i]=0; pm[others_m[0]]=1; pm[others_m[1]]=2
    j,k=pair; l=[x for x in (3,4,5) if x not in pair][0]
    pp={}; pp[j]=3; pp[k]=4; pp[l]=5
    perm=tuple([pm[0],pm[1],pm[2],pp[3],pp[4],pp[5]])
    return perm

def relabel_11_to_ref(i,j):
    """wall ('1',i,j): minus leg i, plus leg j. Send i->0, j->3, others arbitrary fixed."""
    others_m=[x for x in (0,1,2) if x!=i]
    pm=[None,None,None]; pm[i]=0; pm[others_m[0]]=1; pm[others_m[1]]=2
    others_p=[x for x in (3,4,5) if x!=j]
    pp={}; pp[j]=3; pp[others_p[0]]=4; pp[others_p[1]]=5
    return tuple([pm[0],pm[1],pm[2],pp[3],pp[4],pp[5]])

if __name__=="__main__":
    G=full_group(); print("|G|=",len(G))
    print("|S3xS3|=",len(s3s3_elements()))
    # sanity: relabel
    oms=[F(-175,17),F(2),F(3),F(5),F(7),F(-114,17)]
    p=relabel_12_to_ref(0,(3,4))
    print("ref perm identity-ish:",p, "->", apply_perm(p,oms))
