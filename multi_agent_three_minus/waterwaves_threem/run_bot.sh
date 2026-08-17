#!/bin/bash
# Launch ONE agent session for THIS question, headless. Lives in the question dir.
# Usage: ./run_bot.sh <prompt-name> [identity]
#   ./run_bot.sh pi-bot            ./run_bot.sh student-bot student-1
# Env: CLAUDE_MODEL, CLAUDE_EFFORT, DRY_RUN=1
set -uo pipefail
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

BOT_NAME="${1:?Usage: ./run_bot.sh <prompt-name> [identity]}"
IDENTITY="${2:-}"
QDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$QDIR"

LOG_NAME="${IDENTITY:-$BOT_NAME}"
LOG_DIR="${QDIR}/logs/${LOG_NAME}"
TIMESTAMP=$(date +%Y-%m-%dT%H-%M-%S)
LOG_FILE="${LOG_DIR}/${TIMESTAMP}.log"
mkdir -p "${LOG_DIR}"

PROMPT="You are an agent working on ONE self-contained task whose entire directory is ${QDIR}. Work strictly inside ${QDIR}: only read, write, build, and run files under that exact path, and treat it as your root. Do NOT open, read, copy, or modify any other task directory anywhere on this machine -- in particular ignore every other questions/* directory (for example questions/waterwaves_proof); they are different, unrelated problems and must never influence this work. Start by reading ${QDIR}/prompts/${BOT_NAME}.md and follow its instructions; the question.md you work on is ${QDIR}/question.md."
if [ -n "${IDENTITY}" ]; then
    PROMPT="${PROMPT} Your identity for this session is ${IDENTITY}; your bot directory is ${QDIR}/bots/${IDENTITY}/."
fi

MODEL="${CLAUDE_MODEL:-claude-opus-4-8[1m]}"
EFFORT="${CLAUDE_EFFORT:-xhigh}"
echo "[${TIMESTAMP}] model=${MODEL} effort=${EFFORT} prompt=prompts/${BOT_NAME}.md identity=${IDENTITY:-none}" >> "${LOG_FILE}"

if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "DRY_RUN: claude --model ${MODEL} --effort ${EFFORT} --output-format json -p \"${PROMPT}\" --dangerously-skip-permissions"
    echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} DRY_RUN (not launched)" >> "${LOG_FILE}"
    exit 0
fi

JSON_FILE="${LOG_DIR}/${TIMESTAMP}.json"
claude \
  --model "${MODEL}" \
  --effort "${EFFORT}" \
  --output-format json \
  -p "${PROMPT}" \
  --dangerously-skip-permissions \
  > "${JSON_FILE}" 2>> "${LOG_FILE}"
EXIT_CODE=$?

python3 - "${JSON_FILE}" >> "${LOG_FILE}" 2>&1 <<'PYEOF'
import json, sys
try:
    d = json.load(open(sys.argv[1]))
except Exception as e:
    print(f"[usage] parse failed: {e}"); sys.exit(0)
if isinstance(d.get("result"), str):
    print(d["result"])
u = d.get("usage", {}) or {}
print(f"[usage] cost_usd={d.get('total_cost_usd')} duration_ms={d.get('duration_ms')} "
      f"num_turns={d.get('num_turns')} in={u.get('input_tokens')} out={u.get('output_tokens')} "
      f"cache_read={u.get('cache_read_input_tokens')} cache_write={u.get('cache_creation_input_tokens')}")
PYEOF

echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} exited with code ${EXIT_CODE}" >> "${LOG_FILE}"
