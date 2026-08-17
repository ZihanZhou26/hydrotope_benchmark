#!/bin/bash
# Orchestration scheme for THIS question: PI assigns, then 2 students in parallel,
# repeat for N rounds; stop early when summary/SOLVED.md appears.
# Usage: ./run.sh [rounds] [interval_minutes]   (defaults: 8, 60)
# Env passes through to run_bot.sh (CLAUDE_MODEL, CLAUDE_EFFORT, DRY_RUN).
set -uo pipefail
QDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$QDIR"
ROUNDS="${1:-8}"
INTERVAL_MIN="${2:-60}"
START_TIME=$(date -u +%Y-%m-%dT%H:%M:%S)

echo "PI + Students in $(basename "$QDIR"): ${ROUNDS} rounds, ${INTERVAL_MIN} min apart"

if [ -f run_status.json ]; then
    mv run_status.json "run_status_$(date +%Y-%m-%dT%H-%M-%S).json"
fi

for i in $(seq 1 "$ROUNDS"); do
    echo ""
    echo "=== Round ${i}/${ROUNDS} — $(date) ==="
    ROUND_TIME=$(date -u +%Y-%m-%dT%H:%M:%S)
    cat > run_status.json <<STATUSEOF
{
  "total_rounds": ${ROUNDS},
  "current_round": ${i},
  "started": "${START_TIME}",
  "interval_minutes": ${INTERVAL_MIN},
  "last_round_started": "${ROUND_TIME}"
}
STATUSEOF

    echo "Running PI..."
    ./run_bot.sh pi-bot

    echo "Running students in parallel..."
    ./run_bot.sh student-bot student-1 &
    ./run_bot.sh student-bot student-2 &
    wait

    echo "Round ${i} complete at $(date)"
    if [ -f summary/SOLVED.md ]; then
        echo "=== SOLVED — stopping early after round ${i}/${ROUNDS} ==="
        break
    fi
    if [ "$i" -lt "$ROUNDS" ]; then
        echo "Sleeping ${INTERVAL_MIN} minutes..."
        sleep $((INTERVAL_MIN * 60))
    fi
done
echo ""
echo "Done."
