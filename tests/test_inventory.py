"""Layer 3 — inventory, gold, provisions, side-commands, grant/consume flows."""
import unittest

from tests.harness import Harness, tiny_adventure


class GrantsAndState(unittest.TestCase):
    def test_starting_gold_and_provisions_loaded(self):
        adv = tiny_adventure({
            "1": {"description": "x", "exits": {"continue": "2"}, "monsters": []},
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, starting_gold=7, starting_provisions=4)
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["continue"])
        h.start_at("1")
        self.assertEqual(h.player.gold, 7)
        self.assertEqual(h.player.provisions, 4)

    def test_grants_gold_and_provisions_accumulate(self):
        adv = tiny_adventure({
            "1": {
                "description": "treasure",
                "grants_gold": 10,
                "grants_provisions": 3,
                "exits": {"continue": "2"},
                "monsters": [],
            },
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, starting_gold=5)
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["continue"])
        h.start_at("1")
        self.assertEqual(h.player.gold, 15)
        self.assertEqual(h.player.provisions, 3)

    def test_grants_item_accept(self):
        adv = tiny_adventure({
            "1": {
                "description": "stake on floor",
                "grants_item": "wooden_stake",
                "exits": {"continue": "2"},
                "monsters": [],
            },
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, inventory={"wooden_stake": 0})
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["y", "continue"])
        h.start_at("1")
        self.assertEqual(h.player.inventory["wooden_stake"], 1)

    def test_grants_item_decline(self):
        adv = tiny_adventure({
            "1": {
                "description": "stake on floor",
                "grants_item": "wooden_stake",
                "exits": {"continue": "2"},
                "monsters": [],
            },
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, inventory={"wooden_stake": 0})
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["n", "continue"])
        h.start_at("1")
        self.assertEqual(h.player.inventory["wooden_stake"], 0)

    def test_grants_item_list(self):
        adv = tiny_adventure({
            "1": {
                "description": "two items",
                "grants_item": ["garlic", "crucifix"],
                "exits": {"continue": "2"},
                "monsters": [],
            },
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, inventory={"garlic": 0, "crucifix": 0})
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["y", "y", "continue"])
        h.start_at("1")
        self.assertEqual(h.player.inventory["garlic"], 1)
        self.assertEqual(h.player.inventory["crucifix"], 1)

    def test_consumes_item_decrements(self):
        adv = tiny_adventure({
            "1": {
                "description": "use potion on Warlock",
                "consumes_item": "potion_of_invisibility",
                "exits": {"continue": "2"},
                "monsters": [],
            },
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, inventory={"potion_of_invisibility": 0})
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["continue"])
        h.set_state(inventory={"potion_of_invisibility": 1})
        h.start_at("1")
        self.assertEqual(h.player.inventory["potion_of_invisibility"], 0)


class SideCommands(unittest.TestCase):
    """`inv` and `eat` should not re-trigger entry effects of the section."""

    def _adv(self):
        return tiny_adventure({
            "1": {
                "description": "treasure room",
                "grants_gold": 5,
                "exits": {"continue": "2"},
                "monsters": [],
            },
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, starting_gold=0)

    def test_inv_does_not_regrant_gold(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=["inv", "continue"])
        h.start_at("1")
        self.assertEqual(h.player.gold, 5, "Gold should not double-grant after `inv`")

    def test_eat_does_not_regrant(self):
        adv = self._adv()
        adv["config"]["starting_provisions"] = 2
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["eat", "continue"])
        h.set_state(stamina=10)  # below initial so eat actually fires
        h.start_at("1")
        self.assertEqual(h.player.gold, 5)
        self.assertEqual(h.player.provisions, 1, "Provisions consumed by eat")

    def test_invalid_direction_does_not_regrant(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=["nonsense", "continue"])
        h.start_at("1")
        self.assertEqual(h.player.gold, 5)


class EatProvisions(unittest.TestCase):
    def _adv(self):
        return tiny_adventure({
            "1": {"description": "rest", "exits": {"continue": "2"}, "monsters": []},
            "2": {"description": "end", "exits": {}, "monsters": []},
        }, starting_provisions=3)

    def test_eat_restores_stamina(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=["eat", "continue"])
        h.set_state(stamina=10)  # initial_stamina was set by constructor to 18
        h.start_at("1")
        self.assertEqual(h.player.stamina, 14)  # +4
        self.assertEqual(h.player.provisions, 2)

    def test_eat_caps_at_initial_stamina(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=["eat", "continue"])
        # initial_stamina is 3+3+12=18, set stamina to 16 so +4 would overshoot
        h.set_state(stamina=16)
        h.start_at("1")
        self.assertEqual(h.player.stamina, 18)  # capped
        self.assertEqual(h.player.provisions, 2)

    def test_eat_at_full_stamina_no_consume(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=["eat", "continue"])
        # Don't override stamina — it's already at initial
        h.start_at("1")
        self.assertEqual(h.player.provisions, 3, "Should refuse to consume at full STAMINA")

    def test_eat_with_no_provisions(self):
        adv = self._adv()
        adv["config"]["starting_provisions"] = 0
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["eat", "continue"])
        h.set_state(stamina=10)
        h.start_at("1")
        self.assertEqual(h.player.stamina, 10)


if __name__ == "__main__":
    unittest.main()
