# H1 fitting report
Generated at 2026-07-26T05:55:29 UTC

## H1 ansatz tested
For each sign choice $(e_m,e_p)$ and pair $(a,b)$ in $\{(0,1),(0,2),(1,2)\}$,
$$\Phi_{ab}^{e_m,e_p}=\omega_a\omega_b\sum_{S\subseteq\{r\}\cup\{3,4,5\}}(-1)^{|S|}[\theta - e_m\mathbf 1_{r\in S}\,\omega_r^2 - e_p\sum_{j\in S\cap\{3,4,5\}}\omega_j^2]_+^3,$$
$$A_6/i = C\sum_{a<b}\Phi_{ab}^{e_m,e_p}$$
Pair diagnostics used the labeled equation
$$A_6/i = C_{01}\Phi_{01}^{e_m,e_p}+C_{02}\Phi_{02}^{e_m,e_p}+C_{12}\Phi_{12}^{e_m,e_p}$$

## Anchors
- anchor checks:
  - seed_2_3_4_5: ω=['-8', '2', '3', '4', '5', '-6'], A6=i*(-9190656/7)
  - seed_3_5_2_7: ω=['-154/17', '3', '5', '2', '7', '-135/17'], A6=i*(-641893056/85)

- samples: 80
- chamber signature count: 15
## Common coefficient test
- e_m=1,e_p=1: no_common_coeff ref=s0027 w=s0006 C=9991840/123291 residual=2299082631233536/1164415
- e_m=1,e_p=-1: no_common_coeff ref=s0027 w=s0006 C=-999184/164763 residual=-245241501175939072/79360845
- e_m=-1,e_p=1: no_common_coeff ref=s0027 w=s0006 C=-2497960/522171 residual=-47374692244307968/19347105
- e_m=-1,e_p=-1: no_common_coeff zero_train_phi_with_nonzero_amp
## Pair coefficient diagnostics
- e_m=1,e_p=1: no_exact_pair_coeff rank(A)=3 rank([A|y])=4 witness={'type': 'inconsistent_row', 'sample_id': 's0066', 'residual': '1628067343045088/39896535'}
- e_m=1,e_p=-1: no_exact_pair_coeff rank(A)=3 rank([A|y])=4 witness={'type': 'inconsistent_row', 'sample_id': 's0027', 'residual': '6622724737/47858688'}
- e_m=-1,e_p=1: no_exact_pair_coeff rank(A)=3 rank([A|y])=4 witness={'type': 'inconsistent_row', 'sample_id': 's0066', 'residual': '794042748231116672/42818177865'}
- e_m=-1,e_p=-1: no_exact_pair_coeff rank(A)=0 rank([A|y])=1 witness={'type': 'inconsistent_row', 'sample_id': 's0027', 'residual': '312245/2304'}
## Fallback feature fit
- status=no_exact_fit
- rank(A)=14 rank([A|y])=15
- heldout 0/40
## Invariance checks
- s0000: oracle=True h1=True
- s0001: oracle=True h1=True
- s0002: oracle=True h1=True
- s0003: oracle=True h1=True
- s0004: oracle=True h1=True
- s0005: oracle=True h1=True
- s0006: oracle=True h1=True
- s0007: oracle=True h1=True
