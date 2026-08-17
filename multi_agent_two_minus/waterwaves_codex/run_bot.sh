#!/bin/bash
# Launch ONE agent session for THIS question, headless. Lives in the question dir.
# Usage: ./run_bot.sh <prompt-name> [identity]
#   ./run_bot.sh pi-bot            ./run_bot.sh student-bot student-1
# Env: BOT_CODEX_MODEL, BOT_CODEX_EFFORT, BOT_CODEX_SANDBOX, BOT_CODEX_APPROVAL, DRY_RUN=1
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

PROMPT="Read prompts/${BOT_NAME}.md and follow its instructions"
if [ -n "${IDENTITY}" ]; then
    PROMPT="${PROMPT}. Your identity for this session is ${IDENTITY}. Your bot directory is bots/${IDENTITY}/"
fi

MODEL="${BOT_CODEX_MODEL:-gpt-5.5}"
EFFORT="${BOT_CODEX_EFFORT:-xhigh}"
SANDBOX="${BOT_CODEX_SANDBOX:-danger-full-access}"
APPROVAL="${BOT_CODEX_APPROVAL:-never}"
echo "[${TIMESTAMP}] model=${MODEL} effort=${EFFORT} prompt=prompts/${BOT_NAME}.md identity=${IDENTITY:-none}" >> "${LOG_FILE}"

if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "DRY_RUN: codex exec --model ${MODEL} -c model_reasoning_effort=\"${EFFORT}\" --sandbox ${SANDBOX} -c approval_policy=\"${APPROVAL}\" --json -C \"${QDIR}\" \"${PROMPT}\""
    echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} DRY_RUN (not launched)" >> "${LOG_FILE}"
    exit 0
fi

JSONL_FILE="${LOG_DIR}/${TIMESTAMP}.jsonl"
SUMMARY_JSON_FILE="${LOG_DIR}/${TIMESTAMP}.json"
LAST_MESSAGE_FILE="${LOG_DIR}/${TIMESTAMP}.last-message.txt"
codex exec \
  --model "${MODEL}" \
  -c "model_reasoning_effort=\"${EFFORT}\"" \
  --sandbox "${SANDBOX}" \
  -c "approval_policy=\"${APPROVAL}\"" \
  --json \
  --output-last-message "${LAST_MESSAGE_FILE}" \
  -C "${QDIR}" \
  "${PROMPT}" \
  > "${JSONL_FILE}" 2>> "${LOG_FILE}"
EXIT_CODE=$?

python3 - "${JSONL_FILE}" "${LAST_MESSAGE_FILE}" "${SUMMARY_JSON_FILE}" "${EXIT_CODE}" >> "${LOG_FILE}" 2>&1 <<'PYEOF'
import json, sys
jsonl_file, last_message_file, summary_json_file, exit_code = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
usage = {}
turns = 0
last_message = ""
try:
    with open(jsonl_file) as f:
        for line in f:
            if not line.strip():
                continue
            event = json.loads(line)
            if event.get("type") == "agent_message":
                turns += 1
            payload = event.get("payload") or event
            if isinstance(payload, dict):
                for key in ("usage", "token_usage"):
                    if isinstance(payload.get(key), dict):
                        usage.update(payload[key])
except Exception as e:
    print(f"[usage] parse failed: {e}"); sys.exit(0)
try:
    with open(last_message_file) as f:
        last_message = f.read()
        print(last_message)
except FileNotFoundError:
    pass
with open(summary_json_file, "w") as f:
    json.dump({
        "exit_code": exit_code,
        "jsonl_file": jsonl_file,
        "last_message_file": last_message_file,
        "last_message": last_message,
        "num_agent_messages": turns,
        "usage": usage,
    }, f, indent=2)
print(f"[usage] num_agent_messages={turns} in={usage.get('input_tokens')} out={usage.get('output_tokens')} "
      f"cache_read={usage.get('cache_read_input_tokens')} cache_write={usage.get('cache_creation_input_tokens')}")
PYEOF

echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} exited with code ${EXIT_CODE}" >> "${LOG_FILE}"
