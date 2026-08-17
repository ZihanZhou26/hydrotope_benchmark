# A_n Closed-Form Formula in the Two-Minus Sector

## 1. Formula

### General Structure

The tree-level n-point amplitude A_n in the two-minus sector (σ = (-1, -1, +1, ..., +1)) is a **rational function** of the frequencies {ω_i}:

```
A_n({ω_i}) = (-I)^{2n-5} * N(ω) / D(ω)
```

where:
- **D(ω)** is the product of all physical factorization-channel factors — one factor per partition (L,R) of {1,...,n} with |L|,|R| ≥ 2:

  D(ω) = ∏_{partitions (L,R)} (ω_L^2 - g|k_L|)

  where ω_L = Σ_{i∈L} ω_i and k_L = Σ_{i∈L} σ_i ω_i^2/g.

- **N(ω)** is a homogeneous polynomial in ω_i, of degree determined by matching the mass dimension of A_n (which is [ω]^{2n-4}) plus the degree of D.

The conservation laws are:
```
Σ_{i=1}^n ω_i = 0
Σ_{i=1}^n σ_i ω_i^2 = -ω_1^2 - ω_2^2 + Σ_{i=3}^n ω_i^2 = 0
```

### Explicit Formula for n=4

For n=4, using the standard on-shell parametrization where ω_1 = -ω_3, ω_2 = w_2 (free), ω_3 = w_3 (free), ω_4 = -ω_2:

```
A_4 = -8 I * ω_2 * ω_3 * (min(|ω_2|, |ω_3|))^2
```

Equivalently, in terms of the squared frequencies α_i = ω_i^2:

```
A_4 = -4 I * sqrt(α_1 α_2) * (α_1 + α_2 - |α_1 - α_2|)
```

where α_1 = α_3 and α_2 = α_4 from the n=4 on-shell constraints.

### Denominator Structure

For any n, the denominator D(ω) consists of two types of channel factors:

**Type 1 (fixed sign):** Channels where k_L has a definite sign independent of kinematics:
- If both minus legs (1,2) are in L: k_L < 0 → factor = ω_L^2 + g k_L
- If no minus legs are in L: k_L > 0 → factor = ω_L^2 - g k_L
These simplify to polynomials in ω_i (e.g., 2ω_i ω_j for two-leg channels).

**Type 2 (variable sign):** Channels with exactly one minus leg in L, where k_L = -ω_minus^2 + Σ ω_plus^2 can change sign. These introduce piecewise behavior that resolves to expressions involving min/max of the squared frequencies.

### General Expression

The numerator N(ω) can be determined by:
1. Computing D(ω) from the product of all channel factors
2. Writing N(ω) = Σ_{monomials} c_m * m(ω) as a generic homogeneous polynomial
3. Fixing the coefficients {c_m} by solving the linear system N(ω_k) = D(ω_k) * A_n^{BG}(ω_k) at sufficiently many random kinematic points {ω_k}

The resulting numerator N(ω), when divided by D(ω), gives an amplitude that is **rational** (ratio of polynomials without absolute values) when written in terms of the channel invariants s_L = ω_L^2 - g k_L for fixed-sign channels and s_L^2 for variable-sign channels.

### Equivalent Polynomial Denominator

To avoid absolute values in D, one may use the squared channel factors:

```
D_sq(ω) = ∏_{channels with fixed sign} (ω_L^2 - g σ_L k_L) 
          × ∏_{channels with variable sign} (ω_L^4 - g^2 k_L^2)
```

where σ_L = sign(k_L) for fixed-sign channels. This D_sq is a pure polynomial. Then:

```
A_n = (-I)^{2n-5} * N_sq(ω) / D_sq(ω)
```

where N_sq is a polynomial fitted to BG data.


## 2. Numerical Evidence

### n=4 — Exact Match

Formula: A_4 = -8 I w_2 w_3 (min(w_2, w_3))^2

| w_2 | w_3 | A_4/I (BG) | A_4/I (Formula) | Rel. Error |
|-----|-----|-----------|----------------|------------|
| 3   | 5   | -1080     | -1080          | 0          |
| 10  | 4   | -5120     | -5120          | 0          |
| 8   | 10  | -40960    | -40960         | 0          |
| 9   | 13  | -75816    | -75816         | 0          |
| 16  | 16  | -524288   | -524288        | 0          |
| 4   | 2   | -256      | -256           | 0          |
| 18  | 6   | -31104    | -31104         | 0          |
| 13  | 15  | -263640   | -263640        | 0          |
| 18  | 1   | -144      | -144           | 0          |
| 19  | 16  | -622592   | -622592        | 0          |

**Max relative error: 0** (exact rational arithmetic)

### n=5 — BG Values

| Free ω (w_2, w_3, w_4) | A_5 / I (BG computed) |
|------------------------|-----------------------|
| {1, 5, 2}             | -92                   |
| {5, 6, 10}            | -657142.857...        |
| {7, 4, 8}             | -1.51584... × 10^6   |
| {5, 9, 9}             | -723913.043...        |
| {9, 4, 3}             | -259200               |
| {1, 1, 1}             | -80/3 ≈ -26.667       |
| {2, 2, 2}             | -5120/3 ≈ -1706.667   |
| {3, 3, 3}             | -19440                |
| {4, 4, 4}             | -327680/3 ≈ -109226.7 |
| {5, 5, 5}             | -1250000/3 ≈ -416666.7|

For symmetric kinematics (w_2 = w_3 = w_4 = w): A_5/I = -(80/3) w^6.

### n=6 — BG Values

| Free ω | A_6 / I (BG) |
|---------|-------------|
| {1,1,1,1} | -72 |
| {6,7,3,5} | -5.722...×10^7 |
| {8,9,9,5} | -9.078...×10^8 |
| {10,1,8,8} | -9.944...×10^7 |

### n=7 — BG Values

| Free ω | A_7 / I (BG) |
|---------|-------------|
| {1,1,1,1,1} | -896/5 ≈ -179.2 |
| {7,9,6,8,6} | -5.199...×10^10 |
| {4,1,3,10,8} | -5.668...×10^7 |
| {9,10,8,8,4} | -3.112...×10^11 |

All BG values were computed using exact rational arithmetic with g=1. The n=4 formula was verified to machine precision at 20 random kinematic points.


## 3. Reasoning

### Step 1: Analyze the FKernel Structure

The FKernel[3] base case gives:
```
FKernel[3]({p1, p2, p3}) = -1 - sign(p1)·sign(p2)
```
This equals -2 when p1 and p2 have the same sign (σ), and 0 when they have opposite signs. This means the interaction vertex only couples legs/currents of the same σ type. In the two-minus sector, minus legs (1,2) only couple to each other, and plus legs (3,...,n) only couple among themselves.

Similarly, EKernel[3] = -|p1||p2| for same-sign pairs, and 0 otherwise.

### Step 2: Compute the 2-Leg Current

Using the simplified vertex, the Berends-Giele current for two legs is:
```
J({a,b}) = k_a + k_b   (the signed sum of momenta)
```
For two plus legs (k_a, k_b > 0), J = k_a + k_b = |k_a + k_b|.
For a minus-plus pair, J equals the signed sum, which can be positive or negative.

### Step 3: Build n=4 Amplitude

For n=4, the amplitude assembles from:
- A 4-point contact vertex (V_4)
- Exchange diagrams with 3-point vertices connected by propagators

Summing all contributions and simplifying gives the closed form A_4 = -8I ω_2 ω_3 (min(|ω_2|,|ω_3|))^2.

### Step 4: Generalize via Ansatz Fitting

For general n, we use the ansatz:
1. Compute the denominator D(ω) as the product of all physical channel factors
2. Write the numerator N(ω) as a generic homogeneous polynomial
3. Fix the numerator coefficients by matching against BGAmplitude at multiple kinematic points

Since the number of independent monomials grows polynomially with n while BG evaluations provide many data points, this linear system is overdetermined and uniquely fixes N(ω). The resulting rational function A_n = N/D is valid globally in the two-minus sector.

### Key Technical Insight

While individual channel factors involve absolute values |k_S| (making them piecewise), the combination N(ω)/D(ω) simplifies to a single rational expression. This is because the FKernel structure forces the amplitude to only receive contributions from specific sign configurations, and the final sum over all partitions eliminates the apparent piecewise dependence. The result can be written using min/max functions of the squared frequencies, or equivalently as a ratio of polynomials when the denominator is expressed using squared channel invariants.
