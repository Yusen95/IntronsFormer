import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'tomtom_to_tf', Path(__file__).resolve().parents[1] / 'scripts/tomtom_to_tf.py')
mapping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mapping)


class TomtomMappingTests(unittest.TestCase):
    def test_aliases_deduplication_and_q_threshold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            meme = root / 'db.meme'
            meme.write_text('MOTIF M1 (TFAP2D)_(Mus_musculus)_(DBD_0.80)\n'
                            'MOTIF M2 TFAP2D\nMOTIF M3 SNAI2\n')
            tomtom = root / 'tomtom.tsv'
            tomtom.write_text('Query_ID\tTarget_ID\tq-value\tQuery_consensus\n'
                              'q1\tM1\t0.04\tACGT\nq2\tM2\t0.01\tAAAA\n'
                              'q3\tM3\t0.06\tACGT\nq4\tmissing\t0.02\tACGT\n'
                              '# trailing comment\n')
            best, missing = mapping.parse_tomtom(tomtom, mapping.load_meme_map(meme), 0.05)
            self.assertEqual(best, {'TFAP2D': 0.01})
            self.assertEqual(missing, {'missing'})
            self.assertEqual(mapping.flag_low_complexity_targets(tomtom), (1, 4))


if __name__ == '__main__':
    unittest.main()
