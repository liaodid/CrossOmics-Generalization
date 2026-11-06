"""Launch one cell-line holdout with isolated logs and a reproducible run record.

Run with the configured training Python. Never loads another fold's checkpoint.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import os
import shutil
import subprocess
import sys
import uuid

SUFFIXES = ("node_Index.csv", "expr.csv", "drug_fp_phychem_A.csv",
            "drug_fp_phychem_B.csv", "loo_label.csv", "pert.csv", "pheno.csv")


def stamp():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def fingerprint(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def existing_path(explicit, candidates, description):
    if explicit is not None:
        return explicit.resolve()
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    raise FileNotFoundError(f"Cannot locate {description}; specify its path explicitly")


def json_numbers(value):
    if isinstance(value, dict):
        return {str(k): json_numbers(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_numbers(v) for v in value]
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and not __import__("math").isfinite(value):
        return None
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project_root", type=Path, default=Path.cwd())
    parser.add_argument("--baseline_dir", type=Path)
    parser.add_argument("--dataset_file_dir", type=Path)
    parser.add_argument("--entry_script", type=Path)
    parser.add_argument("--holdout_cell_line", default="HS578T")
    parser.add_argument("--mode", choices=("smoke", "train"), default="train")
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--random_seed", type=int, default=1995)
    parser.add_argument("--development_val_fraction", type=float, default=0.2)
    parser.add_argument("--total_epoch", type=int, default=1000)
    parser.add_argument("--patience", type=int, default=500)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--dry_run", action="store_true", help="Check paths and print plan; no files or GPU jobs created")
    options = parser.parse_args()
    root = options.project_root.resolve()
    if not root.is_dir():
        parser.error(f"Project directory does not exist: {root}")
    if options.batch_size < 1 or options.total_epoch < 1 or options.patience < 1:
        parser.error("batch_size, total_epoch and patience must be positive")
    if not 0 < options.development_val_fraction < 1:
        parser.error("development_val_fraction must be between 0 and 1")
    if not options.holdout_cell_line or any(ch not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-()." for ch in options.holdout_cell_line):
        parser.error("Unexpected cell-line name")
    baseline = existing_path(options.baseline_dir, [root / "PTV-1-main/ProteinTalks",
        root / "baseline/proteintalks/PTV-1-main/ProteinTalks"], "baseline directory")
    data = existing_path(options.dataset_file_dir, [root / "PTV1_dataset_20261015",
        root / "data/proteintalks/PTV1_dataset_20261015"], "dataset directory")
    entry = existing_path(options.entry_script, [root / "script/proteintalks_cell_holdout.py",
        root / "script/script/proteintalks_cell_holdout.py"], "holdout entry script")
    prefix = "allcelltype_drugpair_crossdrug_"
    for path in [entry, baseline / "main.py", *[data / (prefix + suffix) for suffix in SUFFIXES]]:
        if not path.is_file():
            raise FileNotFoundError(path)
    run_name = f"{options.mode}_{datetime.now():%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:8]}"
    run_dir = root / "results/proteintalks/cell_holdout" / options.holdout_cell_line / f"seed{options.random_seed}_bs{options.batch_size}" / run_name
    epochs = 2 if options.mode == "smoke" else options.total_epoch
    command = [sys.executable, "-u", str(entry), "--baseline_dir", str(baseline),
        "--holdout_cell_line", options.holdout_cell_line,
        "--development_val_fraction", str(options.development_val_fraction),
        "--dataset_file_dir", str(data), "--trainval_file_prefix", prefix,
        "--dir_save", str(run_dir / "training"), "--random_seed", str(options.random_seed),
        "--total_epoch", str(epochs), "--patience", str(options.patience),
        "--batch_size", str(options.batch_size), "--learning_rate", "0.0005",
        "--hidden_size", "64", "--dropout_rate", "0", "--lambda_pheno", "0.8"]
    print(f"Project: {root}\nHoldout: {options.holdout_cell_line}\nMode: {options.mode}\nBatch size: {options.batch_size}\nEpoch cap: {epochs}\nResults: {run_dir}", flush=True)
    print("No official/previous-fold checkpoint is loaded. Held-out test evaluation is disabled.", flush=True)
    if options.dry_run:
        print(json.dumps(command, ensure_ascii=False, indent=2))
        print("Dry run passed. No training started.")
        return
    run_dir.mkdir(parents=True, exist_ok=False)
    snapshot = run_dir / "source_snapshot"
    snapshot.mkdir()
    shutil.copy2(entry, snapshot / entry.name)
    shutil.copy2(Path(__file__), snapshot / Path(__file__).name)
    (snapshot / "upstream").mkdir()
    for source in baseline.glob("*.py"):
        shutil.copy2(source, snapshot / "upstream" / source.name)
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES=options.gpu, MPLBACKEND="Agg", PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    record = {"started_at": stamp(), "project_root": str(root), "python": sys.executable,
              "options": {k: str(v) if isinstance(v, Path) else v for k, v in vars(options).items()},
              "command": command, "run_directory": str(run_dir), "state": "starting",
              "actual_epoch_cap": epochs, "holdout_evaluation": "disabled",
              "selection_policy": "validation joint loss only; use training/*/best_checkpoint.pt",
              "protocol_note": "batch size 32 differs from prior MCF7 batch size 8; do not attribute cross-run differences only to cell line"}
    write_json(run_dir / "run_status.json", record)
    with (run_dir / "command.json").open("w", encoding="utf-8") as stream:
        json.dump(command, stream, ensure_ascii=False, indent=2)
    try:
        freeze = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", env=env, timeout=120)
        (run_dir / "environment_freeze.txt").write_text(freeze.stdout + freeze.stderr, encoding="utf-8")
        if freeze.returncode:
            raise RuntimeError("pip freeze failed; check environment_freeze.txt")
        try:
            gpu = subprocess.run(["nvidia-smi"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
            (run_dir / "gpu_before.txt").write_text(gpu.stdout + gpu.stderr, encoding="utf-8")
        except (OSError, subprocess.TimeoutExpired) as exc:
            (run_dir / "gpu_before.txt").write_text(str(exc), encoding="utf-8")
        record["state"] = "running"
        write_json(run_dir / "run_status.json", record)
        with (run_dir / "train.log").open("w", encoding="utf-8", buffering=1) as log:
            process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1)
            record["training_pid"] = process.pid
            write_json(run_dir / "run_status.json", record)
            try:
                for line in process.stdout:
                    print(line, end="", flush=True)
                    log.write(line)
                returncode = process.wait()
            except BaseException:
                # Only stop this launcher's own direct training child.
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                raise
        record["returncode"] = returncode
        if returncode:
            raise RuntimeError(f"Training exited with code {returncode}; see {run_dir / 'train.log'}")
        summaries = list((run_dir / "training").glob("*/split_summary.json"))
        if len(summaries) != 1:
            raise RuntimeError("Expected exactly one completed training directory")
        training_dir = summaries[0].parent
        summary = json.loads(summaries[0].read_text(encoding="utf-8"))
        if summary["holdout_cell_line"] != options.holdout_cell_line:
            raise RuntimeError("Unexpected holdout in training summary")
        checkpoint = training_dir / "best_checkpoint.pt"
        if not checkpoint.is_file():
            raise FileNotFoundError(checkpoint)
        import torch
        # Trusted checkpoint created by this process's training child, loaded on CPU.
        saved = torch.load(checkpoint, map_location="cpu", weights_only=False)
        selected = {"checkpoint": str(checkpoint), "relative_checkpoint": str(checkpoint.relative_to(run_dir)),
                    "sha256": fingerprint(checkpoint), "best_epoch_zero_based": saved["epoch"],
                    "best_epoch_one_based": saved["epoch"] + 1,
                    "validation_metrics": json_numbers(saved.get("val_metrics", {})),
                    "splits": summary["splits"], "holdout_evaluation": "not performed",
                    "warning": "Use best_checkpoint.pt, not an epoch-named end-of-training .pth file"}
        write_json(run_dir / "selected_model.json", selected)
        record.update(state="completed", training_directory=str(training_dir), selected_checkpoint=str(checkpoint))
        print(f"\nTraining and validation completed.\nRun directory: {run_dir}\nBest checkpoint: {checkpoint}\nTest set has NOT been evaluated.", flush=True)
    except BaseException as exc:
        record.update(state="interrupted" if isinstance(exc, KeyboardInterrupt) else "failed", error=str(exc))
        raise
    finally:
        record["finished_at"] = stamp()
        write_json(run_dir / "run_status.json", record)


if __name__ == "__main__":
    main()
