"""Regression checks for local CLI/file handling; no external data or GPU needed."""
import csv
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PortabilityTests(unittest.TestCase):
    def command(self, script, *args):
        return subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / script), *map(str, args)],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )

    def test_meme_large_field_and_new_output_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'motifs.csv'
            output = Path(directory) / 'new' / 'motifs.meme'
            with source.open('w', newline='') as handle:
                writer = csv.writer(handle)
                writer.writerow(['Motif_ID', 'Motif_Seq', 'Occurrences', 'Positions'])
                writer.writerow(['motif_1', 'ACGTA', 3, 'x' * 200000])
            result = self.command('08_motifs_to_meme.py', '--in', source, '--out', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            text = output.read_text()
            self.assertIn('w= 5 nsites= 3', text)
            self.assertEqual(text.count('MOTIF '), 1)

    def test_auxiliary_scripts_expose_paths_without_running_analysis(self):
        scripts = {
            'prepare_encode_knockdown.py': '--input-dir',
            'create_knockdown_new_only_scripts.py': '--comparison',
            'summarize_encode_prediction_vs_control_event_counts.py': '--support',
            'summarize_prediction_pos_both_neg_with_control_event_counts.py': '--input',
        }
        for script, option in scripts.items():
            with self.subTest(script=script):
                result = self.command(script, '--help')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(option, result.stdout)

    def test_threshold_summary_creates_output_parent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lists = root / 'results' / 'TEST_K562_result' / 'lists'
            lists.mkdir(parents=True)
            (lists / 'allIntrons.txt').write_text(
                'adjPValue\tlogFoldChange\n0.001\t1\n0.005\t-2\n0.5\t1\n'
            )
            output = root / 'new' / 'summary.tsv'
            result = self.command('summarize_idiffir_allIntrons_adjP_threshold_HPCC.py',
                                  '--idiffir-dir', root / 'results', '--out', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            with output.open() as handle:
                row = next(csv.DictReader(handle, delimiter='\t'))
            self.assertEqual((row['all_events'], row['up_events'], row['down_events']), ('2', '1', '1'))

    def test_list_summary_creates_all_output_parents(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            lists = root / 'results' / 'USF1_K562_result' / 'lists'
            lists.mkdir(parents=True)
            for filename, content in [('allDIRs.txt', 'a\nb\n'), ('upDIRs.txt', 'a\n'), ('downDIRs.txt', 'b\n')]:
                (lists / filename).write_text(content)
            args = ['--idiffir-dir', root / 'results']
            for option, filename in [('pos-tf', 'Pos_TF.tsv'), ('neg-tf', 'Neg_TF.tsv'),
                                     ('pos-rbp', 'Pos_RBP.tsv'), ('neg-rbp', 'Neg_RBP.tsv'), ('meme', 'Homo_sapiens.meme')]:
                args += ['--' + option, ROOT / 'metadata' / 'knockdown' / filename]
            for option in ['tf-out', 'rbp-out', 'combined-out', 'audit-out']:
                args += ['--' + option, root / option / 'counts.tsv']
            result = self.command('summarize_tf_rbp_prediction_control_idiffir_counts_HPCC.py', *args)
            self.assertEqual(result.returncode, 0, result.stderr)
            with (root / 'combined-out' / 'counts.tsv').open() as handle:
                rows = list(csv.DictReader(handle, delimiter='\t'))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['all_events'], '2')


if __name__ == '__main__':
    unittest.main()
