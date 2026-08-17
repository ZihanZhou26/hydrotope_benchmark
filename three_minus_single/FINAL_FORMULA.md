# Closed form for the three-minus sector

This gives a nonrecursive closed analytic formula for the full tree amplitude in
the sector

```text
sigma = (-1,-1,-1,+1,...,+1),  n >= 5.
```

The formula is written first at `g = 1`.  For general gravity,

```text
A_n(omega; g) = g^(3-n) A_n(omega; 1),
```

with the same frequencies and with physical momenta
`k_i = sigma_i omega_i^2/g`.  In the formula below set

```text
hat k_i = -omega_i^2,  i = 1,2,3,
hat k_i = +omega_i^2,  i = 4,...,n,
```

and impose the on-shell conservation laws

```text
sum_i omega_i = 0,        sum_i hat k_i = 0.
```

## Ordered closed kernel

For an ordered list of `m >= 3` momenta `p = (p_1,...,p_m)` with
`sum_a p_a = 0`, define

```text
P_nu = sum_{a=2}^nu p_a,        2 <= nu <= m.
```

For a chain

```text
2 = nu_0 < nu_1 < ... < nu_l <= m
```

let the empty chain have `l = 0` and last element `nu_l = 2`.  The closed
one-dimensional Lagrangian kernel is

```text
F_m(p_1,...,p_m)
 =
 - 1/|p_2| *
 sum_{2=nu_0<nu_1<...<nu_l<=m}
   |P_{nu_l}|^(m-nu_l)/(m-nu_l)!
   prod_{j=1}^l [
     - |P_{nu_{j-1}}|^(nu_j-nu_{j-1}-1)
       /( (nu_j-nu_{j-1}-1)! |P_{nu_j}| )
       * ( P_{nu_{j-1}} p_{nu_j}
           + |P_{nu_{j-1}}|^2/(nu_j-nu_{j-1}) )
   ].
```

The sum is finite: equivalently, choose any subset of `{3,...,m}` and sort it
after the initial entry `2`.  This is the closed chain form of the water-wave
kernel; no recursive `EKernel/FKernel` definition is part of the formula.

The symmetric `m`-point contact vertex is

```text
V_m(q_1,...,q_m; O_1,...,O_m)
 =
 - i/2 * sum_{pi in S_m} O_{pi(1)} O_{pi(2)}
          F_m(q_{pi(1)},...,q_{pi(m)}),
```

where `sum_a q_a = sum_a O_a = 0`.

The scalar propagator for a line carrying total frequency `O` and total
dimensionless momentum `K` is

```text
P(O,K) = -i / ( O^2/|K| - 1 ).
```

## Stable-tree amplitude formula

Let `T_n` be the finite set of connected acyclic trees with `n` labeled leaves
`1,...,n`, all internal vertices having valence at least three.  For a tree
`T in T_n`, an internal vertex `v`, and an incident half-edge `h`, remove `v`
from the tree along `h`; let `I(v,h)` be the set of external labels in the
component reached through `h`.  Define

```text
K(v,h) = sum_{i in I(v,h)} hat k_i,
O(v,h) = sum_{i in I(v,h)} omega_i.
```

For an internal edge `e`, choose either side of the cut and call its label set
`I_e`; then

```text
K_e = sum_{i in I_e} hat k_i,
O_e = sum_{i in I_e} omega_i.
```

The propagator is independent of which side is chosen because it depends only
on `O_e^2` and `|K_e|`.

The complete three-minus amplitude is

```text
A_n^{---+...+}(omega;1)
 =
 sum_{T in T_n}
   [ prod_{v internal in T}
       V_{deg(v)}( {K(v,h)}_{h incident to v};
                   {O(v,h)}_{h incident to v} )
   ]
   [ prod_{e internal in T} P(O_e,K_e) ].
```

This is a closed finite sum over stable trees, permutations at each vertex, and
kernel chains.  It is valid for every `n >= 5` and every on-shell
three-minus kinematic point, with the pole and wall prescriptions below.

## Chambers and poles

The chamber hyperplanes are

```text
K_I = sum_{i in I} hat k_i = 0,
```

for nonempty proper subsets `I` of `{1,...,n}`; by complementarity `I` and
`I^c` define the same wall.  On any open chamber, all signs `sgn(K_I)` are
fixed, so every absolute value in the formula is replaced by a signed linear
form and the answer is a rational function of the `omega_i`.

The physical factorization poles are

```text
Delta_I = O_I^2/|K_I| - 1 = 0,
O_I = sum_{i in I} omega_i,
K_I = sum_{i in I} hat k_i,
```

for subsets that can appear as an internal edge, i.e. `2 <= |I| <= n-2`.
Near such a pole,

```text
A_n = -i A_L A_R / Delta_I + regular,
```

where the two lower amplitudes are evaluated by the same stable-tree formula
with the two internal half-legs carrying `(-O_I,-K_I)` and `(O_I,K_I)`.
If either lower side is a one-minus sector, its factor vanishes.

At a chamber wall `K_I = 0` that is not a physical pole, the value is the
finite limit of the displayed formula from the adjacent chamber(s).  If an
intermediate `|P_nu|` in the closed kernel vanishes, use this same limiting
prescription for the chain expression.  At a physical pole the amplitude is
meromorphic and diverges with the factorization residue above.

## Five-point reduction

For `n = 5`, parity maps the three-minus sector to the two-minus hydrotope
sector.  The stable-tree formula reduces to

```text
A_5^{---++}
 =
 i * 16 * omega_4 * omega_5
   sum_{S subset {1,2,3}} (-1)^|S|
     ( beta^2 - sum_{j in S} omega_j^2 )_+^2,

beta = min(|omega_4|, |omega_5|),       (x)_+ = max(x,0).
```

## Verification

I built the supplied oracle and an independent local evaluator
`formula_eval` whose only kernel input is the closed chain formula above
(`bg_formula.cpp`; it does not use the recursive `EKernel/FKernel` bodies).
The script `verify_formula.sh` compares exact amplitude lines from `./bg` and
`./formula_eval`.

```text
n=5 generic residual: 0 exact (A_5 = i * (-1024))
n=5 parity chamber residual: 0 exact (A_5 = i * (-25344))
n=6 generic residual: 0 exact (A_6 = i * (-135168/5))
n=6 soft/near-pole residual: 0 exact (A_6 = i * (-11637095623376/190919368605))
n=6 asymmetric residual: 0 exact (A_6 = i * (-618237598072/332353125))
n=7 generic residual: 0 exact (A_7 = i * (-18623104/35))
n=7 asymmetric residual: 0 exact (A_7 = i * (-1119330324932544092637064/14855436204225083775))
```

The corresponding commands use:

```text
g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
g++ -O2 -std=c++17 -o formula_eval bg_formula.cpp -lgmpxx -lgmp
./verify_formula.sh
```

References used for the closed kernel and context:

```text
N. Arkani-Hamed, F. Calisto, N. Ussembayev, W. W. Zhao, Z. Zhou,
"Surface Water Wave Scattering and the Hydrotope", arXiv:2606.28280 (2026),
especially Supplemental Eq. (S6) for the closed kernel.

F. A. Berends and W. T. Giele,
"Recursive Calculations for Processes with n Gluons",
Nucl. Phys. B 306 (1988) 759-808.
```
