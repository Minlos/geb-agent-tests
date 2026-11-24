from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
import unittest
import run_qwen_parallel as m
class ParallelBudgetChecks(unittest.TestCase):
    def test_shared_reservation_and_settlement(self):
        budget=m.Budget('0.50')
        def spend(i):
            held=budget.reserve(1000,100);budget.settle(held,'0.0001')
        with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(spend,range(100)))
        self.assertEqual(budget.spent,Decimal('0.0100'))
    def test_completed_profiles_not_repeated(self):
        groups=[('set',None,[{'id':'one'}])]
        jobs=m.pending(groups,{('set','one','original')})
        self.assertEqual(jobs[0][-1],['v3'])
        self.assertFalse(m.pending(groups,{('set','one','original'),('set','one','v3')}))
if __name__=='__main__':unittest.main()
