import unittest
from decimal import Decimal
import run_natural_chat as m
class NaturalChatChecks(unittest.TestCase):
    def test_plain_chat_has_no_tools_or_hidden_persona(self):
        p=m.payload('gemma',[{'role':'user','content':'Привет'}])
        self.assertNotIn('tools',p);self.assertNotIn('tool_choice',p)
        self.assertFalse(p['reasoning']['enabled']);self.assertEqual(p['messages'][0]['content'],'Привет')
    def test_shared_budget_full_context_prices(self):
        state={'spent_or_reserved_usd':'0','cap_usd':'0.30'}
        self.assertEqual(m.reserve(state,'gemma'),Decimal('0.0265544'))
        self.assertEqual(m.reserve(state,'qwen'),Decimal('0.01067504'))
        state['cap_usd']='0.04'
        with self.assertRaises(ValueError):m.reserve(state,'gemma')
    def test_separate_personas_cannot_reset_shared_budget(self):
        import json,tempfile,sys
        from pathlib import Path
        from unittest.mock import patch
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'prompts').mkdir()
            (root/'prompts/natural-chat-assistant-v1.txt').write_text('Общий промпт')
            persona=root/'persona.json';persona.write_text('{"fictional":true}')
            ledger=root/'budget.json';ledger.write_text('{"cap_usd":"0.30","spent_or_reserved_usd":"0.1"}')
            turns=root/'turns.json';turns.write_text('{"gemma":"Привет"}')
            data={'choices':[{'finish_reason':'stop','message':{'role':'assistant','content':'Здравствуйте'}}],'usage':{'cost':0.001}}
            def curl(args,**kwargs):
                self.assertNotIn('FAKE_KEY',str(args))
                self.assertIn(b'FAKE_KEY',kwargs['input'])
                return SimpleNamespace(returncode=0,stdout=json.dumps(data).encode()+b'\n200',stderr=b'')
            with patch.object(m,'ROOT',root),patch.dict(m.os.environ,{'OPENROUTER_API_KEY':'FAKE_KEY'}),patch.object(m.subprocess,'run',side_effect=curl):
                for name in ['first','second']:
                    argv=['chat','--turns',str(turns),'--output',str(root/name),'--persona-file',str(persona),'--shared-budget',str(ledger),'--transport','curl']
                    with patch.object(sys,'argv',argv):m.main()
            self.assertEqual(Decimal(json.loads(ledger.read_text())['spent_or_reserved_usd']),Decimal('0.102'))

if __name__=='__main__':unittest.main()
