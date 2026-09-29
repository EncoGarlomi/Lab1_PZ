import unittest

from main import CoffeeMachine


class CoffeeMachineTests(unittest.TestCase):
    def test_cocoa_uses_cacao_beans_only(self):
        machine = CoffeeMachine()
        coffee_before = machine.coffee_beans
        cacao_before = machine.cacao_beans

        success, _, _ = machine.buy("Какао", "card")

        self.assertTrue(success)
        self.assertEqual(machine.coffee_beans, coffee_before)
        self.assertEqual(machine.cacao_beans, cacao_before - 10)

    def test_cash_purchase_returns_change(self):
        machine = CoffeeMachine()

        success, _, change = machine.buy(
            "Еспресо",
            "cash",
            paid=5000,
            paid_bills={5000: 1},
        )

        self.assertTrue(success)
        self.assertEqual(change, 1000)
        self.assertEqual(machine.money, 4000)

    def test_refill_does_not_exceed_capacity(self):
        machine = CoffeeMachine()

        added = machine.fill(1000, 1000, 1000, 10, 1000, 1000, {}, {})

        self.assertEqual(added["water"], 0)
        self.assertEqual(added["cacao_beans"], 0)
        self.assertEqual(machine.cups, machine.MAX_CAPACITY["cups"])

    def test_take_clears_revenue(self):
        machine = CoffeeMachine()
        machine.buy("Еспресо", "card")

        collected = machine.take()

        self.assertEqual(collected, 4000)
        self.assertEqual(machine.money, 0)
        self.assertEqual(machine.money_nal, 0)
        self.assertEqual(machine.money_beznal, 0)

    def test_card_payment_records_revenue_without_change(self):
        machine = CoffeeMachine()

        success, _, change = machine.buy("Какао", "card")

        self.assertTrue(success)
        self.assertEqual(change, 0)
        self.assertEqual(machine.money_beznal, 5500)


if __name__ == "__main__":
    unittest.main()
