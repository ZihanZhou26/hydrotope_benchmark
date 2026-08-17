# Chronological Log

## Initial request

1. User asked to go to `waterhedron_benchmark_blind/case_1`, finish the task, and put results in `codex_55_xhigh`.

2. Assistant said it would inspect the case directory and create the requested result folder.

3. Ran:

```bash
pwd && rg --files waterhedron_benchmark_blind/case_1 waterhedron_benchmark_blind_case_1 2>/dev/null | head -200
```

Key output: found `/home/zihanz/waterhedron_benchmark_blind/case_1/prompt.md`, `OnShellBG.m`, and prior `claude_opus_48_max/*` files.

4. Ran:

```bash
find /home/zihanz -maxdepth 3 -type d \( -name 'waterhedron_benchmark_blind*' -o -name '*case_1*' \) | sort
```

Key output: found `/home/zihanz/waterhedron_benchmark_blind/case_1`; no separate `waterhedron_benchmark_blind_case_1`.

5. Assistant said it found `prompt.md` and an existing prior run folder, and would read allowed task/source files.

6. Ran:

```bash
sed -n '1,240p' prompt.md
sed -n '1,240p' OnShellBG.m
find . -maxdepth 2 -type f | sort
find /home/zihanz -maxdepth 2 -type d -name 'waterhedron_benchmark_blind_case_1' -o -name 'waterhedron_benchmark_blind_case_1*' | sort
```

Key output: prompt required a global rational formula for the two-minus sector, allowed only `prompt.md` and `OnShellBG.m`, and `OnShellBG.m` contained BG kernels, recursion, `MakeKinematics`, and stock tests. The file listing also showed prior sibling output names.

7. Assistant noted the prompt forbids sibling solution files and treated them as off-limits. It assumed the output path should be `case_1/codex_55_xhigh`.

8. Ran:

```bash
command -v wolframscript || true
command -v python3 && python3 --version
```

Key output: both initially failed with `Out of memory (os error 12)`.

9. Ran:

```bash
command -v wolframscript || true; command -v python3 || true; python3 --version 2>/dev/null || true
```

Key output:

```text
/opt/sns/bin64/wolframscript
/usr/bin/python3
Python 3.6.8
```

10. Assistant said it would generate fresh BG amplitudes.

11. Ran:

```bash
wolframscript -file OnShellBG.m
```

Key output: stock script printed one-minus-sector tests and reached the slow `n = 8` test.

12. Assistant said the stock script was slow and it would stop it.

13. Sent Ctrl-C to the Wolfram session.

Key output: process exited.

14. Ran a targeted Wolfram command loading `OnShellBG.m` and checking the four-point two-minus case.

Key output: failed with `Out of memory (os error 12)`.

15. Ran:

```bash
ps -eo pid,ppid,stat,comm,args --sort=-rss | head -40
```

Key output: showed many high-RSS processes and a lingering `WolframKernel` PID `2379002`.

16. Ran:

```bash
kill 2379002
ps -eo pid,stat,comm,args --sort=-rss | head -20
```

Key output: first kill attempt via login shell failed OOM; non-login kill succeeded; process table no longer showed that Wolfram kernel.

17. Ran:

```bash
wolframscript -code 'Catch[Block[{Print=(Throw[Null]&)}, Get["OnShellBG.m"]]]; Print["loaded"]'
```

Key output:

```text
loaded
Null
```

18. Ran a targeted symbolic four-point Wolfram check with `MakeKinematics[4,{a,b},sig,1]`.

Key output:

```text
Piecewise[{{(-8*I)*a^3*b, a < b}}, (-8*I)*a*b^3]
```

19. Ran a targeted symbolic four-point Wolfram check with `MakeKinematics[4,{-x,y},sig,1]`.

Key output: failed with `Out of memory (os error 12)`.

20. Ran:

```bash
python3 - <<'PY'
print('ok')
PY
```

Key output:

```text
ok
```

21. Ran an inline Python port of the BG recursion.

Key output: failed on the four-point case with:

```text
ZeroDivisionError: float division by zero
```

22. Ran the inline Python port on generic five-point cases.

Key output:

```text
[-2,3,4] amp 184.64768000000603j
[-3,4,5] amp 540.6419753087217j
[-4,2,6] amp 2560.0000000000136j
[-1.7,2.3,3.1] amp 27.890944415604302j
```

23. Ran a targeted five-point Wolfram command for `{-2,3,4}` and `{2,5/2,3}`.

Key output: failed with `Out of memory (os error 12)`.

24. Retried several lightweight commands, including:

```bash
python3 ...
true
sleep 5; true
python3 -i
kill 2255909
```

Key output: all failed with `Out of memory (os error 12)`.

25. Created `codex_55_xhigh/REPORT.md` as a placeholder.

26. Replaced the placeholder with a blocker report saying commands could not fork due to host OOM.

27. Assistant final response: reported inability to complete due OOM and pointed to the blocker report.

## First retry

28. User said: `try now`.

29. Assistant said it would retry the lightweight runtime.

30. Ran:

```bash
true
true
true
true
```

Key output: all failed with `Out of memory (os error 12)`.

31. Updated `REPORT.md` with the retry failure.

32. Assistant final response: reported the host still could not start `true`.

## Second retry

33. User said: `try now`.

34. Assistant said it would test process creation and then run a single scripted path.

35. Ran:

```bash
true
```

Key output: succeeded.

36. Ran a targeted symbolic four-point Wolfram command for `MakeKinematics[4,{-x,y},sig,1]`.

Key output:

```text
{-y, -x, y, x}
Piecewise[{{(8*I)*x^3*y, x < y}, {(8*I)*x*y^3, x > y}}, (24*I)*y^4]
```

37. Ran a targeted five-point Wolfram command for `{-2,3,4}` and `{2,5/2,3}`.

Key output:

```text
{-23/5, -2, 3, 4, -2/5}
184.64768`30.*I
{-9/2, 2, 5/2, 3, -3}
-2304.`30.*I
```

38. Added `codex_55_xhigh/bg_numeric.py`, a Python numeric BG port.

39. Ran:

```bash
python3 - <<'PY'
from codex_55_xhigh.bg_numeric import two_minus_kinematics, bg_amplitude
...
PY
```

Key output: Python port matched Wolfram five-point samples:

```text
[-2, 3, 4] ... 184.64768000000603j
[2, 2.5, 3] ... -2304j
```

40. Ran:

```bash
python3 - <<'PY'
import sympy; import numpy
PY
```

Key output:

```text
NO No module named 'sympy'
NO numpy No module named 'numpy'
```

41. Ran several Python exploratory scripts checking ratios, scaling, kernel values, and candidate denominators.

Key outputs included:

```text
scaling: lambda 1 -> 184.64768, lambda 2 -> 11817.45152, lambda 3 -> 134608.15872
kernel samples: E/F sign patterns
candidate fits: inconsistent
```

42. Ran a five-point symbolic Wolfram `FullSimplify`.

Key output:

```text
FAILED
Null
```

43. Added `codex_55_xhigh/bg_exact.py`, an exact rational Python BG port.

44. Ran:

```bash
python3 - <<'PY'
from codex_55_xhigh.bg_exact import ...
PY
```

Key output:

```text
[-2,3,4] amp = 577024/3125 i = 184.64768
[2,3,5] amp = -3328 i
```

45. Ran exact interpolation attempts.

Key output:

```text
StopIteration
Exception: inconsistent
fail 6 0 inc
fail 9 1 inc
fail 12 2 inc
fail 15 3 inc
```

46. Ran symmetry checks swapping negative and plus legs.

Key output: amplitudes were unchanged under the tested swaps.

47. Added `verify_n4_contradiction.m`.

48. Ran:

```bash
wolframscript -file verify_n4_contradiction.m > verify_n4_contradiction.out && sed -n '1,120p' verify_n4_contradiction.out
```

Key output:

```text
symbolic ws = {-y, -x, y, x}
symbolic A4 = Piecewise[{{(8*I)*x^3*y, x < y}, {(8*I)*x*y^3, x > y}}, (24*I)*y^4]
direct exact numeric BG ... Indeterminate
```

49. Ran a one-parameter five-point `PiecewiseExpand` command in Wolfram.

Key output: a large `Piecewise[...]`, confirming chamber-dependent branch structure in that slice.

50. Cleaned `verify_n4_contradiction.m` and added branch-value and branch-difference lines.

51. Ran:

```bash
wolframscript -file verify_n4_contradiction.m > verify_n4_contradiction.out && sed -n '1,80p' verify_n4_contradiction.out
```

Key output:

```text
symbolic ws = {-y, -x, y, x}
symbolic A4 = Piecewise[{{(8*I)*x^3*y, x < y}, {(8*I)*x*y^3, x > y}}, (24*I)*y^4]
difference between open-branch formulas = (8*I)*x*y*(x^2 - y^2)
branch value from symbolic expression at x=1,y=2 = 16*I
branch value from symbolic expression at x=2,y=1 = 16*I
direct exact numeric BG ... Indeterminate
```

52. Deleted the old blocker `REPORT.md` and added a final `REPORT.md` explaining the inconsistency of the requested global rational formula.

53. Ran:

```bash
find . -maxdepth 1 -type f -printf '%f\n' | sort
```

Key output:

```text
REPORT.md
bg_exact.py
bg_numeric.py
verify_n4_contradiction.m
verify_n4_contradiction.out
```

54. Assistant final response: reported completed attempt and said the supplied task is inconsistent; pointed to `REPORT.md`, `verify_n4_contradiction.m`, and `verify_n4_contradiction.out`.

## Log file request

55. User asked to put the log in a markdown file.

56. Assistant added this file as `LOG.md` in `codex_55_xhigh`.
