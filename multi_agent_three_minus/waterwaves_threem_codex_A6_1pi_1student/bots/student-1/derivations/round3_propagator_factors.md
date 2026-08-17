# Exact pair and triple propagator factors

Set $g=1$ and write

$$
h_S=\omega_S^2-|q_S|,
\qquad
q_S=\sum_{i\in S}\sigma_i\omega_i^2 .
$$

The scalar part of the BG propagator is $|q_S|/h_S$.  The following
factorizations are direct polynomial identities and are useful constraints on
any reconstructed denominator of
$H=A_6/(i\prod_i\omega_i)$.

## Two-leg subsets

For two legs of the same momentum sign, with frequencies $x,y$,

$$
h_{\{x,y\}}=(x+y)^2-x^2-y^2=2xy.
$$

For one minus leg $x$ and one plus leg $y$, put $q=y^2-x^2$.  Then

$$
\frac{|q|}{h}=
\begin{cases}
\dfrac{y-x}{2x},&q>0,\\[4pt]
\dfrac{x-y}{2y},&q<0.
\end{cases}
$$

Thus the apparent factor $x+y$ cancels identically in every non-wall
two-leg propagator.  Its only remaining denominators are external
frequencies, which are precisely the factors already peeled off in
$A_6=i(\prod_i\omega_i)H$.

## Mixed three-leg subsets

Take two minus-leg frequencies $x,y$ and one plus-leg frequency $z$.
Then

$$
q=z^2-x^2-y^2.
$$

On the two sides of the associated $S$ wall,

$$
h=
\begin{cases}
2(x+z)(y+z),&q<0,\\[4pt]
2\bigl(x^2+y^2+xy+z(x+y)\bigr),&q>0.
\end{cases}
$$

For the physical indexing
$S=(M\setminus\{\ell\})\cup\{3+j\}$ this branch variable is exactly

$$
q=a_\ell+b_j-T=S_{\ell j}.
$$

Consequently the $S_{\ell j}$ signs do more than label a generic absolute
value: they select between a product of two mixed frequency sums and an
irreducible homogeneous quadratic.  A proposed common denominator for $H$
must reproduce or cancel this branch behavior.

For the all-minus and all-plus triple channels, conservation gives the same
pair elementary symmetric polynomial $p$, and

$$
h_{\{1,2,3\}}=h_{\{4,5,6\}}=2p.
$$

All displayed identities were expanded symbolically and also follow by direct
substitution into $h_S=\omega_S^2-|q_S|$.
