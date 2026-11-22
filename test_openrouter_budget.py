import importlib
import importlib.util
import unittest
from decimal import Decimal


class BudgetTests(unittest.TestCase):
    def module(self):
        self.assertIsNotNone(importlib.util.find_spec('openrouter_budget'))
        return importlib.import_module('openrouter_budget')

    def test_reservation_uses_entire_context_at_enforced_price_ceiling(self):
        m = self.module(); budget = m.Budget('1', '0.02')
        amount = budget.reserve(1024000, 1024)
        self.assertEqual(amount, Decimal('0.514048'))
        self.assertEqual(budget.spent, Decimal('0.534048'))

    def test_insufficient_budget_stops_before_network_request(self):
        m = self.module(); budget = m.Budget('0.1')
        with self.assertRaises(m.APIError):
            budget.reserve(262144, 1024)
        self.assertEqual(budget.spent, 0)

    def test_known_usage_releases_unused_reservation(self):
        m = self.module(); budget = m.Budget('1')
        held = budget.reserve(262144, 1024)
        budget.settle(held, '0.001')
        self.assertEqual(budget.spent, Decimal('0.001'))

    def test_unknown_usage_retains_reservation(self):
        m = self.module(); budget = m.Budget('1')
        held = budget.reserve(262144, 1024)
        budget.settle(held, None)
        self.assertEqual(budget.spent, held)

    def test_cost_above_bound_does_not_free_reserved_money(self):
        m = self.module(); budget = m.Budget('1')
        held = budget.reserve(262144, 1024)
        with self.assertRaises(m.APIError):
            budget.settle(held, '2')
        self.assertEqual(budget.spent, held)

    def test_invalid_token_bounds_cannot_reduce_recorded_spend(self):
        m = self.module()
        for context, output in [(-1000000, 1024), (0, 1024), (262144, -1), (True, 1), (1, 0)]:
            budget = m.Budget('1')
            with self.subTest(context=context, output=output), self.assertRaises(ValueError):
                budget.reserve(context, output)
            self.assertEqual(budget.spent, 0)

    def test_supplemental_selection_does_not_rerun_other_scenarios(self):
        import run_openrouter_unified as driver
        self.assertEqual([c['id'] for c in driver.select_cases('T01')], ['T01'])
        with self.assertRaises(ValueError):
            driver.select_cases('T99')
