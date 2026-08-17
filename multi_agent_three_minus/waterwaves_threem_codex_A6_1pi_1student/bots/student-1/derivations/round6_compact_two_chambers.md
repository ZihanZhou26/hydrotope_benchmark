# Round 6: compact numerator and denominator in two opposite chambers

## Setup

Choose the chart which eliminates legs \(1\) and \(6\), and put

$$
(u,v,r,s)=(\omega_2,\omega_3,\omega_4,\omega_5),\qquad
\Omega=u+v+r+s ,
$$

$$
m_1=u+v,\quad m_2=uv,\qquad p_1=r+s,\quad p_2=rs .
$$

Define the four mixed-pair factor and the two signed propagator branches

$$
L=(u+r)(u+s)(v+r)(v+s),
$$

$$
B_M=\frac{\Omega^2-K}{2}
    =e_2(u,v,r,s)+u^2+v^2,\qquad
B_P=\frac{\Omega^2+K}{2}
    =e_2(u,v,r,s)+r^2+s^2,
$$

where \(K=r^2+s^2-u^2-v^2\).  Hence

$$
B_M+B_P=\Omega^2,\qquad
4B_MB_P=\Omega^4-K^2
       =(\Omega^2-|K|)(\Omega^2+|K|).
$$

These identities are polynomial identities.  For any omitted minus leg
\(p\) and omitted plus leg \(q\), the same construction on the remaining
two minus and two plus legs gives one of the nine members of a single
\(S_3\times S_3\) orbit.  Minus/plus swap exchanges \(B_M\leftrightarrow B_P\).

## The 31-term core

The degree of the core in the PI's exact `factorP` output is **nine**, not
eight: the displayed monomial \(u^4r^4s\) already has degree nine.  After
homogenizing, the core is separately symmetric in \((u,v)\) and \((r,s)\).
It is the following weighted-degree-nine polynomial, where
\(\deg m_1=\deg p_1=1\) and \(\deg m_2=\deg p_2=2\):

$$
\begin{aligned}
F={}&2m_1^4p_1^3p_2-4m_1^4p_1p_2^2
+3m_1^3p_1^4m_2+4m_1^3p_1^4p_2
-7m_1^3p_1^2m_2p_2-10m_1^3p_1^2p_2^2+4m_1^3p_2^3\\
&+6m_1^2p_1^5m_2+2m_1^2p_1^5p_2
+3m_1^2p_1^3m_2^2-22m_1^2p_1^3m_2p_2
-4m_1^2p_1^3p_2^2-7m_1^2p_1m_2^2p_2
+17m_1^2p_1m_2p_2^2\\
&+3m_1p_1^6m_2-13m_1p_1^4m_2p_2
+2m_1p_1^4p_2^2-m_1p_1^2m_2^2p_2
+15m_1p_1^2m_2p_2^2-6m_1p_1^2p_2^3\\
&+2m_1m_2^2p_2^2-6m_1m_2p_2^3+4m_1p_2^4
-3p_1^5m_2^2+2p_1^5m_2p_2-3p_1^3m_2^3
+14p_1^3m_2^2p_2-9p_1^3m_2p_2^2\\
&+7p_1m_2^3p_2-16p_1m_2^2p_2^2+9p_1m_2p_2^3 .
\end{aligned}
$$

An exact coefficient-basis solve reduces each 110-monomial expanded core to
31 nonzero terms in the 70-dimensional weighted-degree-nine pair-invariant
basis.  Direct simultaneous substitutions verify

$$
C_A(u,v,r,s)=C_A(v,u,r,s)=C_A(u,v,s,r),
$$

and the other exact fitted core is not independent:

$$
C_B(u,v,r,s)=C_A(r,s,u,v)
            =F(p_1,m_1,p_2,m_2).
$$

## Compact formula in the two reconstructed pieces

Let

$$
H=\frac{A_6}{i\prod_{\ell=1}^6\omega_\ell}.
$$

Combining the exact normalizations in `round6_QP.txt`,
\(P_A=yz(1+x+y+z)F/2\) and \(Q_A=-xU/64\), gives

$$
\boxed{
H_A=-32\,\frac{rs\,\Omega\,F(m_1,p_1,m_2,p_2)}
{uv\,L\,B_MB_P}}
$$

in the true piece containing
\((-7,9,-8,-3,-4,13)\).  Here all four chart comparisons
\(u^2-r^2,u^2-s^2,v^2-r^2,v^2-s^2\) are positive.

Likewise `round6_QP_B.txt` has
\(P_B=x(1+x+y+z)F_{\rm swap}/3\) and \(Q_B=-yzU/96\), so

$$
\boxed{
H_B=-32\,\frac{uv\,\Omega\,F(p_1,m_1,p_2,m_2)}
{rs\,L\,B_MB_P}}
$$

in the true piece containing
\((-13,4,3,8,7,-9)\).  All four chart comparisons are negative.
In either piece \(A_6=i(\prod_\ell\omega_\ell)H\).

Thus the denominator has the same universal \(L B_MB_P\); the complete
minus/plus swap exchanges the numerator and denominator single-leg products
and sends \(F\) to its one swap-orbit partner.  This is a compact analytic
construction for these two opposite chambers, not yet the full-domain answer.

## Verification and remaining issue

`bots/student-1/code/bg_s1_r6` was freshly built from the student copy of
`bg.cpp`.  For each base above, twelve deterministic rational perturbations

$$
(u,v,r,s)\longmapsto
(u+t/1000,\ v+2t/1000,\ r-t/1000,\ s+3t/1000),
\qquad t=1,\ldots,12,
$$

remain in the same full 53-sign piece.  Both conservation equations held
exactly, and the boxed formula agreed with exact-GMP BG on \(24/24\) samples
with zero rational residual.  The modular rank and signed rational
reconstruction unit tests also pass.

The rule for interleaved \(2\times2\) comparison matrices is still unknown.
The exact three-new-piece scan is registered as the nonblocking job
`r6_piece_20260726T173931Z`.  It tests every square-free visible single-leg
set after multiplying by \(LB_MB_P\).  Wall and factorization-limit tests must
wait for those additional pieces; no full-domain claim is made here.
