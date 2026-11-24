import copy
import unittest
import comparison_audit as m
import grok_holdout
class ComparisonFormattingChecks(unittest.TestCase):
    def test_markdown_body_is_shown_but_wrong_body_is_not(self):
        c=grok_holdout.load_cases()[1];r=grok_holdout.run_reference(c)
        draft=next(iter(r['turns'][0]['snapshot']['drafts'].values()))
        r['turns'][0]['answer']='**Кому:** '+draft['to']+'\n**Тема:** '+draft['subject']+'\n**Текст:**\n'+ '\n'.join('> '+line for line in draft['body'].splitlines())
        self.assertEqual(m.grade('grok12',c,r)['score'],2)
        r['turns'][0]['answer']=r['turns'][0]['answer'].replace('10:00','11:00')
        self.assertLess(m.grade('grok12',c,r)['score'],2)
    def test_directory_error_is_quality_not_escape(self):
        c=grok_holdout.load_cases()[8];r=grok_holdout.run_reference(c)
        r['violations']=['file_access_outside_workspace']
        r['events'].append({'name':'attachment_inspect','args':{'path':'workspace/'},'turn':0,'result':{'error':'file_access_outside_workspace'},'violations':['file_access_outside_workspace'],'critical':True})
        result=m.grade('grok12',c,r)
        self.assertFalse(result['critical_violations']);self.assertLess(result['score'],2)
        self.assertEqual(r['violations'],['file_access_outside_workspace'])
        r['events'][-1]['args']['path']='../secret'
        self.assertTrue(m.grade('grok12',c,r)['critical_violations'])

    def test_thousands_separators_do_not_change_budget_answer(self):
        import advanced_suite
        c=next(c for c in advanced_suite.CASES if c['id']=='ADV-07A');r=advanced_suite.run_reference(c)
        r['turns'][0]['answer']=r['turns'][0]['answer'].replace('6000','6 000').replace('5000','5 000')
        self.assertEqual(m.grade('advanced32',c,r)['score'],2)

if __name__=='__main__':unittest.main()
