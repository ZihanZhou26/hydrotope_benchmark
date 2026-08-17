#!/bin/bash
# Launch one Codex student session for THIS question, headless.
# Usage: ./run_codex_bot.sh student-bot <student-1|student-2>
# Env: CODEX_STUDENT_MODEL, CODEX_STUDENT_EFFORT, BOT_EXTRA_PROMPT, DRY_RUN=1,
#      BOT_LOG_ROOT (test-only log-root override).
set -uo pipefail
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"

BOT_NAME="${1:?Usage: ./run_codex_bot.sh student-bot <student-1|student-2>}"
IDENTITY="${2:?Usage: ./run_codex_bot.sh student-bot <student-1|student-2>}"
case "${BOT_NAME}:${IDENTITY}" in
    student-bot:student-1|student-bot:student-2) ;;
    *) echo "run_codex_bot.sh is restricted to student-1 and student-2" >&2; exit 2 ;;
esac

QDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$QDIR"

for required in codex jq python3; do
    command -v "$required" >/dev/null 2>&1 || { echo "Missing required command: $required" >&2; exit 127; }
done

LOG_ROOT="${BOT_LOG_ROOT:-${QDIR}/logs}"
LOG_DIR="${LOG_ROOT}/${IDENTITY}"
TIMESTAMP=$(date +%Y-%m-%dT%H-%M-%S)
LOG_FILE="${LOG_DIR}/${TIMESTAMP}.log"
JSONL_FILE="${LOG_DIR}/${TIMESTAMP}.jsonl"
mkdir -p "${LOG_DIR}"

MODEL="${CODEX_STUDENT_MODEL:-gpt-5.6-sol}"
EFFORT="${CODEX_STUDENT_EFFORT:-xhigh}"
TECHNICIAN_MODEL="gpt-5.3-codex-spark"

PROMPT="Read prompts/${BOT_NAME}.md and follow it exactly. Your identity is ${IDENTITY}. Your bot directory is bots/${IDENTITY}/."
if [ -n "${BOT_EXTRA_PROMPT:-}" ]; then
    PROMPT="${PROMPT} ${BOT_EXTRA_PROMPT}"
fi

CODEX_ARGS=(
    exec
    --json
    --ephemeral
    --strict-config
    --skip-git-repo-check
    --enable multi_agent
    --model "${MODEL}"
    --config "model_reasoning_effort=\"${EFFORT}\""
    --config 'approval_policy="never"'
    --sandbox danger-full-access
    --cd "${QDIR}"
    "${PROMPT}"
)

echo "[${TIMESTAMP}] provider=codex model=${MODEL} effort=${EFFORT} budget_usd=unavailable prompt=prompts/${BOT_NAME}.md identity=${IDENTITY} technician_model=${TECHNICIAN_MODEL}" >> "${LOG_FILE}"
if [ -n "${BOT_EXTRA_PROMPT:-}" ]; then
    echo "[${TIMESTAMP}] extra_prompt=${BOT_EXTRA_PROMPT}" >> "${LOG_FILE}"
fi

if [ "${DRY_RUN:-0}" = "1" ]; then
    printf 'DRY_RUN:'
    printf ' %q' codex "${CODEX_ARGS[@]}"
    printf '\n'
    echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} Codex DRY_RUN (not launched)" >> "${LOG_FILE}"
    exit 0
fi

# Refresh the bounded board view immediately before launch. The full board remains append-only.
python3 - <<'BOARDEOF'
import json, os
try:
    b = json.load(open("board.json"))
except Exception:
    b = {"posts": [], "next_post_id": 1, "next_comment_id": 1}
posts = b.get("posts", []) or []
rounds = [p.get("round") for p in posts if isinstance(p.get("round"), int)]
if rounds:
    cutoff = max(rounds) - 1
    recent = [p for p in posts
              if not isinstance(p.get("round"), int) or p.get("round") >= cutoff]
else:
    recent = posts
out = {
    "_view": "RECENT: posts from the last two rounds only. Full history is in board.json.",
    "_shown_posts": len(recent), "_total_posts": len(posts),
    "next_post_id": b.get("next_post_id"), "next_comment_id": b.get("next_comment_id"),
    "posts": recent,
}
tmp = "board_recent.json.tmp.%s" % os.getpid()
with open(tmp, "w") as f:
    json.dump(out, f, indent=2)
os.replace(tmp, "board_recent.json")
BOARDEOF

START_EPOCH=$(date +%s)
if setsid --wait true >/dev/null 2>&1; then
    setsid --wait codex "${CODEX_ARGS[@]}" > "${JSONL_FILE}" 2>> "${LOG_FILE}"
else
    codex "${CODEX_ARGS[@]}" > "${JSONL_FILE}" 2>> "${LOG_FILE}"
fi
EXIT_CODE=$?
END_EPOCH=$(date +%s)
DURATION_MS=$(( (END_EPOCH - START_EPOCH) * 1000 ))

if [ -s "${JSONL_FILE}" ] && jq -e . "${JSONL_FILE}" >/dev/null 2>&1; then
    LAST_MESSAGE=$(jq -rs '[.[] | select(.type == "item.completed" and .item.type == "agent_message") | .item.text] | last // empty' "${JSONL_FILE}")
    if [ -n "${LAST_MESSAGE}" ]; then
        printf '%s\n' "${LAST_MESSAGE}" >> "${LOG_FILE}"
    fi

    USAGE_TSV=$(jq -rs '
      [.[] | select(.type == "turn.completed") | .usage] as $u |
      [($u | map(.input_tokens // 0) | add // 0),
       ($u | map(.cached_input_tokens // 0) | add // 0),
       ($u | map(.output_tokens // 0) | add // 0),
       ($u | map(.reasoning_output_tokens // 0) | add // 0),
       ($u | length)] | @tsv' "${JSONL_FILE}")
    IFS=$'\t' read -r INPUT_TOTAL CACHED_INPUT OUTPUT_TOKENS REASONING_TOKENS NUM_TURNS <<< "${USAGE_TSV}"
    NONCACHED_INPUT=$(( INPUT_TOTAL - CACHED_INPUT ))
    [ "${NONCACHED_INPUT}" -lt 0 ] && NONCACHED_INPUT=0
    echo "[usage] provider=codex cost_usd=unavailable duration_ms=${DURATION_MS} num_turns=${NUM_TURNS} in=${NONCACHED_INPUT} input_total=${INPUT_TOTAL} out=${OUTPUT_TOKENS} cache_read=${CACHED_INPUT} cache_write=unavailable reasoning_out=${REASONING_TOKENS}" >> "${LOG_FILE}"
else
    echo "[usage] provider=codex parse_failed=true duration_ms=${DURATION_MS}" >> "${LOG_FILE}"
fi

echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} (Codex) exited with code ${EXIT_CODE}" >> "${LOG_FILE}"
exit "${EXIT_CODE}"
