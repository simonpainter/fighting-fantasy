# Fighting Fantasy

A Python engine for running text-based adventure games in the style of the classic [Fighting Fantasy](https://en.wikipedia.org/wiki/Fighting_Fantasy) gamebook series, created by Steve Jackson and Ian Livingstone.

## Overview

Fighting Fantasy gamebooks are single-player role-playing adventures first published in 1982. Each book is divided into numbered sections; the reader makes choices that jump between sections, resolving combat and challenges with two six-sided dice and three character attributes: **SKILL**, **STAMINA**, and **LUCK**.

This project provides a Python game engine that faithfully recreates that experience in the terminal — branching narrative, dice-based combat, luck tests, and all.

## Features

- **Branching narrative engine** — section-based story graph where player choices drive progression
- **Character creation** — roll SKILL, STAMINA, and LUCK at the start of each adventure
- **Turn-based combat** — faithful implementation of the Fighting Fantasy combat rules
- **Luck tests** — Test your Luck to modify combat outcomes, at the cost of your LUCK score
- **Multiple mechanics** — luck tests, stamina tests, dice-roll challenges, item/gold checks, random encounters, and more
- **Inventory system** — gold, provisions, items, and numbered keys; eat to restore STAMINA mid-adventure
- **Adventure data format** — define adventures in JSON; no code changes needed

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
git clone https://github.com/simonpainter/fighting-fantasy.git
cd fighting-fantasy
```

No additional dependencies — the engine uses the Python standard library only.

### Running

```bash
python3 main.py adventures/your_adventure.json
```

### Running the test suite

The repository ships with a comprehensive unittest suite covering static
validation of adventure files, every mechanic, the inventory system, and
known winning paths through `adventures/warlock.json`:

```bash
python3 -m unittest discover tests -v
```

All tests use the standard library only and run in well under a second.

## How to Play

### Character Attributes

At the start of an adventure your character's attributes are rolled randomly:

| Attribute | Roll | Range | Description |
|-----------|------|-------|-------------|
| **SKILL** | 1d6 + 6 | 7–12 | Combat prowess and dexterity |
| **STAMINA** | 2d6 + 12 | 14–24 | Health — reach 0 and you die |
| **LUCK** | 1d6 + 6 | 7–12 | Fortune — decreases each time you test it |

### Navigation

At each location you are shown the available exits and prompted to choose a direction. Exits can be cardinal directions (`N`, `S`, `E`, `W`) or descriptive words (`charge`, `back`, `search`, etc.). Input is case-insensitive.

At any exit prompt you can also type:

- `inv` (or `i`, `inventory`) — show your gold, provisions, items, and keys
- `eat` (or `e`) — eat a Provision to restore STAMINA (see [Inventory & Provisions](#inventory--provisions))

### Combat

When a monster is present you must fight before you can move on. Each combat round:

1. Both you and the monster roll **2d6** and add your respective **SKILL** scores to get an **Attack Strength**
2. The higher Attack Strength wins the round and deals **2 STAMINA** damage to the loser
3. A tie means both attacks are deflected — no damage is dealt
4. After each hit you may **Test your Luck** to modify the damage (see below)
5. Combat continues until either side reaches 0 STAMINA

**Testing your Luck in combat:**
- If *you* land a hit: Lucky → deal **4 damage** instead of 2; Unlucky → deal only **1 damage**
- If *you* are hit: Lucky → take only **1 damage** instead of 2; Unlucky → take **3 damage**

### Testing Your Luck

Roll **2d6**. If the result is ≤ your current LUCK score you are **Lucky**. Your LUCK decreases by 1 regardless of the outcome — the more you rely on luck, the riskier it becomes.

### Other Mechanics

Some locations trigger automatic checks rather than a player choice:

| Mechanic | How it works |
|----------|-------------|
| `test_luck` | Roll 2d6 against your LUCK score. LUCK decreases by 1. |
| `test_stamina` | Roll 2d6 against your STAMINA score. STAMINA is unaffected. |
| `dice_roll` | Roll a specified number of dice; certain values cause failure. |
| `pre_combat_luck` | Test Luck before a fight; lucky/unlucky effects are applied to your stats. |
| `test_luck_choice` | Lucky takes a fixed exit; unlucky forces you to pick from the remaining exits. |
| `dice_table` | Roll dice and look up the destination (and any effects) in a table. |
| `random_encounter` | Roll a die against a monster table to see what (if anything) appears. |
| `fight` / `return` | Detour into a sub-section to fight, then return to where you came from. |
| `key_sum` | Sum the numbers on three keys you've collected to determine the next section. |
| `item_check` | Branch based on whether you hold a named item (optionally consuming it). |
| `gold_check` | Branch based on whether you have enough Gold Pieces (optionally spending them). |

See [Mechanic exits](#mechanic-exits) for the JSON schema for each mechanic.

---

## Inventory & Provisions

Beyond SKILL/STAMINA/LUCK, your character carries:

- **Gold Pieces** — accumulated via `grants_gold` locations or starting gold; spent via `gold_check` mechanics
- **Provisions** — meals you can eat at any exit prompt to restore STAMINA
- **Items** — named objects (e.g. `silver_key`, `lantern`) granted by locations and checked by `item_check` mechanics
- **Keys** — numbered keys used by the `key_sum` mechanic

### Eating Provisions

At any exit prompt, type `eat` to consume one Provision. This restores up to **4 STAMINA**, capped at your initial STAMINA score. You cannot eat if you are already at full STAMINA or have no Provisions left.

### Starting equipment

Set starting values in the adventure's `config` block (see below).

---

## Adventure Data Format

Adventures are defined in JSON files. Copy `adventures/game_data.json.example` as a starting point.

### Top-level structure

```json
{
    "config": { ... },
    "1": { ... },
    "2": { ... }
}
```

### `config` block

```json
"config": {
    "title": "The Cave of Shadows",
    "author": "Your Name",
    "description": "Short blurb shown at startup.",
    "background": "Longer backstory shown before character creation.",
    "starting_gold": 10,
    "starting_provisions": 5,
    "inventory": {
        "lantern": 1,
        "rope": 1
    }
}
```

| Field | Type | Purpose |
|-------|------|---------|
| `title` | string | Adventure name shown at startup |
| `author` | string | Author credit |
| `description` | string | Short blurb shown at startup |
| `background` | string | Longer backstory shown before character creation |
| `starting_gold` | int | Gold Pieces the player begins with (default `0`) |
| `starting_provisions` | int | Provisions the player begins with (default `0`) |
| `inventory` | object | `{ "item_name": quantity }` map of starting items (default `{}`) |

### Location block

```json
"42": {
    "description": "Narrative text shown to the player.",
    "exits": {
        "N": "17",
        "open": "85",
        "back": "3"
    },
    "monsters": [
        { "name": "Goblin", "skill": 5, "stamina": 6 }
    ]
}
```

- **Keys** are section numbers as strings
- **`exits`** maps direction/action names to destination section numbers (as strings)
- **`monsters`** is an array of `{ name, skill, stamina }` objects; use `[]` for empty rooms
- Multiple monsters are fought in sequence

#### Optional location fields

Any location may include any of these:

| Field | Type | Effect |
|-------|------|--------|
| `on_entry_effects` | object | `{ "skill": -1, "stamina": -2, "luck": +1 }` — applied automatically on entry. Stats are clamped at 0. |
| `grants_gold` | int | Adds the given number of Gold Pieces to the player. |
| `grants_provisions` | int | Adds Provisions. |
| `grants_item` | string or array | Offers the named item (or each item in the list) — the player chooses to take it. |
| `consumes_item` | string or array | Removes the named item(s) from the inventory if held. |
| `grants_key` | int | Offers a numbered key. Used together with the `key_sum` mechanic. |

Example:

```json
"45": {
    "description": "A merchant offers you a healing draught for 2 Gold Pieces.",
    "on_entry_effects": { "stamina": -1 },
    "grants_item": "healing_draught",
    "exits": { "continue": "46" },
    "monsters": []
}
```

### Mechanic exits

When a location requires an automatic check rather than a player choice, add `lucky` and `unlucky` keys to `exits` and specify a `mechanic`. Most lucky/unlucky mechanics also accept optional `lucky_effects` / `unlucky_effects` inside `mechanic_data` to apply stat changes on each branch.

```json
"71": {
    "description": "Test your Luck to sneak past the sleeping guard...",
    "mechanic": "test_luck",
    "mechanic_data": {
        "unlucky_effects": { "stamina": -2 }
    },
    "exits": {
        "lucky": "301",
        "unlucky": "248"
    },
    "monsters": []
}
```

```json
"298": {
    "description": "Roll one die — a 6 means you slip off the bridge...",
    "mechanic": "dice_roll",
    "mechanic_data": {
        "dice": 1,
        "fail_values": [6]
    },
    "exits": {
        "lucky": "7",
        "unlucky": "86"
    },
    "monsters": []
}
```

```json
"316": {
    "description": "Roll two dice against your STAMINA to swim across...",
    "mechanic": "test_stamina",
    "mechanic_data": {
        "dice": 2
    },
    "exits": {
        "lucky": "151",
        "unlucky": "218"
    },
    "monsters": []
}
```

#### `pre_combat_luck`

Tests Luck immediately before combat starts. `lucky_effects` / `unlucky_effects` are applied to your stats; the fight then proceeds against the monsters defined on the location.

```json
"120": {
    "description": "The orc swings at you before you're ready. Test your Luck.",
    "mechanic": "pre_combat_luck",
    "mechanic_data": {
        "unlucky_effects": { "stamina": -2 }
    },
    "exits": { "continue": "121" },
    "monsters": [{ "name": "Orc", "skill": 6, "stamina": 5 }]
}
```

#### `test_luck_choice`

Lucky goes straight to the `lucky` exit; unlucky forces the player to pick from the remaining exits.

```json
"77": {
    "description": "Test your Luck. If lucky you spot the trapdoor; otherwise you must pick a direction.",
    "mechanic": "test_luck_choice",
    "exits": {
        "lucky": "200",
        "N": "78",
        "S": "79"
    },
    "monsters": []
}
```

#### `dice_table`

Roll dice and look up the destination (and optional effects) in a table. The location's `exits` is unused (typically `{}`).

```json
"55": {
    "description": "Roll two dice on the wandering monster table.",
    "mechanic": "dice_table",
    "mechanic_data": {
        "dice": 2,
        "table": [
            { "rolls": [2, 3, 4],   "destination": "60" },
            { "rolls": [5, 6, 7, 8], "destination": "61", "effects": { "stamina": -1 } },
            { "rolls": [9, 10, 11, 12], "destination": "62" }
        ]
    },
    "exits": {},
    "monsters": []
}
```

#### `random_encounter`

Roll one die against a monster table; if a monster appears, fight it, then return to the section that sent you here (set by a `fight` mechanic).

```json
"180": {
    "description": "A noise behind you — something approaches.",
    "mechanic": "random_encounter",
    "mechanic_data": {
        "table": {
            "1": { "name": "Goblin",  "skill": 5, "stamina": 5 },
            "2": { "name": "Orc",     "skill": 6, "stamina": 6 },
            "3": { "name": "Skeleton","skill": 6, "stamina": 5 }
        }
    },
    "exits": {},
    "monsters": []
}
```

#### `fight` / `return`

`fight` detours the player into a sub-section to resolve a side encounter, then `return` bounces back to where they came from.

```json
"50": {
    "description": "A guard challenges you. Fight!",
    "mechanic": "fight",
    "exits": { "fight": "51" },
    "monsters": []
},
"51": {
    "description": "You defeat the guard and continue on your way.",
    "mechanic": "return",
    "exits": {},
    "monsters": [{ "name": "Guard", "skill": 7, "stamina": 8 }]
}
```

#### `key_sum`

Requires the player to be holding three numbered keys (granted via `grants_key`). Sums them and uses the total as the next section number.

```json
"400": {
    "description": "Three keyholes glow on the door. Insert your keys.",
    "mechanic": "key_sum",
    "exits": {},
    "monsters": []
}
```

#### `item_check`

Branches based on whether the player holds a named item. Set `consume: true` to remove the item on a successful check.

```json
"88": {
    "description": "Do you have the silver key?",
    "mechanic": "item_check",
    "mechanic_data": {
        "item": "silver_key",
        "consume": true
    },
    "exits": {
        "have": "89",
        "missing": "90"
    },
    "monsters": []
}
```

#### `gold_check`

Branches based on whether the player has at least `amount` Gold Pieces. Set `consume: true` to deduct the gold on success.

```json
"112": {
    "description": "The ferryman demands 5 Gold Pieces.",
    "mechanic": "gold_check",
    "mechanic_data": {
        "amount": 5,
        "consume": true
    },
    "exits": {
        "have": "113",
        "missing": "114"
    },
    "monsters": []
}
```

### Endings

A location with an empty `exits` object (`{}`) ends the game — use this for victory or death scenes.

### Adventure file location

Your own adventure JSON files are **gitignored** — only the `game_data.json.example` template is committed to the repository (see `.gitignore`). Place your adventure files in the `adventures/` directory and reference them at runtime:

```bash
python3 main.py adventures/my_adventure.json
```

---

## Project Structure

```
fighting-fantasy/
├── main.py                        # Engine entry point (Player, Location, Monster classes)
├── adventures/
│   └── game_data.json.example     # Example adventure to use as a template
├── tests/
│   ├── harness.py                 # Shared scripted-IO test harness
│   ├── test_static.py             # Static validation of adventure files
│   ├── test_mechanics.py          # Per-mechanic engine tests
│   ├── test_inventory.py          # Inventory, gold, and provisions tests
│   └── test_paths.py              # Known-path playthroughs
├── .github/                       # GitHub workflows / config
├── .gitignore
├── LICENSE
└── README.md
```

## Contributing

Pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup and
workflow details.

Please also review:

- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Security Policy](SECURITY.md)

## Licence

[MIT](LICENSE)
