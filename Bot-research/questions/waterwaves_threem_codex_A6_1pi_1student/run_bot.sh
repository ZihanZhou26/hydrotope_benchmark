#!/bin/bash
# Launch ONE agent session for THIS question, headless. Lives in the question dir.
# Usage: ./run_bot.sh <prompt-name> [identity]
#   ./run_bot.sh pi-bot            ./run_bot.sh student-bot student-1
# Env: CLAUDE_MODEL, CLAUDE_EFFORT, BOT_EXTRA_PROMPT, DRY_RUN=1
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

# --- Refresh the board "recent view": only posts from the last two rounds. ---
# Agents READ board_recent.json (small, bounded); the full history stays in the
# append-only board.json archive. Regenerated at every launch so it reflects the
# latest posts. Posts with no integer round (e.g. out-of-band human posts) are always
# kept, so pinned instructions never fall out of the window.
python3 - <<'BOARDEOF'
import json, os
try:
    b = json.load(open("board.json"))
except Exception:
    b = {"posts": [], "next_post_id": 1, "next_comment_id": 1}
posts = b.get("posts", []) or []
rounds = [p.get("round") for p in posts if isinstance(p.get("round"), int)]
if rounds:
    cutoff = max(rounds) - 1  # keep the last two rounds: max and max-1
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
tmp = f"board_recent.json.tmp.{os.getpid()}"
with open(tmp, "w") as f:
    json.dump(out, f, indent=2)
os.replace(tmp, "board_recent.json")  # atomic; safe under the two parallel students
BOARDEOF

PROMPT="Read prompts/${BOT_NAME}.md and follow its instructions"
if [ -n "${IDENTITY}" ]; then
    PROMPT="${PROMPT}. Your identity for this session is ${IDENTITY}. Your bot directory is bots/${IDENTITY}/"
fi
if [ -n "${BOT_EXTRA_PROMPT:-}" ]; then
    PROMPT="${PROMPT}. ${BOT_EXTRA_PROMPT}"
fi

MODEL="${CLAUDE_MODEL:-claude-opus-4-8[1m]}"
EFFORT="${CLAUDE_EFFORT:-xhigh}"
# Per-session hard dollar cap (cost control). Students grind the most turns on the
# largest context (cache-read ≈ context × turns), so they get a default cap;
# non-student roles run uncapped. Override with CLAUDE_MAX_BUDGET_USD
# (set it to empty to disable the cap for a role).
if [ -n "${CLAUDE_MAX_BUDGET_USD+set}" ]; then
    MAX_BUDGET="${CLAUDE_MAX_BUDGET_USD}"
else
    case "${IDENTITY}" in
        student-*) MAX_BUDGET="10" ;;
        *)         MAX_BUDGET="" ;;
    esac
fi
echo "[${TIMESTAMP}] model=${MODEL} effort=${EFFORT} budget_usd=${MAX_BUDGET:-none} prompt=prompts/${BOT_NAME}.md identity=${IDENTITY:-none}" >> "${LOG_FILE}"
if [ -n "${BOT_EXTRA_PROMPT:-}" ]; then
    echo "[${TIMESTAMP}] extra_prompt=${BOT_EXTRA_PROMPT}" >> "${LOG_FILE}"
fi

# Assemble the invocation; add the budget cap only when one is set for this role.
CLAUDE_ARGS=( --model "${MODEL}" --effort "${EFFORT}" --output-format json )
if [ -n "${MAX_BUDGET}" ]; then
    CLAUDE_ARGS+=( --max-budget-usd "${MAX_BUDGET}" )
fi
CLAUDE_ARGS+=( -p "${PROMPT}" --dangerously-skip-permissions )

if [ "${DRY_RUN:-0}" = "1" ]; then
    echo "DRY_RUN: claude ${CLAUDE_ARGS[*]}"
    echo "[$(date +%Y-%m-%dT%H-%M-%S)] ${BOT_NAME} DRY_RUN (not launched)" >> "${LOG_FILE}"
    exit 0
fi

JSON_FILE="${LOG_DIR}/${TIMESTAMP}.json"
# Detach the worker from any controlling terminal (setsid) so a disconnect/hangup can't SIGHUP it
# mid-round; --wait keeps this synchronous and preserves the exit code. Fall back if unsupported.
if setsid --wait true >/dev/null 2>&1; then
    setsid --wait claude "${CLAUDE_ARGS[@]}" > "${JSON_FILE}" 2>> "${LOG_FILE}"
else
    claude "${CLAUDE_ARGS[@]}" > "${JSON_FILE}" 2>> "${LOG_FILE}"
fi
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
