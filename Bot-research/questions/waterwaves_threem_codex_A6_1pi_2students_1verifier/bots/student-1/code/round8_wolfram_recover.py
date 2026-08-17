#!/usr/bin/env python3
import argparse
import hashlib
import importlib.util
import json
import subprocess
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

WOLFRAM = Path("/opt/sns/bin64/wolframscript")
PRIME = 2147483647


def sha256_text(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_fastsolve(qdir: Path):
    src = qdir / "bots/student-1/code/fastsolve.py"
    if not src.exists():
        raise FileNotFoundError(f"missing fastsolve at {src}")
    spec = importlib.util.spec_from_file_location("round8_fastsolve", str(src))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def load_object_array(path: Path) -> np.ndarray:
    arr = np.load(path, allow_pickle=True)
    if arr.dtype != object:
        arr = arr.astype(object)
    return arr


def parse_fraction_token(tok) -> Fraction:
    if isinstance(tok, int):
        return Fraction(tok, 1)
    if isinstance(tok, float):
        if tok.is_integer():
            return Fraction(int(tok), 1)
        raise ValueError(f"non-integer float token {tok!r}")
    s = str(tok).strip()
    if s in {"", "0"}:
        return Fraction(0, 1)
    if "/" in s:
        n, d = s.split("/", 1)
        return Fraction(int(n), int(d))
    if s.startswith("((") and s.endswith("))"):
        s = s[2:-2]
    return Fraction(int(s), 1)


def write_matrix_wl(A: np.ndarray, y: np.ndarray, out_path: Path):
    rows = []
    for row in A:
        rows.append("{" + ",".join(str(int(v)) for v in row) + "}")
    mat = "{" + ",".join(rows) + "}"

    vec = "{" + ",".join(str(int(v)) for v in y) + "}"
    out_path.write_text(
        "m = " + mat + ";\n"
        "b = " + vec + ";\n"
        "sol = LinearSolve[m, b];\n"
        "out = ExportString[(ToString[#, InputForm] & /@ sol), \"JSON\"];\n"
        "Print[out];\n"
    )
    return {"matrix_shape": list(A.shape), "vector_length": len(y), "wl_path": str(out_path)}


def run_wolfram(script_path: Path, timeout_sec: int = 600):
    if not WOLFRAM.exists():
        raise FileNotFoundError(f"wolframscript not found: {WOLFRAM}")
    t0 = time.perf_counter()
    proc = subprocess.run(
        [str(WOLFRAM), "-script", str(script_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        check=False,
        timeout=timeout_sec,
    )
    wall = time.perf_counter() - t0
    return proc, wall


def verify_solution(A: np.ndarray, y: np.ndarray, x: list) -> (bool, dict):
    nz = [(j, c) for j, c in enumerate(x) if c != 0]
    for ridx in range(A.shape[0]):
        lhs = Fraction(0, 1)
        row = A[ridx]
        for j, cj in nz:
            vij = row[j]
            if vij != 0:
                lhs += Fraction(int(vij), 1) * cj
        rhs = Fraction(int(y[ridx]), 1)
        if lhs != rhs:
            return False, {
                "row": int(ridx),
                "lhs": str(lhs),
                "rhs": str(rhs),
                "support_count": len(nz),
            }
    return True, {"support_count": len(nz)}


def main():
    ap = argparse.ArgumentParser(description="Recover round8 coefficients via Wolfram LinearSolve.")
    ap.add_argument("--qdir", type=Path, default=Path("."))
    ap.add_argument("--timeout", type=int, default=600, help="Wolfram timeout in seconds")
    ap.add_argument("--max-rows", type=int, default=900, help="expected row count (safety check)")
    ap.add_argument("--max-cols", type=int, default=605, help="expected column count (safety check)")
    args = ap.parse_args()

    qdir = args.qdir.resolve()
    t0 = time.perf_counter()

    A_path = qdir / "bots/student-1/data/round8_A_int.npy"
    y_path = qdir / "bots/student-1/data/round8_y_int.npy"
    meta_path = qdir / "bots/student-1/data/round8_A_meta.json"
    wl_data_path = qdir / "bots/student-1/data/round8_wolfram_system.wl"
    sol_json_path = qdir / "bots/student-1/data/round8_wolfram_pivot_solution.json"
    recov_path = qdir / "bots/student-1/data/round8_wolfram_recovery.json"
    out_solution_path = qdir / "bots/student-1/data/round8_hinge_decisive_solution.json"

    fs = load_fastsolve(qdir)

    A = load_object_array(A_path)
    y = load_object_array(y_path)
    if A.shape[0] != y.shape[0]:
        raise RuntimeError(f"A/y row mismatch: {A.shape[0]} vs {y.shape[0]}")
    if A.shape != (args.max_rows, args.max_cols):
        raise RuntimeError(f"unexpected A shape {A.shape}, expected ({args.max_rows}, {args.max_cols})")

    with meta_path.open() as f:
        meta = json.load(f)
    feature_meta = meta.get("feature_meta", [])
    global_meta = meta.get("global_meta", [])
    all_meta = feature_meta + global_meta

    t_pivot = time.perf_counter()
    rank, pivot_cols, _ = fs._echelon_mod(A, PRIME)
    if rank != 182:
        raise RuntimeError(f"pivot rank was {rank}, expected 182")
    pivot_cols = [int(c) for c in pivot_cols]

    A_sub = A[:, pivot_cols]
    _, row_pivots, _ = fs._echelon_mod(A_sub.T, PRIME)
    if len(row_pivots) != rank:
        raise RuntimeError(f"row pivot count {len(row_pivots)} != rank {rank}")
    row_indices = [int(r) for r in row_pivots]
    if len(set(row_indices)) != len(row_indices):
        raise RuntimeError("dependent row selection from Asub.T pivot columns")

    M = A[np.ix_(row_indices, pivot_cols)]
    b = y[row_indices]
    rank_m = fs._echelon_mod(M, PRIME)[0]
    if rank_m != rank:
        raise RuntimeError(f"pivot square rank {rank_m} != {rank}")
    t_pivot = time.perf_counter() - t_pivot

    t_wl = time.perf_counter()
    write_matrix_wl(M, b, wl_data_path)
    wl_proc, wolfram_secs = run_wolfram(wl_data_path, timeout_sec=args.timeout)
    t_wl = time.perf_counter() - t_wl

    if wl_proc.returncode != 0:
        rec = {
            "status": "wolfram_failed",
            "error": wl_proc.stderr[-4000:],
            "command": f"{WOLFRAM} -script {wl_data_path}",
            "timings": {
                "pivot_sec": t_pivot,
                "wolfram_sec": wolfram_secs,
                "total_sec": time.perf_counter() - t0,
            },
            "pivot_columns": pivot_cols,
            "pivot_rows": row_indices,
            "rank": rank,
            "prime": PRIME,
            "paths": {k: str(v) for k, v in {
                "A": A_path,
                "y": y_path,
                "meta": meta_path,
                "wl": wl_data_path,
            }.items()},
            "hashes": {k: sha256_text(v) for k, v in {
                "A": A_path,
                "y": y_path,
                "meta": meta_path,
                "system_wl": wl_data_path,
            }.items()},
        }
        recov_path.write_text(json.dumps(rec, indent=2) + "\n")
        out_solution_path.write_text(
            json.dumps(
                {
                    "status": "backend_error",
                    "backend": "Wolfram LinearSolve",
                    "rank": rank,
                    "pivot_columns": pivot_cols,
                    "pivot_rows": row_indices,
                    "residual_ok": False,
                    "support_count": 0,
                    "support": [],
                    "error": wl_proc.stderr[-2000:],
                },
                indent=2,
            )
            + "\n"
        )
        return

    raw = (wl_proc.stdout or "").strip()
    if not raw:
        raise RuntimeError("wolfram output empty")
    l = raw.find("[")
    r = raw.rfind("]")
    if l == -1 or r == -1 or r < l:
        raise RuntimeError(f"unparseable wolfram output: {raw[:400]}")
    coeff_tokens = json.loads(raw[l : r + 1])
    coeffs = [parse_fraction_token(tok) for tok in coeff_tokens]
    if len(coeffs) != rank:
        raise RuntimeError(f"wolfram coeff count {len(coeffs)} != rank {rank}")

    x = [Fraction(0, 1)] * A.shape[1]
    for idx, c in enumerate(coeffs):
        x[pivot_cols[idx]] = c
    nonzero = [(i, c) for i, c in enumerate(x) if c != 0]

    t_ver = time.perf_counter()
    residual_ok, witness = verify_solution(A, y, x)
    t_ver = time.perf_counter() - t_ver
    total = time.perf_counter() - t0

    support = []
    for idx, c in nonzero:
        meta_item = all_meta[idx] if idx < len(all_meta) else {}
        support.append(
            {
                "column": idx,
                "value": str(c),
                "kind": "hinge" if idx < len(feature_meta) else "dual",
                "metadata": meta_item,
            }
        )

    sol_payload = {
        "status": "ok" if residual_ok else "residual_bad",
        "backend": "Wolfram LinearSolve",
        "rank": rank,
        "pivot_columns": pivot_cols,
        "pivot_rows": row_indices,
        "residual_ok": bool(residual_ok),
        "support_count": len(nonzero),
        "support": support,
    }
    if not residual_ok:
        sol_payload["residual_witness"] = witness
    sol_payload["artifacts"] = {
        "pivot_solution_strings": str(sol_json_path),
        "system_wl": str(wl_data_path),
    }
    out_solution_path.write_text(json.dumps(sol_payload, indent=2) + "\n")

    sol_json_path.write_text(json.dumps([str(c) for c in coeffs], indent=2) + "\n")

    rec = {
        "status": "ok" if residual_ok else "residual_bad",
        "backend": "Wolfram LinearSolve",
        "prime": PRIME,
        "rank": rank,
        "pivot_columns": pivot_cols,
        "pivot_rows": row_indices,
        "paths": {
            "A_int": str(A_path),
            "y_int": str(y_path),
            "meta": str(meta_path),
            "system_wl": str(wl_data_path),
            "pivot_solution": str(sol_json_path),
            "recovery": str(recov_path),
            "solution": str(out_solution_path),
        },
        "hashes": {
            "A_int": sha256_text(A_path),
            "y_int": sha256_text(y_path),
            "meta": sha256_text(meta_path),
            "system_wl": sha256_text(wl_data_path),
        },
        "timings": {
            "pivot_sec": t_pivot,
            "wolfram_sec": wolfram_secs,
            "verify_sec": t_ver,
            "total_sec": total,
            "wolfram_command_sec": wolfram_secs,
            "wolfram_returncode": wl_proc.returncode,
        },
        "solver": {
            "stdout_excerpt": (wl_proc.stdout[-4000:] if wl_proc.stdout else ""),
            "stderr": (wl_proc.stderr[:4000] if wl_proc.stderr else ""),
        },
        "solution_summary": {
            "support_count": len(nonzero),
            "residual_ok": bool(residual_ok),
            "nonzero_columns": [i for i, _ in nonzero],
        },
    }
    recov_path.write_text(json.dumps(rec, indent=2) + "\n")

if __name__ == "__main__":
    main()
