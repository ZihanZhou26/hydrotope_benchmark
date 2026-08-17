# Controlled A6 experiment: PI, two students, and verifier

This question tree is self-contained. Operate only inside it. Never read or
search a parent directory, sibling question, prior run, or another project.
The complete scientific input is `question.md` and `bg.cpp`.

The scheduled PI is a Claude agent. The two scheduled students are independent
Codex agents using `gpt-5.6-sol` with `xhigh` reasoning by default. After both
students finish each research round, a separate Claude verifier audits their
strongest result and files an adversarial report for the next PI session.

The custom Codex `technician` is an implementation-only sub-agent configured
in `.codex/agents/technician.toml`. It is not a scheduled research role.

The task is only the compact complete six-point amplitude \(A_6\). Do not
broaden it to an all-\(n\) formula.
