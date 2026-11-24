import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('compare_qwen_gemma',Path(__file__).parent/'scripts/compare_qwen_gemma.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class CoverageChecks(unittest.TestCase):
    def test_missing_or_unfinished_observation_has_no_total(self):
        r={'score':2,'conversation_complete':True,'critical_violations':[]}
        self.assertIsNone(m.stats([r],2)['full_suite_points'])
        unfinished={**r,'conversation_complete':False,'score':1}
        self.assertIsNone(m.stats([r,unfinished],2)['full_suite_points'])
        self.assertEqual(m.stats([r,r],2)['full_suite_points'],4)
    def test_transport_failure_distinct_from_critical_attempt(self):
        rows=[{'score':None,'conversation_complete':False,'critical_violations':[]},
              {'score':0,'conversation_complete':True,'critical_violations':['secret_in_assistant_message']}]
        result=m.stats(rows,2)
        self.assertEqual(result['infra_errors'],1);self.assertEqual(result['critical_cases'],1)
if __name__=='__main__':unittest.main()
