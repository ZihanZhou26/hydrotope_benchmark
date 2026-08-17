# Exact eight-word chamber geometry

## Definitions

Let \(M=\{1,2,3\}\) be the minus-momentum legs and
\(P=\{4,5,6\}\) the plus-momentum legs.  At a generic point, sort the six
magnitudes strictly,

\[
r_1>r_2>\cdots>r_6,\qquad r_j=|\omega_{\pi_j}|,
\]

and define its **momentum word**

\[
W=\sigma_{\pi_1}\sigma_{\pi_2}\cdots\sigma_{\pi_6}.
\]

This is a finite, permutation-invariant selection rule: labels within \(M\)
and \(P\) never enter \(W\).  The proof below is for the standard physical
sheet used by the supplied on-shell sampling prescription
\(\omega_2,\ldots,\omega_5>0\), where the solved \(\omega_1,\omega_6<0\).
Exact exploratory enumeration found the same word set on other energy-sign
sheets, but that extension is not claimed here without a sheet-independent
proof.

## Analytic parametrization and dominance inequalities

On the standard four-positive/two-negative sheet, relabeling within \(M\) and
\(P\) puts the frequencies in the form

\[
(\omega_1,\ldots,\omega_6)=(-a,b,c,d,e,-f),\qquad
a,b,c,d,e,f>0.
\]

With \(S=b+c+d+e\) and \(r=bc-de\), the two conservation equations give

\[
a=d+e+\frac{r}{S},\qquad
f=b+c-\frac{r}{S}.
\]

The following four inequalities are strict:

\[
\begin{aligned}
a-d&=\frac{e(b+c+e)+bc}{S}>0,&
a-e&=\frac{d(b+c+d)+bc}{S}>0,\\
f-b&=\frac{c(c+d+e)+de}{S}>0,&
f-c&=\frac{b(b+d+e)+de}{S}>0.
\end{aligned}
\]

Thus the negative-frequency minus leg precedes both positive-frequency plus
legs, while the negative-frequency plus leg precedes both positive-frequency
minus legs in decreasing-magnitude order.

There is also a sheet-independent filter.  Put
\(C_j=\sum_{\ell=1}^{j}\sigma_{\pi_\ell}\).  Since there are three signs of
each kind, \(C_6=0\), and summation by parts gives

\[
\sum_{j=1}^{6}\sigma_{\pi_j}r_j^2
=\sum_{j=1}^{5}C_j(r_j^2-r_{j+1}^2).
\]

Momentum conservation and strict ordering therefore require the prefix sums
\(C_j\) to attain both positive and negative values.  A word whose prefix
sums are all nonnegative or all nonpositive is impossible away from a tie.

Enumerating the linear extensions of the four dominance inequalities gives
twelve sign words.  The prefix-sum test excludes
\[
+-++--,\quad +-+-+-,\quad -+-++-,\quad -+--++,
\]
leaving exactly, on this sheet,

\[
\boxed{\mathcal W=
\{+-+--+,\ +--++-,\ +--+-+,\ +---++,\
-+++--,\ -++-+-,\ -++--+,\ -+-++-\}.}
\]

(The first excluded word above is the six-character word
\(\texttt{+-++--}\); the leading \(+\) in display math is a sign, not an
addition operator.)

Every allowed word is realized by an exact rational point.  The table gives
\((a;b,c,d,e;f)\); the actual frequencies are
\((-a,b,c,d,e,-f)\).  The last column is the exact imaginary coefficient
\(A_6/i\), evaluated with the PI's independently built exact GMP oracle
because the student-2 technician thread failed before producing its own build.

| \(W\) | \((a;b,c,d,e;f)\) | \(A_6/i\) |
|---|---|---:|
| \(+-+--+\) | \((63/8;4,5,1,6;65/8)\) | \(-35954928/11\) |
| \(+--++-\) | \((24/5;1,4,2,3;26/5)\) | \(-11267584/105\) |
| \(+--+-+\) | \((9/2;2,4,1,3;11/2)\) | \(-635328/7\) |
| \(+---++\) | \((46/11;3,5,1,2;75/11)\) | \(-2396640/77\) |
| \(-+++--\) | \((75/11;1,2,3,5;46/11)\) | \(-2396640/77\) |
| \(-++-+-\) | \((11/2;1,3,2,4;9/2)\) | \(-635328/7\) |
| \(-++--+\) | \((26/5;2,3,1,4;24/5)\) | \(-11267584/105\) |
| \(-+-++-\) | \((65/8;1,6,4,5;63/8)\) | \(-35954928/11\) |

For the standard sheet the complete codimension-one adjacency graph is
obtained by swapping adjacent opposite signs.  Its eight undirected edges are

\[
\begin{gathered}
+-+--+\leftrightarrow-++--+,\qquad
+-+--+\leftrightarrow+--+-+,\\
+--++-\leftrightarrow-+-++-,\qquad
+--++-\leftrightarrow+--+-+,\qquad
+--+-+\leftrightarrow+---++,\\
-+++--\leftrightarrow-++-+-,\qquad
-++-+-\leftrightarrow-+-++-,\qquad
-++-+-\leftrightarrow-++--+.
\end{gathered}
\]

Each edge is a mixed pair wall
\[
q_{mp}=\omega_p^2-\omega_m^2=0,\qquad m\in M,\ p\in P.
\]
At a tie, \(W\) is defined by either one-sided strict ordering; a compact
positive-part formula should supply the common limiting value without an
independent tie convention.

## Reproducibility notes

The rational representatives follow directly from the displayed
parametrization.  Substitution verifies both conservation equations exactly.
Exact oracle calls used

```text
bots/pi/code/bg -n 6 -w b,c,d,e -s -1,-1,-1,1,1,1
```

and returned the eight values tabulated above.  This is evidence for the
chamber classification, but it is not a substitute for the still-missing
student-2 brick evaluator.
