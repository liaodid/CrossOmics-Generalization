"""Sequential remaining figure folds: train, select by validation loss, then test.

Run with the training environment's Python. --dry_run requires only stdlib.
Resume only batches created by this script, with trusted local checkpoints.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

from run_proteintalks_fold import existing_path, SUFFIXES

CELLS = ['BT20', 'BT549', 'HCC1143', 'HCC1187', 'HCC1395', 'HCC1806',
         'HCC1937', 'HCC38', 'HCC70', 'MDA-MB-231', 'MDA-MB-436',
         'MDA-MB-453', 'MDA-MB-453(ATCC)', 'MDA-MB-468', 'T47D']
PREFIX = 'allcelltype_drugpair_crossdrug_'


def save(path, value):
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def counts_from_csv(data):
    times = defaultdict(set)
    with (data / (PREFIX + 'loo_label.csv')).open(encoding='utf-8-sig', newline='') as stream:
        for name, time in csv.reader(stream):
            if '#' in name:
                times[name].add(int(time))
    return Counter(name.split('_', 1)[0] for name, values in times.items()
                   if {6, 24, 48} <= values)


def run_logged(command, root, log_path, env):
    with log_path.open('a', encoding='utf-8', buffering=1) as log:
        log.write('\nCOMMAND: ' + json.dumps(command, ensure_ascii=False) + '\n')
        process = subprocess.Popen(command, cwd=root, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        try:
            for line in process.stdout:
                print(line, end='', flush=True)
                log.write(line)
            code = process.wait()
        except KeyboardInterrupt:
            # Console Ctrl+C also reaches the launcher, which cleans up its own
            # training child. Give that cleanup time before stopping the launcher.
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.terminate()
                process.wait(timeout=15)
            raise
        except BaseException:
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            raise
    if code:
        raise RuntimeError(f'Child process exited {code}; see {log_path}')


def resolve_training(root, fold, seed, batch, before):
    parent = root / 'results/proteintalks/cell_holdout' / fold / f'seed{seed}_bs{batch}'
    created = set(parent.glob('train_*')) - before
    if len(created) != 1:
        raise RuntimeError(f'Expected one new training run for {fold}, got {len(created)}')
    outer = created.pop()
    status = json.loads((outer / 'run_status.json').read_text(encoding='utf-8'))
    if status['state'] != 'completed':
        raise RuntimeError(f'Training did not complete: {outer}')
    training = Path(status['training_directory'])
    if not (training / 'best_checkpoint.pt').is_file():
        raise FileNotFoundError(training / 'best_checkpoint.pt')
    return training


def refresh_summary(batch_dir, state):
    fields = ['cell_line', 'state', 'train_n', 'val_n', 'test_n', 'test_auprc',
              'test_auroc', 'test_accuracy', 'test_f1', 'test_protein_mse',
              'checkpoint_epoch_zero_based', 'training_directory']
    with (batch_dir / 'fold_metrics.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for cell, fold in state['folds'].items():
            row = dict(cell_line=cell, state=fold['state'], training_directory=fold.get('training_directory', ''))
            if fold.get('metrics'):
                metric = fold['metrics']
                row.update(train_n=fold['splits']['train']['n'], val_n=fold['splits']['val']['n'],
                           test_n=metric['n'], test_auprc=metric['auprc_average_precision'],
                           test_auroc=metric['auroc'], test_accuracy=metric['accuracy_threshold_0.5'],
                           test_f1=metric['f1_threshold_0.5'],
                           test_protein_mse=metric['proteomics_mse_normalized_space'],
                           checkpoint_epoch_zero_based=metric['checkpoint_epoch_zero_based'])
            writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project_root', type=Path, default=Path.cwd())
    parser.add_argument('--baseline_dir', type=Path)
    parser.add_argument('--dataset_file_dir', type=Path)
    parser.add_argument('--cells', nargs='+', default=CELLS)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--random_seed', type=int, default=1995)
    parser.add_argument('--total_epoch', type=int, default=1000)
    parser.add_argument('--patience', type=int, default=500)
    parser.add_argument('--gpu', default='0')
    parser.add_argument('--resume', type=Path, help='Existing batch directory; keep original configuration')
    parser.add_argument('--dry_run', action='store_true')
    opts = parser.parse_args()
    if min(opts.batch_size, opts.total_epoch, opts.patience) < 1:
        parser.error('batch_size, total_epoch and patience must be positive')
    if len(set(opts.cells)) != len(opts.cells) or any(cell not in CELLS for cell in opts.cells):
        parser.error('--cells must be unique names from the 15 remaining figure cells')
    root = opts.project_root.resolve()
    baseline = existing_path(opts.baseline_dir, [root / 'PTV-1-main/ProteinTalks',
        root / 'baseline/proteintalks/PTV-1-main/ProteinTalks'], 'baseline')
    data = existing_path(opts.dataset_file_dir, [root / 'PTV1_dataset_20261015',
        root / 'data/proteintalks/PTV1_dataset_20261015'], 'data')
    entry = existing_path(None, [root / 'script/proteintalks_cell_holdout.py',
        root / 'script/script/proteintalks_cell_holdout.py'], 'holdout entry')
    scripts = Path(__file__).resolve().parent
    launcher, evaluator = scripts / 'run_proteintalks_fold.py', scripts / 'evaluate_proteintalks_holdout.py'
    paths = [entry, launcher, evaluator, Path(__file__).resolve(), *baseline.glob('*.py'),
             *[data / (PREFIX + suffix) for suffix in SUFFIXES]]
    if not (baseline / 'main.py').is_file():
        raise FileNotFoundError(baseline / 'main.py')
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)
    counts = counts_from_csv(data)
    total = sum(counts.values())
    print('CSV candidate counts (actual counts audited by Dataset on each fold):', flush=True)
    for cell in opts.cells:
        test_n = counts[cell]
        if not test_n:
            raise ValueError(f'No complete conditions for {cell}')
        train_n = int((total - test_n) * .8)
        print(f'  {cell}: train={train_n}, val={total-test_n-train_n}, test={test_n}', flush=True)
    config = dict(cells=opts.cells, batch_size=opts.batch_size, random_seed=opts.random_seed,
                  total_epoch=opts.total_epoch, patience=opts.patience, gpu=opts.gpu,
                  project_root=str(root), baseline_dir=str(baseline), dataset_file_dir=str(data))
    state = None
    if opts.resume:
        batch_dir = opts.resume.resolve()
        state = json.loads((batch_dir / 'batch_state.json').read_text(encoding='utf-8'))
        if state['config'] != config:
            parser.error('Resume configuration differs; use the original arguments')
    else:
        batch_dir = root / 'results/proteintalks/batches' / ('remaining_' + datetime.now().strftime('%Y%m%d_%H%M%S_') + uuid.uuid4().hex[:8])
    print(f'Batch directory: {batch_dir}', flush=True)
    if opts.dry_run:
        print('Dry run passed; no files written, no training/evaluation started.')
        return
    hashes = {str(path): fingerprint(path) for path in paths}
    if state is not None:
        if state['input_sha256'] != hashes:
            raise ValueError('Data or source changed since batch start; do not mix protocols')
    else:
        batch_dir.mkdir(parents=True, exist_ok=False)
        state = dict(config=config, input_sha256=hashes,
                     policy='Independent random initialization per cell; validation joint loss selects weights; test only after training. No test-based tuning.',
                     folds={cell: {'state': 'pending'} for cell in opts.cells})
    state_path = batch_dir / 'batch_state.json'
    save(state_path, state)
    env = os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES=opts.gpu, PYTHONIOENCODING='utf-8', PYTHONUTF8='1', MPLBACKEND='Agg')
    for cell, fold in state['folds'].items():
        if fold['state'] == 'completed':
            print(f'Skipping completed fold: {cell}', flush=True)
            continue
        try:
            if not fold.get('training_directory'):
                # Recover a completed child after an interruption before state was saved.
                if 'training_runs_before' not in fold:
                    parent = root / 'results/proteintalks/cell_holdout' / cell / f'seed{opts.random_seed}_bs{opts.batch_size}'
                    fold['training_runs_before'] = [str(p) for p in parent.glob('train_*')]
                    fold['state'] = 'training'
                    save(state_path, state)
                    command = [sys.executable, '-u', str(launcher), '--project_root', str(root),
                        '--baseline_dir', str(baseline), '--dataset_file_dir', str(data), '--entry_script', str(entry),
                        '--holdout_cell_line', cell, '--mode', 'train', '--batch_size', str(opts.batch_size),
                        '--random_seed', str(opts.random_seed), '--total_epoch', str(opts.total_epoch),
                        '--patience', str(opts.patience), '--gpu', opts.gpu]
                    run_logged(command, root, batch_dir / f'{cell}.log', env)
                training = resolve_training(root, cell, opts.random_seed, opts.batch_size,
                                            {Path(p) for p in fold['training_runs_before']})
                fold['training_directory'] = str(training)
                fold['state'] = 'trained'
                save(state_path, state)
            training = Path(fold['training_directory'])
            metrics_file = training / 'holdout_evaluation/holdout_metrics.json'
            if not metrics_file.is_file():
                fold['state'] = 'evaluating'
                save(state_path, state)
                command = [sys.executable, '-u', str(evaluator), '--run_dir', str(training),
                    '--baseline_dir', str(baseline), '--dataset_file_dir', str(data),
                    '--batch_size', str(opts.batch_size), '--device', 'cuda']
                run_logged(command, root, batch_dir / f'{cell}.log', env)
            metric = json.loads(metrics_file.read_text(encoding='utf-8'))
            if metric['holdout_cell_line'] != cell or fingerprint(training / 'best_checkpoint.pt') != metric['checkpoint_sha256']:
                raise ValueError('Evaluation checkpoint/cell mismatch')
            summary = json.loads((training / 'split_summary.json').read_text(encoding='utf-8'))
            fold.update(state='completed', metrics=metric, splits=summary['splits'])
            fold.pop('error', None)
            save(state_path, state)
            refresh_summary(batch_dir, state)
            print(f"Completed {cell}: AP={metric['auprc_average_precision']}, AUROC={metric['auroc']}", flush=True)
        except BaseException as exc:
            fold.update(state='interrupted' if isinstance(exc, KeyboardInterrupt) else 'failed', error=str(exc))
            save(state_path, state)
            refresh_summary(batch_dir, state)
            raise
    print(f'All requested folds completed. Summary: {batch_dir / "fold_metrics.csv"}', flush=True)


if __name__ == '__main__':
    main()
