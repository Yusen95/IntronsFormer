import argparse
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import run_pipeline as pipeline
from scripts.runtime_options import resolve_runtime


class PipelineTests(unittest.TestCase):
    def test_example_runs_existing_scripts_and_rejects_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'results with spaces'
            pipeline.main(['preprocess', '--example', '--output-dir', str(output)])
            self.assertTrue((output / 'PIPELINE_COMPLETE').is_file())
            self.assertFalse((output / 'datasets.txt').exists())
            for name, count in [('IR.bed', 10670), ('nonIR.bed', 55360),
                                ('IR.windows.bed', 10354), ('nonIR.windows.bed', 44436)]:
                with (output / 'K562' / name).open() as handle:
                    self.assertEqual(sum(1 for _ in handle), count)
            with self.assertRaisesRegex(ValueError, 'new or empty'):
                pipeline.main(['preprocess', '--example', '--output-dir', str(output)])

    def test_preprocess_manifest_order_paths_and_dataset_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'input with spaces').write_text('fixture')
            manifest = base / 'inputs.tsv'
            manifest.write_text('\t'.join(pipeline.FIELDS) + '\n' + ''.join(
                sample + '\t' + '\t'.join(['input with spaces'] * 7) + '\n'
                for sample in ['K562', 'GM12878']))
            out = base / 'processed'
            # Simulate external BigWig stages to test orchestration and handoff;
            # this does not claim to test pyBigWig or the model.
            def produce(command, **kwargs):
                if '--output' in command:
                    Path(command[command.index('--output') + 1]).write_text('fixture')
                elif command[1].endswith('02_filter_bed_windows.py'):
                    Path(command[-1]).write_text('fixture')
            with patch.object(pipeline.subprocess, 'run', side_effect=produce) as run:
                pipeline.main(['preprocess', '--manifest', str(manifest), '--output-dir', str(out)])
            self.assertEqual(run.call_count, 12)
            self.assertEqual((out / 'datasets.txt').read_text().splitlines(),
                             ['K562/model_input.npz', 'GM12878/model_input.npz'])
            args = pipeline.parse_args(['train', '--dataset-list', str(out/'datasets.txt'),
                '--batch-size', '2', '--accumulation-steps', '32', '--device', 'cpu',
                '--precision', 'fp32', '--torch-threads', '2'])
            commands, _, _ = pipeline.model_plan(args, base/'model')
            command = commands[0]
            self.assertEqual(command[command.index('--batch-size')+1], '2')
            self.assertEqual(command[command.index('--accumulation-steps')+1], '32')
            self.assertEqual(command[command.index('--device')+1], 'cpu')
            self.assertEqual(command[command.index('--torch-threads')+1], '2')
            self.assertLess(command.index(str((out/'K562/model_input.npz').resolve())),
                            command.index(str((out/'GM12878/model_input.npz').resolve())))

    def test_interpretation_covers_both_signs_and_both_databases(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            for name in ('data.npz', 'model.pt', 'tf.meme', 'rbp.meme'):
                (base/name).write_text('fixture')
            args = pipeline.parse_args(['interpret', '--datasets', str(base/'data.npz'),
                '--checkpoint', str(base/'model.pt'), '--tf-db', str(base/'tf.meme'),
                '--rbp-db', str(base/'rbp.meme'), '--infer-batch-size', '1', '--internal-batch-size', '1'])
            with patch.object(pipeline.shutil, 'which', return_value='tomtom'):
                commands, expected, _ = pipeline.model_plan(args, base/'out')
            self.assertEqual(len(commands), 13)
            searches = [c for c in commands if c[0] == 'tomtom']
            self.assertEqual([Path(c[2]).name for c in searches],
                             ['tf_pos', 'rbp_pos', 'tf_neg', 'rbp_neg'])
            self.assertEqual(len(expected), 6)
            self.assertEqual(commands[0][commands[0].index('--infer-batch-size')+1], '1')

    def test_dry_run_writes_nothing_and_failure_stops_pipeline(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)/'output'
            with patch.object(pipeline.subprocess, 'run') as run, contextlib.redirect_stdout(io.StringIO()):
                pipeline.main(['preprocess', '--example', '--output-dir', str(out), '--dry-run'])
                run.assert_not_called()
            self.assertFalse(out.exists())
            with patch.object(pipeline.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'stage')) as run:
                with self.assertRaises(subprocess.CalledProcessError):
                    pipeline.main(['preprocess', '--example', '--output-dir', str(out)])
                self.assertEqual(run.call_count, 1)
            self.assertFalse((out/'PIPELINE_COMPLETE').exists())

    def test_missing_input_and_invalid_sizes_rejected_before_launch(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory)/'absent.txt'
            with patch.object(pipeline.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'Missing or empty'):
                    pipeline.main(['train', '--dataset-list', str(missing)])
                run.assert_not_called()
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    pipeline.parse_args(['train','--datasets','x.npz','--batch-size','0'])

    def test_precision_fallback_and_explicit_cpu(self):
        fake = Mock()
        fake.cuda.is_available.return_value = True
        fake.cuda.is_bf16_supported.return_value = False
        fake.device.side_effect = lambda name: name
        args = argparse.Namespace(device='auto', precision='auto', torch_threads=2)
        with patch.dict(sys.modules, {'torch': fake}):
            self.assertEqual(resolve_runtime(args), ('cuda', False))
            args.precision = 'bf16'
            with self.assertRaisesRegex(ValueError, 'BF16'):
                resolve_runtime(args)
            args.device, args.precision = 'cpu', 'fp32'
            self.assertEqual(resolve_runtime(args), ('cpu', False))
            fake.set_num_threads.assert_called_with(2)
            args.device = 'cuda'
            fake.cuda.is_available.return_value = False
            with self.assertRaisesRegex(ValueError, 'CUDA is unavailable'):
                resolve_runtime(args)


if __name__ == '__main__':
    unittest.main()
