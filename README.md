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
- **Multiple mechanics** — luck tests, stamina tests, and dice-roll challenges all supported
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
    "background": "Longer backstory shown before character creation."
}
```

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

### Mechanic exits

When a location requires an automatic check rather than a player choice, add `lucky` and `unlucky` keys to `exits` and specify a `mechanic`:

```json
"71": {
    "description": "Test your Luck to sneak past the sleeping guard...",
    "mechanic": "test_luck",
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

### Endings

A location with an empty `exits` object (`{}`) ends the game — use this for victory or death scenes.

### Adventure file location

Adventure JSON files are **not committed to the repository** (see `.gitignore`). Place your adventure files in the `adventures/` directory and reference them at runtime:

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
├── .gitignore
└── README.md
```

## Contributing

Pull requests are welcome. Please open an issue first to discuss significant changes.

## Licence

[MIT](LICENSE)
