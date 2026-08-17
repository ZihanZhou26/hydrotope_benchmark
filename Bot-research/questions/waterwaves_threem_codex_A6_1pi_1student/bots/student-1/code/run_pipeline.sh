#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${ROOT}/data"
mkdir -p "${DATA_DIR}"

if [ ! -x "${ROOT}/code/bg" ]; then
  echo "[run] building bg.cpp"
  g++ -O2 -std=c++17 -o "${ROOT}/code/bg" "${ROOT}/code/bg.cpp" -lgmpxx -lgmp
fi

python3 "${ROOT}/code/calibration.py" | tee "${DATA_DIR}/calibration.txt"
python3 "${ROOT}/code/domain_scan.py" | tee "${DATA_DIR}/domain_scan.log"
python3 "${ROOT}/code/pole_scan.py" | tee "${DATA_DIR}/pole_scan.log"
python3 "${ROOT}/code/wall_approach.py" | tee "${DATA_DIR}/wall_approach.log"
python3 "${ROOT}/code/ansatz_fit.py" | tee "${DATA_DIR}/h1_fit_report.txt"
