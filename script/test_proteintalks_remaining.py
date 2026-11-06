"""Exercise batch orchestration with fake children, without torch or GPU."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import run_proteintalks_remaining as batch


class BatchTest(unittest.TestCase):
    def test_evaluation_failure_resumes_without_retraining(self):
        scratch = Path(__file__).resolve().parents[1] / 'tmp'
        scratch.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch, prefix='batch_test_') as temp:
            root = Path(temp)
            data = root / 'PTV1_dataset_20261015'
            baseline = root / 'PTV-1-main/ProteinTalks'
            entry = root / 'script/proteintalks_cell_holdout.py'
            data.mkdir()
            baseline.mkdir(parents=True)
            entry.parent.mkdir()
            entry.write_text('# fake', encoding='utf-8')
            (baseline / 'main.py').write_text('# fake', encoding='utf-8')
            for suffix in batch.SUFFIXES:
                (data / (batch.PREFIX + suffix)).write_text('', encoding='utf-8')
            (data / (batch.PREFIX + 'loo_label.csv')).write_text(
                'BT20_#1,6\nBT20_#1,24\nBT20_#1,48\nBT20_#2,6\n'
                'BT549_#1,6\nBT549_#1,24\nBT549_#1,48\n', encoding='utf-8')
            self.assertEqual(batch.counts_from_csv(data), {'BT20': 1, 'BT549': 1})
            calls = []
            fail_eval = [True]

            def fake_run(command, root, log, env):
                args = lambda name: command[command.index(name) + 1]
                is_train = '--holdout_cell_line' in command
                calls.append('train' if is_train else 'eval')
                if is_train:
                    outer = root / 'results/proteintalks/cell_holdout/BT20/seed1995_bs32/train_fake'
                    training = outer / 'training/hash'
                    training.mkdir(parents=True)
                    (training / 'best_checkpoint.pt').write_bytes(b'fake-checkpoint')
                    batch.save(outer / 'run_status.json', dict(state='completed', training_directory=str(training)))
                    batch.save(training / 'split_summary.json', dict(splits={'train': {'n': 1}, 'val': {'n': 1}}))
                else:
                    if fail_eval.pop() if fail_eval else False:
                        raise RuntimeError('simulated evaluator failure')
                    training = Path(args('--run_dir'))
                    output = training / 'holdout_evaluation'
                    output.mkdir()
                    batch.save(output / 'holdout_metrics.json', {
                        'holdout_cell_line': 'BT20', 'n': 1,
                        'auprc_average_precision': .7, 'auroc': .8, 'accuracy_threshold_0.5': .9,
                        'f1_threshold_0.5': .6, 'proteomics_mse_normalized_space': .1,
                        'checkpoint_epoch_zero_based': 3,
                        'checkpoint_sha256': batch.fingerprint(training / 'best_checkpoint.pt')})

            args = ['batch', '--project_root', str(root), '--cells', 'BT20']
            with patch.object(batch, 'run_logged', side_effect=fake_run), contextlib.redirect_stdout(io.StringIO()):
                with patch('sys.argv', args), self.assertRaisesRegex(RuntimeError, 'simulated'):
                    batch.main()
                batch_dir = next((root / 'results/proteintalks/batches').iterdir())
                with patch('sys.argv', args + ['--resume', str(batch_dir)]):
                    batch.main()
                self.assertEqual(calls, ['train', 'eval', 'eval'])
                with patch('sys.argv', args + ['--resume', str(batch_dir)]):
                    batch.main()
                self.assertEqual(calls, ['train', 'eval', 'eval'])
                state = json.loads((batch_dir / 'batch_state.json').read_text(encoding='utf-8'))
                self.assertEqual(state['folds']['BT20']['state'], 'completed')
                self.assertIn('0.7', (batch_dir / 'fold_metrics.csv').read_text(encoding='utf-8-sig'))

    def test_figure_targets(self):
        self.assertEqual(len(batch.CELLS), 15)
        self.assertEqual(len(set(batch.CELLS)), 15)
        self.assertFalse({'MCF7', 'HS578T', 'DU4475'} & set(batch.CELLS))


if __name__ == '__main__':
    unittest.main()
