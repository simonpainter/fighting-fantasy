"""Layer 2 — exercise every supported mechanic with deterministic RNG.

Each test builds a tiny in-memory adventure that fires a single mechanic,
then asserts the engine routes correctly for both branches.
"""
import unittest

from tests.harness import Harness, tiny_adventure


def two_room(extra: dict) -> dict:
    """Section 1 with the supplied mechanic; lucky→2, unlucky→3 by default."""
    base = {
        "1": {"description": "test", "exits": {"lucky": "2", "unlucky": "3"}, "monsters": []},
        "2": {"description": "lucky end", "exits": {}, "monsters": []},
        "3": {"description": "unlucky end", "exits": {}, "monsters": []},
    }
    base["1"].update(extra)
    return tiny_adventure(base)


class TestLuckMechanic(unittest.TestCase):
    """test_luck: 2d6 ≤ LUCK passes; LUCK decrements each test."""

    def _adv(self):
        return two_room({"mechanic": "test_luck"})

    def test_lucky_branch(self):
        # 4 rolls for char creation, 2 for the luck test
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 1, 1], inputs=[""])
        h.set_state(luck=12)
        h.start_at("1")
        self.assertEqual(h.player.location.id, "2")
        self.assertEqual(h.player.luck, 11)  # luck decremented

    def test_unlucky_branch(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 6, 6], inputs=[""])
        h.set_state(luck=8)
        h.start_at("1")
        self.assertEqual(h.player.location.id, "3")


class TestStaminaMechanic(unittest.TestCase):
    def _adv(self):
        return two_room({"mechanic": "test_stamina", "mechanic_data": {"dice": 2}})

    def test_passes_stamina(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 1, 2], inputs=[""])
        h.set_state(stamina=20)
        h.start_at("1")
        self.assertEqual(h.player.location.id, "2")

    def test_fails_stamina(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 6, 6], inputs=[""])
        h.set_state(stamina=10)
        h.start_at("1")
        self.assertEqual(h.player.location.id, "3")


class DiceRollMechanic(unittest.TestCase):
    def _adv(self):
        return two_room({
            "mechanic": "dice_roll",
            "mechanic_data": {"dice": 1, "fail_values": [6]},
        })

    def test_safe_roll(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 4], inputs=[""])
        h.start_at("1")
        self.assertEqual(h.player.location.id, "2")

    def test_fail_value(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 6], inputs=[""])
        h.start_at("1")
        self.assertEqual(h.player.location.id, "3")


class DiceTableMechanic(unittest.TestCase):
    def _adv(self):
        return tiny_adventure({
            "1": {
                "description": "roll table",
                "mechanic": "dice_table",
                "mechanic_data": {
                    "dice": 1,
                    "table": [
                        {"rolls": [1, 2], "destination": "10", "effects": {"stamina": -2}},
                        {"rolls": [3, 4, 5, 6], "destination": "11"},
                    ],
                },
                "exits": {},
                "monsters": [],
            },
            "10": {"description": "low end", "exits": {}, "monsters": []},
            "11": {"description": "high end", "exits": {}, "monsters": []},
        })

    def test_low_roll_applies_effects(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 1], inputs=[""])
        h.set_state(stamina=20)
        h.start_at("1")
        self.assertEqual(h.player.location.id, "10")
        self.assertEqual(h.player.stamina, 18)

    def test_high_roll(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3, 5], inputs=[""])
        h.start_at("1")
        self.assertEqual(h.player.location.id, "11")


class KeySumMechanic(unittest.TestCase):
    def _adv(self):
        return tiny_adventure({
            "1": {
                "description": "lock",
                "mechanic": "key_sum",
                "exits": {},
                "monsters": [],
            },
            "300": {"description": "open", "exits": {}, "monsters": []},
        })

    def test_three_keys_sum_routes(self):
        # 100 + 100 + 100 = 300
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=[])
        h.set_state(keys=[100, 100, 100])
        h.start_at("1")
        self.assertEqual(h.player.location.id, "300")

    def test_too_few_keys_ends_quest(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=[])
        h.set_state(keys=[100, 100])
        h.start_at("1")
        # Game ended without reaching 300
        self.assertNotEqual(h.player.location.id, "300")


class ItemCheckMechanic(unittest.TestCase):
    def _adv(self):
        return tiny_adventure({
            "1": {
                "description": "vampire room",
                "mechanic": "item_check",
                "mechanic_data": {"item": "wooden_stake", "consume": True},
                "exits": {"have": "10", "missing": "11"},
                "monsters": [],
            },
            "10": {"description": "stake him", "exits": {}, "monsters": []},
            "11": {"description": "die", "exits": {}, "monsters": []},
        }, inventory={"wooden_stake": 0})

    def test_with_item_consumes_and_routes(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=[])
        h.set_state(inventory={"wooden_stake": 1})
        h.start_at("1")
        self.assertEqual(h.player.location.id, "10")
        self.assertEqual(h.player.inventory["wooden_stake"], 0)  # consumed

    def test_without_item(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=[])
        h.start_at("1")
        self.assertEqual(h.player.location.id, "11")


class GoldCheckMechanic(unittest.TestCase):
    def _adv(self):
        return tiny_adventure({
            "1": {
                "description": "ferryman wants 3 gp",
                "mechanic": "gold_check",
                "mechanic_data": {"amount": 3, "consume": True},
                "exits": {"have": "10", "missing": "11"},
                "monsters": [],
            },
            "10": {"description": "ride", "exits": {}, "monsters": []},
            "11": {"description": "stuck", "exits": {}, "monsters": []},
        }, starting_gold=0)

    def test_enough_gold_consumes(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=[], config_overrides={"starting_gold": 5})
        h.start_at("1")
        self.assertEqual(h.player.location.id, "10")
        self.assertEqual(h.player.gold, 2)

    def test_not_enough_gold(self):
        h = Harness(self._adv(), rolls=[3, 3, 3, 3], inputs=[])
        h.start_at("1")
        self.assertEqual(h.player.location.id, "11")
        self.assertEqual(h.player.gold, 0)


class FightMechanic(unittest.TestCase):
    """Combat with deterministic rolls. SKILL 12 vs SKILL 5 should win."""

    def _adv(self):
        return tiny_adventure({
            "1": {
                "description": "fight",
                "exits": {"continue": "2"},
                "monsters": [{"name": "Rat", "skill": 5, "stamina": 4}],
            },
            "2": {"description": "victory", "exits": {}, "monsters": []},
        })

    def test_player_wins(self):
        # char-creation: 4. Combat: press enter to fight. Then per round:
        #   2 rolls (player), 2 rolls (monster), 'n' to skip luck on hit.
        # 4 damage to monster (stamina 4) needs 2 rounds of 2 damage.
        h = Harness(
            self._adv(),
            rolls=[3, 3, 3, 3,
                   6, 6, 1, 1,   # round 1: player 12+12=24 vs monster 2+5=7 → hit
                   6, 6, 1, 1],  # round 2: same
            inputs=["", "n", "n", "continue"],
        )
        h.start_at("1")
        self.assertEqual(h.player.location.id, "2")
        self.assertGreater(h.player.stamina, 0)


class FatalEmptyExit(unittest.TestCase):
    """Empty-string destination should kill the player gracefully (e.g. §379)."""

    def test_empty_unlucky_kills(self):
        adv = tiny_adventure({
            "1": {
                "description": "lightning box",
                "mechanic": "test_luck",
                "exits": {"lucky": "2", "unlucky": ""},
                "monsters": [],
            },
            "2": {"description": "survive", "exits": {}, "monsters": []},
        })
        h = Harness(adv, rolls=[3, 3, 3, 3, 6, 6], inputs=[""])
        h.set_state(luck=8)
        h.start_at("1")
        self.assertEqual(h.player.stamina, 0)


if __name__ == "__main__":
    unittest.main()
