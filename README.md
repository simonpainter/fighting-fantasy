# Fighting Fantasy

A digital implementation of the classic Fighting Fantasy gamebook adventure system.

## Overview

This project brings the iconic Fighting Fantasy tabletop RPG experience to life in a digital format. Players can explore branching narratives, manage their character's stats, and battle enemies using the classic dice-based combat system.

## Features

- **Character creation** — Roll your SKILL, STAMINA, and LUCK attributes
- **Turn-based combat** — Fight monsters using the classic Fighting Fantasy combat rules
- **Branching narrative** — Make choices that shape your adventure
- **Inventory management** — Collect items, provisions, and equipment
- **Dice mechanics** — Faithful recreation of the two-dice system from the books

## Getting Started

### Prerequisites

> Add your runtime/language requirements here (e.g., Node.js, Python, etc.)

### Installation

```bash
git clone https://github.com/simonpainter/fighting-fantasy.git
cd fighting-fantasy
```

> Add installation steps here.

### Running

> Add run instructions here.

## How to Play

Characters have three core attributes:

| Attribute | Description |
|-----------|-------------|
| **SKILL** | Combat ability and dexterity (rolled as 1d6 + 6) |
| **STAMINA** | Health points (rolled as 2d6 + 12) |
| **LUCK** | Fortune and fate (rolled as 1d6 + 6) |

Combat is resolved each round by both sides rolling 2d6 and adding their SKILL. The higher total hits the opponent, reducing their STAMINA by 2. A tie means both miss.

## Contributing

Pull requests are welcome. Please open an issue first to discuss significant changes.

## Licence

[MIT](LICENSE)
