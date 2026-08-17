#!/bin/bash
# Controlled architecture: one Claude PI, two Codex students in parallel,
# then one independent Claude verifier.
# Usage: ./run.sh [research_rounds] [interval_minutes]
set -uo pipefail
QDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$QDIR"

ROUNDS="${1:-8}"
INTERVAL_MIN="${2:-60}"
MAX_WAIT_HOURS="${MAX_WAIT_HOURS:-24}"
START_TIME="$(date -u +%Y-%m-%dT%H:%M:%S)"
FINAL_PI_PROMPT="This is the final PI summary round. Assign no new work and do not routinely duplicate the verifier's calculations. Read both latest student handoffs and the latest Claude verifier report. You may independently double-check one affected load-bearing claim if there is significant progress, a suspected error, or conflicting evidence; record any such check in bots/pi/verified.yaml. Distinguish verifier-confirmed results from unverified claims, update summary/logic.yaml and summary/group_meeting_notes.md, and write summary/FINAL_SUMMARY.md. Write summary/SOLVED.md only if the full definition of done is met and no blocking verifier gap remains."
mkdir -p jobs

write_status() {
  cat > run_status.json <<EOF
{
  "total_research_rounds": ${ROUNDS},
  "current_round": ${1},
  "phase": "${2}",
  "started": "${START_TIME}",
  "interval_minutes": ${INTERVAL_MIN},
  "updated": "$(date -u +%Y-%m-%dT%H:%M:%S)"
}
EOF
}

blocking_pending() {
  local f id
  for f in jobs/*.json; do
    [ -e "$f" ] || continue
    grep -q '"blocking"[[:space:]]*:[[:space:]]*true' "$f" || continue
    id="$(basename "$f" .json)"
    if [ ! -e "jobs/${id}.done" ] && [ ! -e "jobs/${id}.fail" ] &&
       [ ! -e "jobs/${id}.timeout" ]; then
      return 0
    fi
  done
  return 1
}

wait_for_blocking_jobs() {
  local waited=0 poll=300 cap=$((MAX_WAIT_HOURS * 3600)) f id
  while blocking_pending; do
    if [ "$waited" -ge "$cap" ]; then
      for f in jobs/*.json; do
        [ -e "$f" ] || continue
        grep -q '"blocking"[[:space:]]*:[[:space:]]*true' "$f" || continue
        id="$(basename "$f" .json)"
        [ -e "jobs/${id}.done" ] || [ -e "jobs/${id}.fail" ] ||
          touch "jobs/${id}.timeout"
      done
      return
    fi
    echo "[$(date)] blocking job pending (${waited}s/${cap}s)"
    sleep "$poll"
    waited=$((waited + poll))
  done
}

echo "A6 controlled run: one Claude PI + two Codex students + one Claude verifier"
for i in $(seq 1 "$ROUNDS"); do
  echo "=== Research round ${i}/${ROUNDS} — $(date) ==="
  if blocking_pending; then
    write_status "$i" "waiting_blocking_job"
    wait_for_blocking_jobs
  fi

  write_status "$i" "pi"
  ./run_bot.sh pi-bot || exit 1
  if [ -f summary/SOLVED.md ]; then
    echo "PI declared the task solved after a cleared verifier report."
    break
  fi

  write_status "$i" "students"
  ./run_codex_bot.sh student-bot student-1 &
  PID1=$!
  ./run_codex_bot.sh student-bot student-2 &
  PID2=$!
  STATUS=0
  wait "$PID1" || STATUS=1
  wait "$PID2" || STATUS=1
  [ "$STATUS" -eq 0 ] || exit 1

  write_status "$i" "claude_verifier"
  CLAUDE_MODEL="${VERIFIER_MODEL:-claude-opus-4-8[1m]}" \
    CLAUDE_EFFORT="${VERIFIER_EFFORT:-xhigh}" \
    ./run_bot.sh verifier-bot verifier || exit 1

  if [ "$i" -lt "$ROUNDS" ]; then
    sleep $((INTERVAL_MIN * 60))
  fi
done

write_status "$ROUNDS" "final_pi_summary"
BOT_EXTRA_PROMPT="$FINAL_PI_PROMPT" ./run_bot.sh pi-bot || exit 1
write_status "$ROUNDS" "complete"
echo "Done."
