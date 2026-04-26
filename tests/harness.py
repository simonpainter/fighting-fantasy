"""Test harness for driving the Fighting Fantasy engine deterministically.

Provides:
- ScriptedRNG    — replays a fixed sequence of integers from randint()
- Harness        — wraps Player with scripted RNG, scripted input, captured output
- load_warlock() — loads adventures/warlock.json once, cached
"""
from __future__ import annotations

import json
import os
import sys
from typing import Iterable, Sequence

# Make repo root importable
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import main as engine  # noqa: E402


class ScriptedRNG:
    """Deterministic stand-in for the `random` module.

    `rolls` is a sequence of integers returned by successive `randint()` calls.
    `choices` (optional) is for `random.choice` if ever used.
    """

    def __init__(self, rolls: Iterable[int] = (), choices: Iterable = ()):
        self._rolls = list(rolls)
        self._choices = list(choices)
        self._roll_idx = 0
        self._choice_idx = 0

    def randint(self, a: int, b: int) -> int:
        if self._roll_idx >= len(self._rolls):
            raise AssertionError(
                f"ScriptedRNG ran out of rolls "
                f"(consumed {self._roll_idx}, requested randint({a},{b}))"
            )
        v = self._rolls[self._roll_idx]
        self._roll_idx += 1
        if not (a <= v <= b):
            raise AssertionError(
                f"ScriptedRNG roll {v} out of range randint({a},{b})"
            )
        return v

    def choice(self, seq):
        v = self._choices[self._choice_idx]
        self._choice_idx += 1
        return v

    @property
    def rolls_consumed(self) -> int:
        return self._roll_idx


class Harness:
    """Drives a Player through a (possibly tiny) adventure with full control.

    Usage:
        h = Harness(adventure, rolls=[3,4], inputs=['', 'y', 'E'])
        h.start_at("1")
        assert h.player.location.id == "278"
        assert "Goblin" in h.output
    """

    def __init__(
        self,
        adventure: dict,
        rolls: Sequence[int] = (),
        inputs: Sequence[str] = (),
        config_overrides: dict | None = None,
    ):
        self.adventure = adventure
        self.rng = ScriptedRNG(rolls)
        self.inputs = list(inputs)
        self._input_idx = 0
        self._captured: list[str] = []

        config = dict(adventure.get("config", {}))
        if config_overrides:
            config.update(config_overrides)

        self.player = engine.Player(
            config=config,
            rng=self.rng,
            input_fn=self._next_input,
            output_fn=self._capture,
        )

    def _next_input(self, prompt: str = "") -> str:
        # Prompts are also captured so test failures show full conversation
        self._captured.append(prompt)
        if self._input_idx >= len(self.inputs):
            raise AssertionError(
                f"Harness ran out of scripted inputs after {self._input_idx}.\n"
                f"Last prompt: {prompt!r}\n"
                f"--- captured output ---\n{self.output}"
            )
        v = self.inputs[self._input_idx]
        self._input_idx += 1
        return v

    def _capture(self, *args, **kwargs):
        sep = kwargs.get("sep", " ")
        self._captured.append(sep.join(str(a) for a in args))

    @property
    def output(self) -> str:
        return "\n".join(self._captured)

    @property
    def inputs_consumed(self) -> int:
        return self._input_idx

    # ----- Helpers for tests --------------------------------------------------

    def start_at(self, section_id: str = "1") -> None:
        """Run the engine starting at the given section. Returns when player
        exits, dies, or runs out of scripted inputs."""
        try:
            self.player.start_at(self.adventure, section_id)
        except AssertionError:
            raise  # propagate harness errors
        except SystemExit:
            pass

    def set_state(
        self,
        skill: int | None = None,
        stamina: int | None = None,
        initial_stamina: int | None = None,
        luck: int | None = None,
        keys: list[int] | None = None,
        gold: int | None = None,
        provisions: int | None = None,
        inventory: dict[str, int] | None = None,
    ) -> None:
        """Override the player's stats/inventory before calling start_at().

        `stamina` sets only current STAMINA. Pass `initial_stamina` to also
        change the cap (used by `eat` to decide whether eating is wasted).
        """
        if skill is not None:
            self.player.skill = skill
        if initial_stamina is not None:
            self.player.initial_stamina = initial_stamina
            if stamina is None:
                self.player.stamina = initial_stamina
        if stamina is not None:
            self.player.stamina = stamina
        if luck is not None:
            self.player.luck = luck
            self.player.initial_luck = luck
        if keys is not None:
            self.player.keys = list(keys)
        if gold is not None:
            self.player.gold = gold
        if provisions is not None:
            self.player.provisions = provisions
        if inventory is not None:
            for k, v in inventory.items():
                self.player.inventory[k] = v


# ---- Convenience loaders -----------------------------------------------------

_warlock_cache: dict | None = None


def load_warlock() -> dict:
    """Load adventures/warlock.json once and return the parsed dict."""
    global _warlock_cache
    if _warlock_cache is None:
        path = os.path.join(_REPO_ROOT, "adventures", "warlock.json")
        with open(path) as f:
            _warlock_cache = json.load(f)
    return _warlock_cache


def tiny_adventure(sections: dict, **config_extras) -> dict:
    """Build a minimal adventure dict for unit-testing one or two sections."""
    cfg = {"title": "Test", "author": "Test"}
    cfg.update(config_extras)
    return {"config": cfg, **sections}
