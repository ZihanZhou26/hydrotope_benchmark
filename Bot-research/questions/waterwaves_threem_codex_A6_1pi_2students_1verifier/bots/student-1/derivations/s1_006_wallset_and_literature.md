# Claim `s1_006`: the subset-momentum wall set reduces to the joint \(q/Q\) arrangement

## Exact kinematic enumeration

Write \(x_i=\omega_i^2>0\), \(M=\{1,2,3\}\), and
\(P=\{4,5,6\}\).  For a subset \(S\), let
\[
a=|S\cap M|,\qquad b=|S\cap P|.
\]
Then
\[
k_S=-\sum_{m\in S\cap M}x_m+\sum_{p\in S\cap P}x_p,
\qquad k_S=-k_{S^c}
\]
on the resonant manifold.  A same-sector subset has a strict sign, so it
cannot define a wall away from an external soft limit.  The mixed types,
modulo complementation \((a,b)\leftrightarrow(3-a,3-b)\), reduce as follows:

| subset type | complement type | wall representative |
|---|---|---|
| \((1,1)\) | \((2,2)\) | \(q_{mp}=x_p-x_m=0\), \(3\cdot3=9\) walls |
| \((1,2)\) | \((2,1)\) | \(Q_{m;pq}=x_p+x_q-x_m=0\), \(3\binom32=9\) walls |
| \((1,3)\) | \((2,0)\) | impossible, since the complement has strict negative sign |
| \((3,1)\) | \((0,2)\) | impossible, since the complement has strict positive sign |
| \((2,3)\) | \((1,0)\) | impossible, since the complement has strict negative sign |
| \((3,2)\) | \((0,1)\) | impossible, since the complement has strict positive sign |

Thus every non-soft subset-momentum wall is in exactly one of the two
\(S_3(M)\times S_3(P)\) orbits
\[
\boxed{\{q_{mp}=0\}_{9}\ \cup\ \{Q_{m;pq}=0\}_{9}.}
\]
This proves kinematic completeness of the candidate 18-wall set.  It does
not by itself prove that the pole-subtracted BG remainder is one polynomial
on every open component; the exact degree-eight reconstruction battery for
that empirical statement is running separately.

## Public-literature check on 2026-07-26

The primary 2026 paper *Surface Water Wave Scattering and the Hydrotope*
derives only the two-minus formula.  It states that the independent
three-minus sector begins at six points and “will be investigated in future
work”; its bibliography lists *Surface water wave amplitudes and the
hydrohedron* only as “to appear.”  Searches of arXiv by the exact title,
“hydrohedron,” “three-minus,” and the author list found no public sequel.

The authors' linked public repository describes itself only as numerical
Berends--Giele recursion code and presently contains `Hydrotope.wl` plus a
README; it exposes no compact three-minus numerator or joint-fan
wall-crossing rule.

The published hydrotope derivation does supply a useful structural template:
Fourier representation of a single slice constraint factorizes the box-edge
integrals, whose inclusion--exclusion expansion produces one-variable
truncated powers.  But the paper contains no two-dimensional hydrohedron
integrand or cocycle that would determine the coupled \(q/Q\) assembly here.
No unverified crossing rule from the literature is therefore imported.

Primary sources:

- https://arxiv.org/abs/2606.28280
- https://github.com/ZihanZhou26/Hydrotope

## Correction to earlier student state

The attribution in `s1_004` of a particular \(H_{24}\) branch exchange to a
\(Q\)-wall was incorrect; the PI and verifier located that narrow exchange
at the magnitude tie \(q_{35}=0\).  Conversely, the later blanket exclusion
of all \(Q\)-walls was also incorrect: the round-4 verifier and
`pi_vchk_003` independently established genuine order-three jumps across
\(Q_{m;pq}=0\).  The correct global candidate fan is the joint 18-wall set
above.
