#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION="waterwaves_threem_codex55_clean"

if [[ "${1:-}" != "--worker" ]]; then
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    echo "tmux session already exists: $SESSION" >&2
    exit 1
  fi
  tmux new-session -d -s "$SESSION" "$ROOT/run.sh --worker"
  echo "Started: $SESSION"
  echo "Attach: tmux attach -t $SESSION"
  exit 0
fi

cd "$ROOT"

if [[ -e codex_events.jsonl || -e FINAL_FORMULA.md ]]; then
  echo "Refusing to overwrite an existing run." >&2
  exit 1
fi

codex exec \
  --cd "$ROOT" \
  --skip-git-repo-check \
  --model gpt-5.5 \
  --config 'model_reasoning_effort="xhigh"' \
  --config 'project_root_markers=[]' \
  --config 'default_permissions="three_minus_only"' \
  --disable multi_agent \
  --color never \
  --json \
  'Read AGENTS.md and question.md in full. Find and write FINAL_FORMULA.md containing the final full-domain closed-form formula requested there. Do not narrow the problem or return a partial substitute. Local files outside this directory are forbidden by the permission profile; online web research is allowed.' \
  2>codex_stderr.log \
  | tee codex_events.jsonl
