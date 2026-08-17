# Controlled A6 experiment: one PI and one student

This question tree is self-contained. Operate only inside it. Never read or
search a parent directory, sibling question, prior run, or another project.
The complete scientific input is `question.md` and `bg.cpp`.

The scheduled PI is a Claude agent launched by `run_bot.sh`. The scheduled
student is a Codex agent launched by `run_codex_bot.sh`, using
`gpt-5.6-sol` with `xhigh` reasoning by default.

The custom Codex `technician` is an implementation-only sub-agent configured
in `.codex/agents/technician.toml`. It is not a scheduled research role.

The task is only the compact complete six-point amplitude \(A_6\). Do not
broaden it to an all-\(n\) formula.
