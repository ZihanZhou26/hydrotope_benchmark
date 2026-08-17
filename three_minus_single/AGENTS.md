# Three-minus formula task

Read `question.md` and solve that scientific problem as one agent.

Your local filesystem access is strictly limited to this directory. Do not
read, list, search, or inspect any path outside it. Online web search and
scientific literature are allowed. Do not use other AI models or sub-agents.

Return the final closed-form analytic formula for the complete domain requested
in `question.md`: every `n >= 5` and arbitrary on-shell three-minus kinematics.
The partial-description and scope-narrowing fallbacks in `question.md` do not
apply. Do not stop with selected values of `n`, selected chambers, an
approximation, or a transcription of the BG recursion. Write the completed
answer to `FINAL_FORMULA.md`, including the definitions and prescriptions needed
to evaluate the formula and concise BG-code verification evidence.

The references in `question.md` to a PI, students, boards, bot directories,
cluster computing, and group deliverables do not apply to this single-agent
run. You may compile and modify the supplied private copy `bg.cpp` here.
