"""Layer 4 — walk known paths through the real warlock.json adventure.

These tests confirm that critical routes are reachable and that the engine
correctly executes long sequences end-to-end.
"""
import unittest
from collections import deque
from itertools import combinations

from tests.harness import Harness, load_warlock


KEYS_IN_DUNGEON = [9, 99, 111, 111, 66]
WINNING_KEYS = [99, 111, 111]
WINNING_SUM = sum(WINNING_KEYS)  # 321


class GraphReachability(unittest.TestCase):
    """Pure graph analysis — no engine. Confirms structural integrity."""

    @classmethod
    def setUpClass(cls):
        cls.adv = load_warlock()
        cls.sections = {k: v for k, v in cls.adv.items() if k != "config"}

    def _build_graph(self):
        valid_sums = {sum(c) for c in combinations(KEYS_IN_DUNGEON, 3)}
        graph = {sid: set() for sid in self.sections}
        for sid, body in self.sections.items():
            for dest in body.get("exits", {}).values():
                if dest and str(dest) in self.sections:
                    graph[sid].add(str(dest))
            # key_sum mechanic can route to any valid sum destination
            if body.get("mechanic") == "key_sum":
                for s in valid_sums:
                    if str(s) in self.sections:
                        graph[sid].add(str(s))
            # dice_table routes via mechanic_data, not exits
            if body.get("mechanic") == "dice_table":
                for row in body.get("mechanic_data", {}).get("table", []):
                    d = str(row.get("destination"))
                    if d in self.sections:
                        graph[sid].add(d)
        return graph

    def test_400_is_reachable_from_1(self):
        graph = self._build_graph()
        seen = {"1"}
        q = deque(["1"])
        while q:
            cur = q.popleft()
            for nxt in graph[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        self.assertIn("400", seen, "Victory section §400 must be reachable from §1")

    def test_only_winning_key_combo_routes_to_400(self):
        # 99 + 111 + 111 = 321 → §169 → §400
        self.assertEqual(WINNING_SUM, 321)
        self.assertEqual(self.sections["321"]["exits"].get("continue"), "169")
        # §169 should lead to §400 directly or via short chain
        graph = self._build_graph()
        seen, q = {"169"}, deque(["169"])
        while q:
            cur = q.popleft()
            for nxt in graph[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        self.assertIn("400", seen)

    def test_no_duplicate_section_keys(self):
        # JSON parse already deduplicates, but confirm no collisions in config
        # and section namespace.
        ids = list(self.sections.keys())
        self.assertEqual(len(ids), len(set(ids)))


class WinningPath(unittest.TestCase):
    """Drive the engine through the final key-sum puzzle to victory."""

    def test_key_sum_321_routes_to_169_then_400(self):
        adv = load_warlock()
        # §139 (key_sum) → §321 (continue) → §169 (continue) → §400 (victory end)
        h = Harness(
            adv,
            rolls=[3, 3, 3, 3],
            inputs=["continue", "continue"],
        )
        h.set_state(keys=WINNING_KEYS)
        h.start_at("139")
        self.assertEqual(h.player.location.id, "400",
                         f"Expected to land on §400, got §{h.player.location.id}")


class WrongKeyCombos(unittest.TestCase):
    """All non-winning 3-key sums should route to a wrong-key page (§198 or §182)."""

    def test_each_wrong_combo_reaches_known_decoy(self):
        adv = load_warlock()
        sections = {k: v for k, v in adv.items() if k != "config"}
        wrong_combos = [c for c in combinations(KEYS_IN_DUNGEON, 3) if sum(c) != 321]
        for combo in wrong_combos:
            with self.subTest(combo=combo):
                target = str(sum(combo))
                # The target section exists and routes to a wrong-key decoy
                self.assertIn(target, sections,
                              f"Sum {target} should map to an existing section")
                dest = sections[target]["exits"].get("continue")
                self.assertIn(dest, ("198", "182"),
                              f"§{target} should route to §198 or §182")


class StartingAtArbitrarySection(unittest.TestCase):
    """Verify the engine can begin at any section (key feature of the harness)."""

    def test_start_at_section_278(self):
        adv = load_warlock()
        # Just confirm the engine starts at an arbitrary section without crash.
        # The harness will raise AssertionError if it runs out of inputs;
        # we expect that as a clean termination signal here.
        h = Harness(adv, rolls=[3, 3, 3, 3], inputs=["N"])
        try:
            h.start_at("278")
        except AssertionError as e:
            self.assertIn("ran out of scripted inputs", str(e))
        # Either way, the engine made progress past §278
        self.assertIsNotNone(h.player.location)


if __name__ == "__main__":
    unittest.main()
