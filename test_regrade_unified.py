import copy
import hashlib
import unittest

from pathlib import Path
import run_unified as runner
from unified_cases import CASES
from regrade_unified import combine


class RegradeIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows = [runner.run_case(c, runner.ReferenceClient(c)) for c in runner.expanded_cases(CASES)]
        cls.primary = {'metadata': {'model': 'REFERENCE_ONLY', 'source_sha256': {
            'unified_environment.py': hashlib.sha256(Path('unified_environment.py').read_bytes()).hexdigest()}}, 'results': rows}
        cls.supplement = copy.deepcopy(cls.primary)
        cls.supplement['results'] = [r for r in cls.supplement['results'] if r['id'] == 'T01']

    def test_original_records_remain_unchanged(self):
        before = copy.deepcopy(self.primary)
        reviewed = combine(self.primary, self.supplement)
        self.assertEqual(self.primary, before)
        self.assertEqual(reviewed['summary']['full_suite_points'], 72)

    def test_model_identity_mismatch_rejected(self):
        data = copy.deepcopy(self.supplement); data['metadata']['model'] = 'OTHER'
        with self.assertRaises(ValueError):
            combine(self.primary, data)

    def test_changed_prompt_outside_declared_replacement_rejected(self):
        data = copy.deepcopy(self.primary)
        next(r for r in data['results'] if r['id'] == 'T02')['turns'][0]['user'] = 'Different task'
        with self.assertRaises(ValueError):
            combine(data, self.supplement)

    def test_critical_violation_survives_offline_regrade(self):
        data = copy.deepcopy(self.primary)
        row = next(r for r in data['results'] if r['id'] == 'T25')
        row['violations'] = ['secret_in_assistant_message']
        reviewed = combine(data, self.supplement)
        self.assertEqual(next(r for r in reviewed['results'] if r['id'] == 'T25')['score'], 0)
