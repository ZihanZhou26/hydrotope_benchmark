# Run manifest

## Architecture

- PI: Claude, default `claude-opus-4-8[1m]`, `xhigh`
- Student: Codex, default `gpt-5.6-sol`, `xhigh`
- Student technician: Codex Spark implementation sub-agent, on demand

Each requested round runs the PI and then `student-1`. A final PI-only summary
session runs after the research rounds.

## Launch

```bash
cd /home/zihanz/zihanz_bot_research/questions/waterwaves_threem_codex_A6_1pi_1student
./run.sh 8 60
```

For a persistent local launch:

```bash
nohup ./run.sh 8 60 > run.out 2>&1 < /dev/null &
echo $! > run.pid
```

Model overrides:

```bash
CLAUDE_MODEL='claude-opus-4-8[1m]' \
CODEX_STUDENT_MODEL='gpt-5.6-sol' \
CODEX_STUDENT_EFFORT='xhigh' \
./run.sh 8 60
```

## Isolation

This is a fresh state. It contains the same compact-\(A_6\) `question.md`
used by the comparison run, including that prompt's stated eight-piece
baseline, plus the common `bg.cpp` and compute guide. Its bot registries are
empty, and it contains no prior summaries, claims, sessions, generated
formula artifacts, or solved marker.
