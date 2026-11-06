"""Evaluate saved MCF7 holdout once, using best_checkpoint.pt and saved IDs.

Does not train, reconstruct random splits, choose checkpoints, or adapt on test.
Only load a run directory containing checkpoints that you created and trust.
"""
import argparse
import csv
import hashlib
import inspect
import json
import math
from pathlib import Path
import sys


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_manifests(run_dir, summary):
    manifests = {}
    holdout = summary["holdout_cell_line"]
    for split in ("train", "val", "test"):
        with (run_dir / f"{split}_samples.csv").open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        if len(rows) != summary["splits"][split]["n"] or not rows:
            raise ValueError(f"Unexpected {split} sample count")
        for row in rows:
            cell = row["experiment_type"].split("_", 1)[0]
            if row["cell_line"] != cell or ((cell == holdout) != (split == "test")):
                raise ValueError(f"Cell-line isolation failed: {split} {row}")
            if float(row["effective_label"]) not in (0.0, 1.0):
                raise ValueError("Expected binary effective labels")
        manifests[split] = rows
    all_rows = sum(manifests.values(), [])
    indices = [int(row["dataset_index"]) for row in all_rows]
    ids = [row["experiment_type"] for row in all_rows]
    if sorted(indices) != list(range(len(all_rows))) or len(set(ids)) != len(ids):
        raise ValueError("Duplicate, overlapping or missing manifest IDs/indices")
    return manifests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run_dir", type=Path, required=True)
    parser.add_argument("--baseline_dir", type=Path, required=True)
    parser.add_argument("--dataset_file_dir", type=Path, required=True)
    parser.add_argument("--batch_size", type=int, default=8)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    options = parser.parse_args()
    if options.batch_size < 1:
        parser.error("batch_size must be positive")
    run_dir = options.run_dir.resolve()
    summary = json.loads((run_dir / "split_summary.json").read_text(encoding="utf-8"))
    manifests = audit_manifests(run_dir, summary)
    # Use the checkpoint saved inside the validation-improvement branch, not the
    # epoch-named end-of-training file (which may contain last-epoch weights).
    checkpoint_path = run_dir / "best_checkpoint.pt"
    if not checkpoint_path.is_file():
        raise FileNotFoundError(checkpoint_path)
    print("Verifying training data and model/loader fingerprints...", flush=True)
    for filename, expected in summary["data_sha256"].items():
        path = options.dataset_file_dir / filename
        if sha256(path) != expected:
            raise ValueError(f"Data differs from training: {path}")
    for filename in ("dataset.py", "model.py"):
        if sha256(options.baseline_dir / filename) != summary["code_sha256"][filename]:
            raise ValueError(f"Model/loader differs from training: {filename}")
    print("Fingerprints and saved split isolation verified.", flush=True)

    import torch
    import numpy as np
    from sklearn.metrics import (accuracy_score, average_precision_score,
                                 confusion_matrix, f1_score, roc_auc_score)
    from torch.utils.data import DataLoader, Subset
    sys.path.insert(0, str(options.baseline_dir.resolve()))
    from dataset import ProteomicsDataset, clean_dataset
    from model import ppODE
    args = summary["arguments"]
    torch.manual_seed(summary["seed"])
    np.random.seed(summary["seed"])
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.enabled = summary.get("gpu_backend", {}).get("cudnn_enabled", True)
    device = options.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable")
    print(f"Device={device}; holdout={summary['holdout_cell_line']}; no training.", flush=True)
    dataset = ProteomicsDataset(args["trainval_file_prefix"], str(options.dataset_file_dir), args["check_time_point"])
    dataset, nan_samples = clean_dataset(dataset)
    all_rows = sum(manifests.values(), [])
    if len(dataset) != len(all_rows):
        raise ValueError("Loaded dataset size differs from saved manifest")
    names = dataset.get_experiment_types()
    for row in all_rows:
        i = int(row["dataset_index"])
        if names[i] != row["experiment_type"] or float(dataset[i][3]) != float(row["effective_label"]):
            raise ValueError(f"Loaded sample differs from manifest at index {i}")
    test_rows = manifests["test"]
    indices = [int(row["dataset_index"]) for row in test_rows]
    n_protein = dataset[indices[0]][0].shape[0]
    n_drug = dataset[indices[0]][4].shape[0]
    model = ppODE(1, 1, args["hidden_size"], 1, n_protein, n_drug, args["dropout_rate"]).to(device)
    load_options = {"weights_only": False} if "weights_only" in inspect.signature(torch.load).parameters else {}
    # This checkpoint is the user's own saved training output, including metadata.
    checkpoint = torch.load(checkpoint_path, map_location="cpu", **load_options)
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.eval()
    probs, targets, pro_predictions, pro_targets = [], [], [], []
    loader = DataLoader(Subset(dataset, indices), batch_size=options.batch_size, shuffle=False)
    with torch.no_grad():
        for batch in loader:
            x, pert, y, pheno, a, b = [value.to(device) for value in batch]
            y_hat, probability, _ = model(x, pert, a, b, args["time_stamp_predict_drug"])
            probs.extend(probability.cpu().tolist())
            targets.extend(pheno.cpu().tolist())
            pro_predictions.append(y_hat.cpu().numpy())
            pro_targets.append(y.cpu().numpy())
    probs = np.asarray(probs)
    targets = np.asarray(targets)
    predicted_y, true_y = np.concatenate(pro_predictions), np.concatenate(pro_targets)
    if not (np.isfinite(probs).all() and np.isfinite(predicted_y).all()):
        raise ValueError("Nonfinite predictions; do not report metrics")
    if not ((probs >= 0).all() and (probs <= 1).all()):
        raise ValueError("Predicted probabilities outside [0,1]")
    two_classes = len(np.unique(targets)) == 2
    metrics = {
        "holdout_cell_line": summary["holdout_cell_line"], "n": len(indices),
        "positives": int(targets.sum()), "positive_fraction": float(targets.mean()),
        "accuracy_threshold_0.5": float(accuracy_score(targets, probs >= 0.5)),
        "auprc_average_precision": float(average_precision_score(targets, probs)) if two_classes else None,
        "auroc": float(roc_auc_score(targets, probs)) if two_classes else None,
        "f1_threshold_0.5": float(f1_score(targets, probs >= 0.5, zero_division=0)),
        "confusion_matrix_rows_true_cols_pred_0_1": confusion_matrix(targets, probs >= 0.5, labels=[0, 1]).tolist(),
        "proteomics_mse_normalized_space": float(np.mean((predicted_y.astype('float64') - true_y) ** 2)),
        "all_negative_accuracy_baseline": float((targets == 0).mean()),
        "random_ranking_AP_reference_prevalence": float(targets.mean()),
        "test_samples_with_upstream_nan_replacement": sum(i in set(nan_samples) for i in indices),
        "checkpoint": str(checkpoint_path), "checkpoint_sha256": sha256(checkpoint_path),
        "checkpoint_epoch_zero_based": int(checkpoint["epoch"]),
        "weight_selection": "Best saved validation joint loss, no test-based selection; deterministic, no SWAG.",
        "data_and_model_loader_sha256_verified": True,
        "environment": {"torch": torch.__version__, "cuda": torch.version.cuda, "device": device},
        "label_policy": summary["label_policy"],
        "limitations": "Own 80/20 development split; upstream residual missing labels/NaN replacements retained; not an exact reproduction of the paper's original fold."
    }
    if not all(math.isfinite(value) for value in metrics.values() if isinstance(value, float)):
        raise ValueError("Nonfinite metric")
    output = run_dir / "holdout_evaluation"
    output.mkdir(exist_ok=True)
    with (output / "holdout_predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["dataset_index", "experiment_type", "ground_truth", "predicted_probability", "predicted_label"])
        for row, label, prob in zip(test_rows, targets, probs):
            writer.writerow([row["dataset_index"], row["experiment_type"], int(label), float(prob), int(prob >= 0.5)])
    np.savez_compressed(output / "holdout_proteomics.npz", predictions=predicted_y, ground_truth=true_y,
                        experiment_types=np.asarray([row["experiment_type"] for row in test_rows]),
                        time_hours=np.asarray([6, 24, 48]))
    (output / "holdout_metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2), flush=True)
    print(f"Evaluation completed. Outputs: {output}", flush=True)


if __name__ == "__main__":
    main()
