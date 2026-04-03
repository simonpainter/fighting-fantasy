# Fighting Fantasy

A Python engine for running text-based adventure games in the style of the classic [Fighting Fantasy](https://en.wikipedia.org/wiki/Fighting_Fantasy) gamebook series, created by Steve Jackson and Ian Livingstone.

## Overview

Fighting Fantasy gamebooks are single-player role-playing adventures first published in 1982. Each book is divided into numbered sections; the reader makes choices that jump between sections, resolving combat and challenges with two six-sided dice and three character attributes: **SKILL**, **STAMINA**, and **LUCK**.

This project provides a Python game engine that faithfully recreates that experience in the terminal — branching narrative, dice-based combat, inventory, and all.

## Features

- **Branching narrative engine** — section-based story graph where player choices drive progression
- **Character creation** — roll SKILL, STAMINA, and LUCK at the start of each adventure
- **Turn-based combat** — faithful implementation of the Fighting Fantasy combat rules
- **Luck tests** — Test your Luck to modify outcomes, at the cost of your LUCK score
- **Inventory management** — collect and use items and provisions throughout your adventure
- **Adventure data format** — define adventures in structured data files; no code changes needed

## Getting Started

### Prerequisites

- Python 3.10+

### Installation

```bash
git clone https://github.com/simonpainter/fighting-fantasy.git
cd fighting-fantasy
pip install -r requirements.txt
```

### Running

```bash
python main.py adventures/warlock.json
```

## How to Play

### Character Attributes

At the start of an adventure your character's attributes are rolled randomly:

| Attribute | Roll | Description |
|-----------|------|-------------|
| **SKILL** | 1d6 + 6 | Combat prowess and dexterity (max 12) |
| **STAMINA** | 2d6 + 12 | Health — reach 0 and you're dead (max 24) |
| **LUCK** | 1d6 + 6 | Fortune — decreases each time you test it (max 12) |

### Combat

Each combat round, both you and your opponent roll 2d6 and add your respective SKILL scores to get an **Attack Strength**. The higher value wins the round and deals **2 points of STAMINA** damage to the loser. A tie means both miss.

### Testing Your Luck

Roll 2d6. If the result is ≤ your current LUCK score you are **Lucky** — your LUCK then decreases by 1 regardless of outcome.

## Project Structure

```
fighting-fantasy/
├── main.py          # Entry point
├── engine/          # Core game engine
│   ├── game.py      # Game loop and section navigation
│   ├── character.py # Character attributes and dice rolling
│   ├── combat.py    # Combat resolution
│   └── inventory.py # Inventory management
├── adventures/      # Adventure data files
└── tests/           # Unit tests
```

## Contributing

Pull requests are welcome. Please open an issue first to discuss significant changes.

## Licence

[MIT](LICENSE)
