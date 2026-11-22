from decimal import Decimal
import unittest
from run_grok_security_continue import PinnedPriceBudget,PRICE_PROMPT,PRICE_COMPLETION
from run_tests import APIError

class SecurityBudgetChecks(unittest.TestCase):
    def test_old_reservation_is_kept_with_tighter_request_bound(self):
        b=PinnedPriceBudget('0.30','0.13443362')
        held=b.reserve(262144,1024)
        self.assertEqual(held,Decimal('0.02656256'))
        b.settle(held,'0.001')
        self.assertEqual(b.spent,Decimal('0.13543362'))

    def test_uncertain_cost_keeps_hold_and_limit_stops_before_next_request(self):
        b=PinnedPriceBudget('0.03')
        held=b.reserve(262144,1024);b.settle(held,None)
        with self.assertRaises(APIError):b.reserve(262144,1024)
        self.assertEqual(b.spent,held)

if __name__=='__main__':unittest.main()
