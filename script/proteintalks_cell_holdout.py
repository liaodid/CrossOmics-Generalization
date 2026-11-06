"""Train upstream ProteinTalks with one cell line held out, without editing it.

Run from the repository root. Extra arguments are passed to upstream config.py.
Default: held-out data are saved as a manifest but never passed to Trainer.
"""
import argparse
import csv
import hashlib
import importlib
import importlib.metadata
import inspect
import json
import math
from pathlib import Path
import random
import sys

ROOT = next((parent for parent in Path(__file__).resolve().parents
             if (parent / "baseline/proteintalks/PTV-1-main/ProteinTalks/main.py").is_file()),
            Path(__file__).resolve().parents[1])


def install_scheduler_compatibility(torch):
    """Discard only the removed verbose argument on modern PyTorch."""
    original = torch.optim.lr_scheduler.ReduceLROnPlateau
    if "verbose" in inspect.signature(original).parameters:
        return

    class CompatibleReduceLROnPlateau(original):
        def __init__(self, *args, verbose=False, **kwargs):
            super().__init__(*args, **kwargs)

    torch.optim.lr_scheduler.ReduceLROnPlateau = CompatibleReduceLROnPlateau
    print("Compatibility: omitted removed scheduler verbose argument.", flush=True)


def cell_of(experiment):
    return experiment.split("_", 1)[0]


def split_conditions(experiments, holdout="MCF7", val_fraction=0.2, seed=1995):
    """Indices refer to loaded Dataset order, NOT raw CSV row numbers."""
    if not 0 < val_fraction < 1:
        raise ValueError("development_val_fraction must be between 0 and 1")
    if len(experiments) != len(set(experiments)):
        raise ValueError("Duplicate experiment IDs; cannot split safely")
    test = [i for i, name in enumerate(experiments) if cell_of(name) == holdout]
    development = [i for i, name in enumerate(experiments) if cell_of(name) != holdout]
    if not test:
        raise ValueError(f"No samples for {holdout!r}; available: {sorted(set(map(cell_of, experiments)))}")
    if len(development) < 2:
        raise ValueError("Not enough development samples")
    # Independent RNG: changing the split must not consume PyTorch model-init RNG.
    random.Random(seed).shuffle(development)
    train_count = math.floor(len(development) * (1 - val_fraction))
    if not 0 < train_count < len(development):
        raise ValueError("Empty training or validation set")
    splits = {"train": development[:train_count], "val": development[train_count:], "test": test}
    groups = [set(v) for v in splits.values()]
    assert not (groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2])
    assert set.union(*groups) == set(range(len(experiments)))
    assert all(cell_of(experiments[i]) != holdout for k in ("train", "val") for i in splits[k])
    return splits


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(dataset, splits, destination, args, options, nan_samples):
    import torch
    destination.mkdir(parents=True, exist_ok=True)
    names = dataset.get_experiment_types()
    summary = {}
    for split, indices in splits.items():
        torch.save(indices, destination / f"{split}_indices.pt")
        with (destination / f"{split}_samples.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["dataset_index", "experiment_type", "cell_line", "effective_label", "upstream_nan_replaced"])
            for i in indices:
                writer.writerow([i, names[i], cell_of(names[i]), float(dataset[i][3]), int(i in nan_samples)])
        positives = sum(float(dataset[i][3]) for i in indices)
        summary[split] = {"n": len(indices), "positives": positives,
                          "positive_fraction": positives / len(indices),
                          "cell_lines": sorted({cell_of(names[i]) for i in indices})}
    versions = {}
    for name in ["torch", "torchdyn", "torchdiffeq", "numpy", "pandas", "scikit-learn", "setuptools"]:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    hashes = {p.name: digest(p) for p in sorted(Path(args.dataset_file_dir).glob(args.trainval_file_prefix + "*.csv"))}
    code_hashes = {p.name: digest(p) for p in sorted(Path(options.baseline_dir).glob("*.py"))}
    code_hashes[Path(__file__).name] = digest(Path(__file__))
    record = {"holdout_cell_line": options.holdout_cell_line,
              "development_val_fraction": options.development_val_fraction,
              "seed": args.random_seed, "splits": summary, "arguments": vars(args),
              "environment": versions, "data_sha256": hashes, "code_sha256": code_hashes,
              "execution_options": vars(options),
              "gpu_backend": {"cuda_runtime": torch.version.cuda,
                              "cudnn_version": torch.backends.cudnn.version(),
                              "cudnn_enabled": torch.backends.cudnn.enabled},
              "label_policy": "Unmodified upstream loader: residual missing phenotype becomes 0; tensor NaNs become 1e-6.",
              "index_semantics": "Indices refer to loaded ProteomicsDataset, not raw CSV rows.",
              "training_test_policy": "Holdout is never passed to Trainer. Optional evaluation only after training.",
              "checkpoint_policy": "Random initialization; no official checkpoint is loaded."}
    (destination / "split_summary.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"Manifests saved to: {destination.resolve()}", flush=True)


def evaluate_holdout(args, dataset, indices, destination):
    """Only best deterministic checkpoint; no SWAG sampling or test adaptation."""
    import torch
    import numpy as np
    from sklearn.metrics import accuracy_score, average_precision_score, roc_auc_score
    from torch.utils.data import DataLoader, Subset
    from model import ppODE
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sample = dataset[indices[0]]
    model = ppODE(1, 1, args.hidden_size, 1, sample[0].shape[0], sample[4].shape[0], args.dropout_rate).to(device)
    checkpoint_path = destination / "best_checkpoint.pt"
    # Only read the checkpoint created by this run, including validation metadata.
    load_options = {"weights_only": False} if "weights_only" in inspect.signature(torch.load).parameters else {}
    checkpoint = torch.load(checkpoint_path, map_location=device, **load_options)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    probabilities, targets = [], []
    squared_error, element_count = 0.0, 0
    with torch.no_grad():
        for batch in DataLoader(Subset(dataset, indices), batch_size=args.batch_size, shuffle=False):
            x, pert, y, pheno, a, b = [value.to(device) for value in batch]
            predicted_y, p, _ = model(x, pert, a, b, args.time_stamp_predict_drug)
            probabilities.extend(p.cpu().tolist())
            targets.extend(pheno.cpu().tolist())
            squared_error += float(((predicted_y - y) ** 2).sum())
            element_count += y.numel()
    p = np.asarray(probabilities)
    target = np.asarray(targets)
    two_classes = len(np.unique(target)) == 2
    metrics = {"n": len(indices), "checkpoint": str(checkpoint_path), "epoch": checkpoint.get("epoch"),
               "accuracy_threshold_0.5": float(accuracy_score(target, p >= 0.5)),
               "auroc": float(roc_auc_score(target, p)) if two_classes else None,
               "auprc_average_precision": float(average_precision_score(target, p)) if two_classes else None,
               "proteomics_mse_normalized_space": squared_error / element_count,
               "note": "Deterministic checkpoint selected only by validation loss; upstream label/NaN policy retained."}
    with (destination / "holdout_predictions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["dataset_index", "experiment_type", "ground_truth", "predicted_probability", "predicted_label"])
        for i, label, prob in zip(indices, targets, probabilities):
            writer.writerow([i, dataset.get_experiment_types()[i], label, prob, int(prob >= 0.5)])
    (destination / "holdout_metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("Final held-out evaluation:", json.dumps(metrics, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--baseline_dir", default=str(ROOT / "baseline/proteintalks/PTV-1-main/ProteinTalks"))
    parser.add_argument("--holdout_cell_line", default="MCF7")
    parser.add_argument("--development_val_fraction", type=float, default=0.2)
    parser.add_argument("--split_only", action="store_true", help="Load, audit and save split; do not initialize/train model")
    parser.add_argument("--evaluate_holdout", action="store_true", help="Evaluate best deterministic checkpoint once after training")
    parser.add_argument("--disable_cudnn", action="store_true", help="Diagnostic fallback: keep CUDA, disable cuDNN convolution backend")
    options, upstream_arguments = parser.parse_known_args()
    if options.split_only and options.evaluate_holdout:
        parser.error("--split_only cannot be combined with --evaluate_holdout")
    if not (Path(options.baseline_dir) / "main.py").is_file():
        parser.error("Cannot find upstream main.py; check --baseline_dir")
    sys.path.insert(0, str(Path(options.baseline_dir).resolve()))
    sys.argv = [str(Path(options.baseline_dir) / "main.py")] + upstream_arguments
    from config import get_args, setup_device, setup_directories
    args = get_args()
    if args.train_from_scratch != "from_scratch" or args.cp_save_dir_best:
        parser.error("Cell-line holdout training requires random initialization; do not pass a checkpoint")
    if args.test_file_prefix or not args.trainval_file_prefix:
        parser.error("Provide --trainval_file_prefix only; do not supply --test_file_prefix")
    if args.indices_dir or args.indices_prefix:
        parser.error("This entry creates its own split; external indices are not supported")
    blocked = {"--train_percent", "--val_percent", "--test_percent"}
    if any(arg.split("=", 1)[0] in blocked for arg in upstream_arguments):
        parser.error("Use --development_val_fraction; upstream random-split percentages do not apply")
    if args.total_epoch < 1:
        parser.error("--total_epoch must be >= 1")
    import torch
    from torch.utils.data import DataLoader, Subset
    from dataset import ProteomicsDataset, clean_dataset
    install_scheduler_compatibility(torch)
    setup_device(args)
    if options.disable_cudnn:
        torch.backends.cudnn.enabled = False
    print(f"PyTorch={torch.__version__}; CUDA={torch.version.cuda}; "
          f"cuDNN={torch.backends.cudnn.version()}; cuDNN enabled={torch.backends.cudnn.enabled}", flush=True)
    if torch.cuda.is_available():
        print(f"GPU={torch.cuda.get_device_name(0)}", flush=True)
    dataset = ProteomicsDataset(args.trainval_file_prefix, args.dataset_file_dir, args.check_time_point)
    dataset, nan_samples = clean_dataset(dataset)
    splits = split_conditions(dataset.get_experiment_types(), options.holdout_cell_line,
                              options.development_val_fraction, args.random_seed)
    args.dir_save = setup_directories(args)
    destination = Path(args.dir_save)
    write_manifest(dataset, splits, destination, args, options, set(nan_samples))
    if options.split_only:
        print("Split only: no training, checkpoint loading or holdout evaluation.")
        return
    loaders = [DataLoader(Subset(dataset, splits[k]), batch_size=args.batch_size, shuffle=(k == "train"),
                          generator=torch.Generator().manual_seed(args.random_seed)) for k in ("train", "val")]
    upstream_main = importlib.import_module("main")
    # Reuse upstream model/optimizer/Trainer without changing upstream source files.
    upstream_main.get_args = lambda: args
    upstream_main.setup_directories = lambda current_args: str(destination)
    upstream_main.prepare_data = lambda current_args: (loaders[0], loaders[1], None, {
        k: sum(float(dataset[i][3]) for i in splits[k]) / len(splits[k]) for k in ("train", "val")})
    print(f"Training from scratch; {options.holdout_cell_line} NEVER enters Trainer.", flush=True)
    upstream_main.main()
    if options.evaluate_holdout:
        evaluate_holdout(args, dataset, splits["test"], destination)
    else:
        print("Holdout evaluation skipped; no test performance was used to tune this run.", flush=True)


if __name__ == "__main__":
    main()
