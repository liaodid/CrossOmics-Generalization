"""Audit copied fold artifacts without loading torch/pickle checkpoints."""
import csv
import hashlib
import json
import math
from pathlib import Path
import random
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/proteintalks/PTV1_dataset_20261015'
BASE = ROOT / 'baseline/proteintalks/PTV-1-main/ProteinTalks'
PREFIX = 'allcelltype_drugpair_crossdrug_'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def metrics(y, p):
    order = np.argsort(-p, kind='stable')
    yy, pp = y[order], p[order]
    ends = np.r_[np.flatnonzero(np.diff(pp)), len(p)-1]
    tp = np.cumsum(yy)[ends]
    ap = float(np.sum(np.diff(np.r_[0, tp]) * tp / (ends+1)) / y.sum())
    pair = p[y == 1, None] - p[y == 0][None, :]
    auc = float(np.mean((pair > 0) + .5*(pair == 0)))
    label = p >= .5
    cm = [[int(np.sum((y == i) & (label == j))) for j in (0, 1)] for i in (0, 1)]
    tn, fp, fn, truep = np.asarray(cm).ravel()
    return dict(auprc_average_precision=ap, auroc=auc,
                accuracy_threshold_0_5=float(np.mean(y == label)),
                f1_threshold_0_5=float(2*truep / (2*truep+fp+fn)), cm=cm)


def main():
    out = ROOT / 'outputs/proteintalks_audit'
    out.mkdir(parents=True, exist_ok=True)
    root = ROOT / 'results/proteintalks/cell_holdout'
    formal = sorted(root.glob('*/seed*/train_*/run_status.json'))
    data_hash = {p.name: sha(p) for p in DATA.glob(PREFIX+'*.csv')}
    first_labels = {}
    times = {}
    with (DATA / (PREFIX+'loo_label.csv')).open(newline='', encoding='utf-8-sig') as stream:
        raw_names = list(csv.reader(stream))
    with (DATA / (PREFIX+'pheno.csv')).open(newline='', encoding='utf-8-sig') as stream:
        raw_labels = list(csv.reader(stream))
    for (name, time), value in zip(raw_names, raw_labels):
        if name not in first_labels:
            label = float(value[0]) if value and value[0].strip() else float('nan')
            first_labels[name] = 0.0 if math.isnan(label) else label
        if '#' in name:
            times.setdefault(name, set()).add(int(time))
    expected_names = sorted(name for name, time in times.items() if {6,24,48} <= time)
    results, ignored, errors = [], [], []
    for status_path in formal:
        outer = status_path.parent
        status = read(status_path)
        if status['state'] != 'completed':
            ignored.append(dict(run=str(outer.relative_to(ROOT)), state=status['state']))
            continue
        issues = []
        def check(ok, message):
            if not ok:
                issues.append(message)
        try:
            summary_paths = list((outer / 'training').glob('*/split_summary.json'))
            check(len(summary_paths) == 1, 'Expected exactly one split summary')
            training = summary_paths[0].parent
            s = read(summary_paths[0])
            selected = read(outer / 'selected_model.json')
            m = read(training / 'holdout_evaluation/holdout_metrics.json')
            cell = s['holdout_cell_line']
            checkpoint_sha = sha(training / 'best_checkpoint.pt')
            check(checkpoint_sha == m['checkpoint_sha256'] == selected['sha256'], 'Checkpoint SHA mismatch')
            check(selected['best_epoch_zero_based'] == m['checkpoint_epoch_zero_based'], 'Best epoch mismatch')
            check(m['holdout_cell_line'] == cell == outer.parents[1].name, 'Cell name mismatch')
            check(s['data_sha256'] == data_hash, 'Data hashes differ from local source')
            for name in ('model.py', 'dataset.py'):
                check(s['code_sha256'][name] == sha(BASE / name), 'Local upstream differs: '+name)
                check(s['code_sha256'][name] == sha(outer / 'source_snapshot/upstream' / name), 'Snapshot differs: '+name)
            manifests = {k: rows(training / (k+'_samples.csv')) for k in ('train','val','test')}
            all_rows = sum(manifests.values(), [])
            indexed = sorted(all_rows, key=lambda r: int(r['dataset_index']))
            names = [r['experiment_type'] for r in indexed]
            check([int(r['dataset_index']) for r in indexed] == list(range(len(expected_names))), 'Duplicate/missing dataset indices')
            check(names == expected_names, 'Dataset IDs differ from complete source conditions')
            for k, group in manifests.items():
                check(len(group) == s['splits'][k]['n'], k+' count mismatch')
                check(sum(float(r['effective_label']) for r in group) == s['splits'][k]['positives'], k+' positives mismatch')
                for r in group:
                    check(r['cell_line'] == r['experiment_type'].split('_',1)[0], 'Manifest cell label mismatch')
                    check((r['cell_line'] == cell) == (k == 'test'), 'Holdout leaked into development')
                    check(float(r['effective_label']) == first_labels[r['experiment_type']], 'Label differs from upstream source')
            dev = [i for i,name in enumerate(names) if name.split('_',1)[0] != cell]
            random.Random(s['seed']).shuffle(dev)
            cut = math.floor(len(dev)*(1-s['development_val_fraction']))
            check([int(r['dataset_index']) for r in manifests['train']] == dev[:cut], 'Train split not reproducible')
            check([int(r['dataset_index']) for r in manifests['val']] == dev[cut:], 'Val split not reproducible')
            pred = rows(training / 'holdout_evaluation/holdout_predictions.csv')
            check([r['experiment_type'] for r in pred] == [r['experiment_type'] for r in manifests['test']], 'Prediction ID/order mismatch')
            check([r['dataset_index'] for r in pred] == [r['dataset_index'] for r in manifests['test']], 'Prediction index mismatch')
            y = np.array([float(r['ground_truth']) for r in pred])
            p = np.array([float(r['predicted_probability']) for r in pred])
            check(np.array_equal(y, [float(r['effective_label']) for r in manifests['test']]), 'Prediction target mismatch')
            check(np.isfinite(p).all() and ((p>=0)&(p<=1)).all(), 'Invalid probabilities')
            check(np.array_equal(p>=.5, [int(r['predicted_label']) for r in pred]), 'Threshold labels mismatch')
            recomputed = metrics(y,p)
            for key in ('auprc_average_precision','auroc','accuracy_threshold_0_5','f1_threshold_0_5'):
                recorded_key = key.replace('_0_5','_0.5')
                check(abs(recomputed[key]-m[recorded_key]) < 1e-10, 'Metric mismatch '+key)
            check(recomputed['cm'] == m['confusion_matrix_rows_true_cols_pred_0_1'], 'Confusion matrix mismatch')
            check(len(y) == m['n'] and int(y.sum()) == m['positives'], 'Test count mismatch')
            check(sum(int(r['upstream_nan_replaced']) for r in manifests['test']) == m['test_samples_with_upstream_nan_replacement'], 'NaN replacement count mismatch')
            with np.load(training / 'holdout_evaluation/holdout_proteomics.npz', allow_pickle=False) as npz:
                yp, yt = npz['predictions'], npz['ground_truth']
                check(yp.shape == yt.shape == (len(y),3,5585,1), 'Unexpected NPZ shape')
                check(np.isfinite(yp).all() and np.isfinite(yt).all(), 'Nonfinite NPZ values')
                check(npz['experiment_types'].tolist() == [r['experiment_type'] for r in pred], 'NPZ ID mismatch')
                check(npz['time_hours'].tolist() == [6,24,48], 'NPZ timepoints mismatch')
                mse = float(np.mean((yp.astype('float64')-yt)**2))
                check(abs(mse-m['proteomics_mse_normalized_space']) < 1e-10, 'Protein MSE mismatch')
            log = (outer / 'train.log').read_text(encoding='utf-8', errors='replace')
            check('Training completed.' in log, 'Training completion not in log')
            check('Traceback (most recent call last)' not in log, 'Traceback in completed training log')
            a = s['arguments']
            result = dict(cell_line=cell, batch_size=a['batch_size'], seed=s['seed'],
                train_n=len(manifests['train']), val_n=len(manifests['val']), test_n=m['n'],
                ap=m['auprc_average_precision'], auc=m['auroc'], accuracy=m['accuracy_threshold_0.5'],
                f1=m['f1_threshold_0.5'], protein_mse=mse, positive_fraction=m['positive_fraction'],
                nan_replaced=m['test_samples_with_upstream_nan_replacement'],
                best_epoch_zero_based=m['checkpoint_epoch_zero_based'],
                issues=issues, training_directory=str(training.relative_to(ROOT)),
                configuration={k:a[k] for k in ['hidden_size','dropout_rate','learning_rate','lambda_pheno','total_epoch','patience','use_swag','train_from_scratch']})
            results.append(result)
            print(cell, 'PASS' if not issues else issues, f"AP={result['ap']:.4f}", flush=True)
        except Exception as exc:
            errors.append(dict(run=str(outer.relative_to(ROOT)), error=repr(exc), issues=issues))
    group64 = [r for r in results if r['batch_size'] == 64]
    macro = {k:float(np.mean([r[k] for r in group64])) for k in ('ap','auc','accuracy','f1','protein_mse')}
    report = dict(folds=results, excluded_noncompleted_runs=ignored, errors=errors,
                  bs64_macro_mean=macro, bs64_test_total=sum(r['test_n'] for r in group64),
                  checks='Source hashes, manifests, exact cell isolation, split reproducibility, original phenotype labels, checkpoint file SHA, independent classification metrics, NPZ shape/IDs/finiteness/MSE; no torch inference rerun or checkpoint unpickling.')
    (out / 'audit_results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    text = ['# ProteinTalks 结果检查\n', f'完成并读取：{len(results)} 折；异常：{len(errors)}；未完成运行：{len(ignored)}。\n',
        '|细胞系|batch|训练/验证/测试|AP|AUROC|Accuracy|F1|蛋白MSE|检查|', '|---|---:|---|---:|---:|---:|---:|---:|---|']
    for r in results:
        text.append(f"|{r['cell_line']}|{r['batch_size']}|{r['train_n']}/{r['val_n']}/{r['test_n']}|{r['ap']:.4f}|{r['auc']:.4f}|{r['accuracy']:.4f}|{r['f1']:.4f}|{r['protein_mse']:.5f}|{'通过' if not r['issues'] else '; '.join(r['issues'])}|")
    text += ['', '64 批大小的 15 折等权平均：'+json.dumps(macro), '',
        '检查范围：数据和代码指纹、细胞系隔离、划分重建、原始表型标签、checkpoint 文件哈希、独立重算分类指标、NPZ 维度/ID/有限值/蛋白 MSE。未重跑模型前向推理，未读取 checkpoint 内部对象。', '',
        '历史中断运行：'+json.dumps(ignored, ensure_ascii=False), '', '读取异常：'+json.dumps(errors, ensure_ascii=False), '',
        '解释限制：单种子；MCF7/HS578T 与其余折 batch 不同；标签版本和原文划分未严格对齐；上游缺失标签置零与 NaN 替换规则保留。']
    (out / 'audit_report.md').write_text('\n'.join(text), encoding='utf-8')
    print(json.dumps(dict(completed=len(results), issues=sum(bool(r['issues']) for r in results), errors=errors, excluded=ignored, macro64=macro), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
