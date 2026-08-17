# Round 8 off-wall ground-truth report

## Build
- shared bg.cpp sha256: `bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`
- private bg_round8.cpp sha256: `bd1afe67c45e1e9403c03a0b78373ebb492235be56fc1e5ee9281cbbec9040c1`
- shared/private bg hashes equal: `True`
- compile success: `True`

## Anchor checks (onshell)
- A6/i = `-9190656/7`
- P_pole = `42588288/7`
- R_Q = `-136630560`
- S = `129233568`
- matches expected: {'A6': 'True', 'P_pole': 'True', 'R_Q': 'True', 'S': 'True'}

## Extracted q-wall cells
- extracted cells: 2 / 2 (physical cells)
- jump division exact checks: 2/2

### MPPM (wall (1, 4))
- status: ok
- P: `['8', '2', '-3', '-5', '4', '-6']`
- d: `['4', '3', '1', '-3', '-1', '-4']`
- t0: `1/2`
- word: `MPPM`
- adjacent-wall interval: `[-1/2, 1]`
- sample window: `[3/10, 7/10]`
- sample points: 7 off-wall points
- non-active q/Q signatures: `{'pair_q': {'0,3': -1, '0,4': -1, '0,5': -1, '1,3': 1, '1,5': 1, '2,3': 1, '2,4': 1, '2,5': 1}, 'triple_Q': {'0,3,4': -1, '0,3,5': 1, '0,4,5': -1, '1,3,4': 1, '1,3,5': 1, '1,4,5': 1, '2,3,4': 1, '2,3,5': 1, '2,4,5': 1}, 'freq': {'0': 1, '1': 1, '2': -1, '3': -1, '4': 1, '5': -1}}`
- fit holdout residuals: left `0`, right `0`
- q-wall quotient polynomial: `-29024*t**6 + 20768*t**5 + 310784*t**4 + 256704*t**3 - 440800*t**2 - 872928*t - 190656`
- jump remainder: `0`
- on-wall trace match: `True`
- off-wall formula checks: `7/7`

### PMMP (wall (2, 3))
- status: ok
- P: `['10', '-7', '-6', '-5', '-4', '12']`
- d: `['1', '1', '1', '-1', '-1', '-1']`
- t0: `1/2`
- word: `PMMP`
- adjacent-wall interval: `[-1, 1]`
- sample window: `[3/10, 7/10]`
- sample points: 7 off-wall points
- non-active q/Q signatures: `{'pair_q': {'0,3': -1, '0,4': -1, '0,5': 1, '1,3': -1, '1,4': -1, '1,5': 1, '2,4': -1, '2,5': 1}, 'triple_Q': {'0,3,4': -1, '0,3,5': 1, '0,4,5': 1, '1,3,4': 1, '1,3,5': 1, '1,4,5': 1, '2,3,4': 1, '2,3,5': 1, '2,4,5': 1}, 'freq': {'0': 1, '1': -1, '2': -1, '3': -1, '4': -1, '5': 1}}`
- fit holdout residuals: left `0`, right `0`
- q-wall quotient polynomial: `-320*t**6 - 2912*t**5 + 4480*t**4 + 474752*t**3 - 684416*t**2 + 5101888*t + 8743168`
- jump remainder: `0`
- on-wall trace match: `True`
- off-wall formula checks: `7/7`

## Jump cocycle check
- Delta at z=y: `-32*a**6 - 128*a**5*b - 128*a**5*x - 256*a**5*y - 96*a**4*b**2 - 288*a**4*b*x - 448*a**4*b*y - 96*a**4*x**2 - 512*a**4*x*y - 416*a**4*y**2 + 96*a**3*b**3 - 32*a**3*b**2*x + 32*a**3*b**2*y - 128*a**3*b*x**2 - 544*a**3*b*x*y - 416*a**3*b*y**2 - 192*a**3*x**2*y - 384*a**3*x*y**2 - 160*a**3*y**3 + 128*a**2*b**4 + 288*a**2*b**3*x + 416*a**2*b**3*y + 64*a**2*b**2*x**2 + 416*a**2*b**2*x*y + 352*a**2*b**2*y**2 - 64*a**2*b*x**2*y - 160*a**2*b*x*y**2 - 64*a**2*b*y**3 + 32*a**2*x*y**3 + 32*a*b**5 + 160*a*b**4*x + 224*a*b**4*y + 128*a*b**3*x**2 + 544*a*b**3*x*y + 416*a*b**3*y**2 + 192*a*b**2*x**2*y + 384*a*b**2*x*y**2 + 160*a*b**2*y**3 + 32*b**5*y + 32*b**4*x**2 + 96*b**4*x*y + 64*b**4*y**2 + 64*b**3*x**2*y + 160*b**3*x*y**2 + 64*b**3*y**3 - 32*b**2*x*y**3`
- factored Delta: `-32*(a - b)*(a + b)*(a**4 + 4*a**3*b + 4*a**3*x + 8*a**3*y + 4*a**2*b**2 + 9*a**2*b*x + 14*a**2*b*y + 3*a**2*x**2 + 16*a**2*x*y + 13*a**2*y**2 + a*b**3 + 5*a*b**2*x + 7*a*b**2*y + 4*a*b*x**2 + 17*a*b*x*y + 13*a*b*y**2 + 6*a*x**2*y + 12*a*x*y**2 + 5*a*y**3 + b**3*y + b**2*x**2 + 3*b**2*x*y + 2*b**2*y**2 + 2*b*x**2*y + 5*b*x*y**2 + 2*b*y**3 - x*y**3)`
- J(a,b,x,y): `a**4 + 4*a**3*b + 4*a**3*x + 8*a**3*y + 4*a**2*b**2 + 9*a**2*b*x + 14*a**2*b*y + 3*a**2*x**2 + 16*a**2*x*y + 13*a**2*y**2 + a*b**3 + 5*a*b**2*x + 7*a*b**2*y + 4*a*b*x**2 + 17*a*b*x*y + 13*a*b*y**2 + 6*a*x**2*y + 12*a*x*y**2 + 5*a*y**3 + b**3*y + b**2*x**2 + 3*b**2*x*y + 2*b**2*y**2 + 2*b*x**2*y + 5*b*x*y**2 + 2*b*y**3 - x*y**3`
- factored J: `a**4 + 4*a**3*b + 4*a**3*x + 8*a**3*y + 4*a**2*b**2 + 9*a**2*b*x + 14*a**2*b*y + 3*a**2*x**2 + 16*a**2*x*y + 13*a**2*y**2 + a*b**3 + 5*a*b**2*x + 7*a*b**2*y + 4*a*b*x**2 + 17*a*b*x*y + 13*a*b*y**2 + 6*a*x**2*y + 12*a*x*y**2 + 5*a*y**3 + b**3*y + b**2*x**2 + 3*b**2*x*y + 2*b**2*y**2 + 2*b*x**2*y + 5*b*x*y**2 + 2*b*y**3 - x*y**3`
- divisible by 32*q: `True`
- J nonzero: `True`
- witness J value: `-881/16`
- witness Delta value: `-21144`
- witness implies `Delta` nonzero on z=y wall: `True`