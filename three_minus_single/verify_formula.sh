#!/usr/bin/env bash
set -euo pipefail

g++ -O2 -std=c++17 -o bg bg.cpp -lgmpxx -lgmp
g++ -O2 -std=c++17 -o formula_eval bg_formula.cpp -lgmpxx -lgmp

run_case() {
  local label="$1"
  local n="$2"
  local w="$3"
  local s="$4"
  local a b
  a="$(./bg -n "$n" -w "$w" -s "$s" | grep "^A_${n} =")"
  b="$(./formula_eval -n "$n" -w "$w" -s "$s" | grep "^A_${n} =")"
  if [[ "$a" != "$b" ]]; then
    echo "$label residual: FAIL"
    echo "  bg:      $a"
    echo "  formula: $b"
    return 1
  fi
  echo "$label residual: 0 exact ($a)"
}

S5="-1,-1,-1,1,1"
S6="-1,-1,-1,1,1,1"
S7="-1,-1,-1,1,1,1,1"

run_case "n=5 generic" 5 "1,2,3" "$S5"
run_case "n=5 parity chamber" 5 "2,3,5" "$S5"
run_case "n=6 generic" 6 "1,2,3,4" "$S6"
run_case "n=6 soft/near-pole" 6 "1/7,1,19,18" "$S6"
run_case "n=6 asymmetric" 6 "1/5,2,7,11" "$S6"
run_case "n=7 generic" 7 "1,2,3,4,5" "$S7"
run_case "n=7 asymmetric" 7 "1/3,2,5,7,13" "$S7"
