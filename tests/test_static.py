"""Layer 1 — static validation of adventures/warlock.json.

Catches structural issues without running the engine: missing exit destinations,
unknown mechanic types, undeclared inventory items, malformed mechanic_data, etc.
"""
import unittest

from tests.harness import load_warlock


SUPPORTED_MECHANICS = {
    "test_luck",
    "test_stamina",
    "dice_roll",
    "dice_table",
    "key_sum",
    "item_check",
    "gold_check",
    "pre_combat_luck",
    "test_luck_choice",
    "random_encounter",
    "fight",
    "return",
}


class StaticAdventureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.adv = load_warlock()
        cls.config = cls.adv["config"]
        cls.sections = {k: v for k, v in cls.adv.items() if k != "config"}
        cls.declared_items = set(cls.config.get("inventory", {}).keys())

    def test_400_sections_present(self):
        ids = {int(k) for k in self.sections}
        self.assertEqual(len(self.sections), 400, "Expected 400 sections")
        self.assertEqual(min(ids), 1)
        self.assertEqual(max(ids), 400)
        self.assertEqual(ids, set(range(1, 401)), "Section IDs not contiguous 1..400")

    def test_required_fields_per_section(self):
        for sid, body in self.sections.items():
            with self.subTest(section=sid):
                self.assertIn("description", body)
                self.assertIn("exits", body)
                self.assertIn("monsters", body)
                self.assertIsInstance(body["exits"], dict)
                self.assertIsInstance(body["monsters"], list)

    def test_all_exit_destinations_exist(self):
        for sid, body in self.sections.items():
            for action, dest in body["exits"].items():
                with self.subTest(section=sid, action=action):
                    if dest == "" or dest is None:
                        # Empty destination is the documented death sentinel
                        # — engine kills the player and ends the game.
                        continue
                    self.assertIn(
                        str(dest),
                        self.sections,
                        f"§{sid} exit '{action}' → {dest} does not exist",
                    )

    def test_all_mechanics_are_supported(self):
        for sid, body in self.sections.items():
            mech = body.get("mechanic")
            if mech is None:
                continue
            with self.subTest(section=sid, mechanic=mech):
                self.assertIn(mech, SUPPORTED_MECHANICS)

    def test_test_mechanics_have_lucky_unlucky_exits(self):
        # test_luck_choice is special: only `lucky` is required; the unlucky
        # branch presents the remaining exits as a free choice.
        needs = {"test_luck", "test_stamina", "dice_roll"}
        for sid, body in self.sections.items():
            if body.get("mechanic") in needs:
                with self.subTest(section=sid):
                    self.assertIn("lucky", body["exits"])
                    self.assertIn("unlucky", body["exits"])
            if body.get("mechanic") == "test_luck_choice":
                with self.subTest(section=sid):
                    self.assertIn("lucky", body["exits"])
                    self.assertGreaterEqual(
                        len(body["exits"]), 2,
                        "test_luck_choice needs `lucky` plus at least one free-choice exit",
                    )

    def test_check_mechanics_have_have_missing_exits(self):
        for sid, body in self.sections.items():
            if body.get("mechanic") in {"item_check", "gold_check"}:
                with self.subTest(section=sid):
                    self.assertIn("have", body["exits"])
                    self.assertIn("missing", body["exits"])

    def test_dice_table_well_formed(self):
        for sid, body in self.sections.items():
            if body.get("mechanic") != "dice_table":
                continue
            with self.subTest(section=sid):
                data = body.get("mechanic_data", {})
                self.assertIn("table", data)
                for row in data["table"]:
                    self.assertIn("rolls", row)
                    self.assertIn("destination", row)
                    self.assertIn(str(row["destination"]), self.sections)

    def test_grants_item_declared_in_config(self):
        for sid, body in self.sections.items():
            grants = body.get("grants_item")
            if not grants:
                continue
            items = grants if isinstance(grants, list) else [grants]
            for it in items:
                with self.subTest(section=sid, item=it):
                    self.assertIn(it, self.declared_items,
                                  f"§{sid} grants undeclared item '{it}'")

    def test_consumes_item_declared_in_config(self):
        for sid, body in self.sections.items():
            consumes = body.get("consumes_item")
            if not consumes:
                continue
            items = consumes if isinstance(consumes, list) else [consumes]
            for it in items:
                with self.subTest(section=sid, item=it):
                    self.assertIn(it, self.declared_items)

    def test_item_check_references_declared_item(self):
        for sid, body in self.sections.items():
            if body.get("mechanic") != "item_check":
                continue
            item = body.get("mechanic_data", {}).get("item")
            with self.subTest(section=sid):
                self.assertIn(item, self.declared_items)

    def test_no_unsupported_top_level_keys(self):
        allowed = {
            "description", "exits", "monsters",
            "mechanic", "mechanic_data",
            "on_entry_effects",
            "grants_key", "grants_item", "grants_gold", "grants_provisions",
            "consumes_item",
        }
        for sid, body in self.sections.items():
            for key in body:
                with self.subTest(section=sid, key=key):
                    self.assertIn(key, allowed)


if __name__ == "__main__":
    unittest.main()
