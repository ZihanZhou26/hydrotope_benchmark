Two-minus sector closed-form result (read prompt.md + OnShellBG.m only).

KEY FILES
- report.md                 : formula, evidence, reasoning, scope/caveats.
- final_verify.wls          : main verification (imports only ../OnShellBG.m).
- final_verify_output.txt   : captured output, exact (relErr = 0) for n=4..7.
- verify_n8.wls             : optional n=8 numeric cross-check.
- loader.wls               : shared loader that imports ../OnShellBG.m and
                              strips its built-in demo tests.

THE FORMULA (canonical physical channel from MakeKinematics)
  [x]_+ = max(x,0)
  T_m(t;{a}) = sum_{S subset R} (-1)^|S| [t - sum_{j in S} a_j]_+^m
  A_n = i 2^(n-1)/g^(n-3) * omega_1 * omega_2 * T_{n-3}(omega_2^2; {omega_j^2 : j=3..n-1})

Other *.wls files are scratch scripts from discovery (chamber analysis,
scaling tests, gap scans).
