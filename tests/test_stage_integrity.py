"""Regression checks for standalone stages and generated shell jobs."""
import csv
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = 'C:/Program Files/Git/bin/bash.exe' if os.name == 'nt' and Path('C:/Program Files/Git/bin/bash.exe').exists() else shutil.which('bash')


def load_script(name):
    spec = importlib.util.spec_from_file_location('audit_module', ROOT / 'scripts' / name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StageTests(unittest.TestCase):
    def test_standalone_preprocessing_creates_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = load_script('01_filter_ir_events.py')
            second = load_script('02_filter_bed_windows.py')
            ir, nonir = root/'ir/events.bed', root/'nonir/events.bed'
            first.main(ROOT/'example/cufflinks/K562_genes.fpkm_tracking',
                       ROOT/'example/irfinder/K562_IRFinder-IR-dir.txt', ir, nonir)
            second.main(ir, root/'windows/events.bed')
            self.assertEqual(len((root/'windows/events.bed').read_text().splitlines()), 10354)

    def test_large_ig_fields_and_single_base(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            # Field length exceeds csv's default 131072 bytes.
            scores = ['0.000000'] * 15000 + ['1.000000'] * 4995 + ['10.000000'] * 5
            for name, rows in [('seq', [['0'], [','.join(['0'] * len(scores))]]),
                               ('score', [['1.0'], [','.join(scores)]])]:
                with (root/name).open('w', newline='') as handle:
                    csv.writer(handle).writerows(rows)
            out = root/'new/motifs.csv'
            result = subprocess.run([sys.executable, str(ROOT/'scripts/07_extract_ig_motifs.py'),
                '--seq', str(root/'seq'), '--score', str(root/'score'), '--out', str(out),
                '--direction', 'pos', '--count', '1'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with out.open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual([row['Motif_Seq'] for row in rows], ['AAAAA'])

    def test_tomtom_invalid_qvalues_are_not_matches(self):
        module = load_script('tomtom_to_tf.py')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'tomtom.tsv'
            path.write_text('Target_ID\tq-value\nA\tnan\nB\t-0.1\nC\tinf\nD\t0.01\n')
            matches, _ = module.parse_tomtom(path, {x:x for x in 'ABCD'}, .05)
            self.assertEqual(matches, {'D': .01})

    @unittest.skipUnless(BASH, 'Bash required')
    def test_failed_download_is_not_reused(self):
        module = load_script('prepare_encode_knockdown.py')
        row = dict(Local_Subdir='TF_knockdown/TEST', Local_File='one.fastq.gz',
                   Run_ID='TEST', Condition='KO', Replicate_Index='1', Read='1',
                   File_Accession='ENCFFTEST', Download_URL='https://example.invalid/test')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            script = root/'download.sh'
            module.write_download_script(script, [row])
            body = script.read_text()
            prefix = 'wget() { printf partial > "$3"; return 1; }\n'
            env = dict(os.environ, BASE_DIR=root.as_posix())
            failed = subprocess.run([BASH], input=prefix+body, text=True, capture_output=True, env=env)
            self.assertNotEqual(failed.returncode, 0)
            target = root/row['Local_Subdir']/row['Local_File']
            self.assertFalse(target.exists())
            prefix = 'wget() { printf complete | gzip -c > "$3"; }\n'
            passed = subprocess.run([BASH], input=prefix+body, text=True, capture_output=True, env=env)
            self.assertEqual(passed.returncode, 0, passed.stderr)
            self.assertTrue(target.exists())
            skipped = subprocess.run([BASH], input='wget() { return 99; }\n'+body,
                                     text=True, capture_output=True, env=env)
            self.assertEqual(skipped.returncode, 0, skipped.stderr)

    @unittest.skipUnless(BASH, 'Bash required')
    def test_peak_download_does_not_skip_other_accessions(self):
        body = (ROOT/'scripts/download_encode_peaks_from_selected_tsv.sh').read_text()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            fields = ['positive', 'TF', 'TEST', 'TEST', 'K562', 'ENCSRTEST', 'ChIP-seq',
                      'ENCFFNEW', 'GRCh38', 'peaks', '1', 'date', 'date', 'date',
                      'https://example.invalid/test', 'experiment', 'file']
            manifest = root/'selected.tsv'
            manifest.write_text('\t'.join(['header'] * 17)+'\n'+'\t'.join(fields)+'\n')
            target = root/'ChIP-seq_K562/TEST'; target.mkdir(parents=True)
            (target/'old_ENCFFOLD_peaks.narrowPeak.bed').write_text('old\n')
            # Supply script location explicitly because the test executes via stdin.
            body = body.replace('REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"',
                                'REPO_DIR="."')
            result = subprocess.run([BASH], input='wget() { printf "chr1\\t0\\t10\\n" | gzip -c > "$3"; }\n'+body,
                text=True, capture_output=True, env=dict(os.environ, BASE_DIR=root.as_posix(), SELECTED_TSV=manifest.as_posix()))
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = target/'TEST_K562_ENCSRTEST_ENCFFNEW_GRCh38_rep1.narrowPeak.bed'
            self.assertEqual(expected.read_text(), 'chr1\t0\t10\n')

    @unittest.skipUnless(BASH, 'Bash required')
    def test_idiffir_environment_does_not_leak_to_next_run(self):
        # Execute the first two real archived job blocks with lightweight tool stand-ins.
        body = (ROOT/'outputs/knockdown/run_all_knockdown_irfinder_idiffir.sh').read_text()
        body = body.split('\n)\n', 2)
        first_two = '\n)\n'.join(body[:2]) + '\n)\n'
        prefix = '''IRFinder() { [ "${IDIFFIR_ACTIVE:-no}" = no ] || return 93; }
conda() { export IDIFFIR_ACTIVE=yes; }
source() { :; }
idiffir.py() { :; }
'''
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root/'RBP_knockdown').mkdir()
            work = root/'Project1/iDiffIR'; work.mkdir(parents=True)
            convert = work/'convertBam.sh'; convert.write_text('#!/usr/bin/env bash\nexit 0\n')
            convert.chmod(0o755)
            result = subprocess.run([BASH], input=prefix+first_two, text=True, capture_output=True,
                                    env=dict(os.environ, BASE_DIR=root.as_posix()))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('IRFinder DAZAP1_HepG2', result.stdout)


if __name__ == '__main__':
    unittest.main()
