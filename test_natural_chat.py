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
if __name__=='__main__':unittest.main()
