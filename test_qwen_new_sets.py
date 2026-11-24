import unittest
from decimal import Decimal
import run_qwen_new_sets as m
from run_tests import APIError

class QwenExperimentChecks(unittest.TestCase):
    def test_sets_are_frozen_and_invalid_case_excluded(self):
        sets=m.datasets()
        self.assertEqual([len(cases) for name,module,cases in sets],[12,23,32])
        self.assertNotIn('SEC-04B',[c['id'] for c in sets[1][2]])

    def test_budget_reserves_full_context_at_enforced_prices(self):
        budget=m.Budget('0.50');held=budget.reserve(262144,1024)
        self.assertEqual(held,Decimal('0.01071104'))
        budget.settle(held,'0.001');self.assertEqual(budget.spent,Decimal('0.001'))
        with self.assertRaises(APIError):m.Budget('0.001').reserve(262144,1024)

    def test_incomplete_or_transport_failure_cannot_be_full_pass(self):
        r={'status':'harness_error','error':'Transport/JSON error; no automatic retry; reservation retained','turns':[],'score':2,'critical_violations':[]}
        m.normalize_record(r,{'user_turns':['task']})
        self.assertFalse(r['conversation_complete']);self.assertIsNone(r['score']);self.assertFalse(r['full_pass'])

if __name__=='__main__':unittest.main()
