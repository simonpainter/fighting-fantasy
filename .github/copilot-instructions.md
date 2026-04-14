# Copilot Instructions: Parsing Fighting Fantasy Book Pages into JSON

## Purpose

These instructions describe how to convert photographs or scans of printed **Fighting Fantasy** gamebook pages into correctly structured JSON entries for use with the `main.py` game engine.

---

## JSON Structure Overview

The adventure file is a single JSON object. Every entry is either the special `config` block or a numbered section. All section keys are **strings**.

```json
{
    "config": { ... },
    "1": { ... },
    "2": { ... }
}
```

Each section has this shape:

```json
"<section_number>": {
    "description": "<full narrative text>",
    "exits": { "<action>": "<destination_section>" },
    "monsters": []
}
```

Mechanic sections add optional fields:

```json
"<section_number>": {
    "description": "<full narrative text>",
    "mechanic": "<mechanic_type>",
    "mechanic_data": { ... },
    "exits": {
        "lucky": "<section>",
        "unlucky": "<section>"
    },
    "monsters": []
}
```

---

## Multi-Page Batch Strategy

When given a group of page images to process, follow this workflow rather than parsing each image immediately as you encounter it.

### Phase 1 — Transcribe all pages to temporary files

For every page image, write the raw visible text to a temporary file (e.g. `page_001.txt`, `page_002.txt`, …) **without attempting to parse JSON yet**. Capture everything exactly as printed:

- Section numbers
- All narrative text, including partial sections that run off the bottom of the page
- SKILL / STAMINA monster stats
- "Turn to N" references
- Any mechanic instructions (Test your Luck, Roll one die, etc.)

Do not discard or summarise — accuracy at this stage prevents errors later.

### Phase 2 — Establish page order and section boundaries

Read through all temporary files to build a map of which sections appear on which pages. A section may span multiple pages:

- A page ending mid-sentence means the section continues on the next page.
- A page beginning mid-sentence (no section number at the top) is a continuation of the previous page's last section.
- A single page may contain several complete sections plus a partial one at the end.

Construct an ordered list of sections, noting which temporary files contribute to each:

```
Section 7  → page_003.txt (partial start) + page_004.txt (completion)
Section 8  → page_004.txt
Section 9  → page_004.txt (partial start) + page_005.txt (completion)
```

Only proceed to Phase 3 once every section has all its contributing pages identified.

### Phase 3 — Parse sections one by one into JSON

Work through the ordered section list. For each section:

1. Concatenate the relevant text fragments from the temporary files in page order.
2. Apply the parsing rules below to produce the JSON entry.
3. Append the entry to the target adventure JSON file.
4. Verify the entry before moving to the next section.

Delete the temporary files once all sections have been written successfully.

---

## Step-by-Step Parsing Rules

### 1. Identify the Section Number

- The section number appears as a **bold or large numeral** at the top of the section, before the narrative text.
- Use it as the JSON key (as a string): `"42": { ... }`.
- A page may contain **multiple sections** — parse each one separately.
- Ignore decorative dice images printed at the bottom of pages; they are layout decoration and do not affect the JSON.

### 2. Extract the Description

- Copy the **full narrative text** of the section verbatim as the `"description"` value.
- Preserve all sentence content, including embedded instructions such as "turn to 71" — these are the source material for determining exits but must stay in the description too.
- Use a **single string** (no line breaks). Replace any line breaks in the printed text with a space.
- Do **not** include the section number itself in the description text.

### 3. Determine Exits

Scan the description for phrases like:
- "turn to **N**"
- "go to **N**"
- "return to **N**"

Map each choice to a direction/action key and the destination section number (as a string).

#### Cardinal direction exits

When the text says things like "turn west (turn to 71) or east (turn to 278)":

```json
"exits": {
    "W": "71",
    "E": "278"
}
```

Use single uppercase letters: `N`, `S`, `E`, `W`.

#### Descriptive action exits

When the text offers narrative choices, use a short lowercase word that captures the action:

| Book text | Exit key |
|-----------|----------|
| "charge the door down" | `"charge"` |
| "turn round and go back" | `"back"` |
| "open the door" | `"open"` |
| "ignore this room and continue" | `"ignore"` |
| "search for secret passages" | `"search"` |
| "press on northwards" | `"continue"` |
| "pull the right lever" | `"right"` |
| "Escape through the door" | `"escape"` |
| "If you defeat him, turn to …" (post-combat) | `"fight won"` |

When the section simply redirects with "Turn to N" and no player choice is involved, use `"continue"`:

```json
"exits": { "continue": "319" }
```

#### Endings

Sections that end the game (victory or death with no onward path) use an **empty exits object**:

```json
"exits": {}
```

### 4. Identify Monsters

Look for named creatures with **SKILL** and **STAMINA** values in the text.

Format:

```json
"monsters": [
    { "name": "Goblin", "skill": 5, "stamina": 6 }
]
```

- If no monsters are present, use `"monsters": []`.
- Multiple monsters are listed in the order they must be fought.
- If a monster's stats are not given explicitly in the section text, check adjacent sections or surrounding context.

### 5. Identify Mechanics

When the narrative says **"Test your Luck"**, **"Test your Stamina"**, or **"Roll one/two die/dice"**, the section uses an automatic mechanic rather than a free player choice. Use `"lucky"` and `"unlucky"` exit keys instead of directional keys.

#### `test_luck`

Triggered by: *"Test your Luck"*

```json
"mechanic": "test_luck",
"exits": {
    "lucky": "<section if lucky>",
    "unlucky": "<section if unlucky>"
}
```

No `mechanic_data` needed.

#### `test_stamina`

Triggered by: *"Test your Stamina"* or *"Roll two dice against your STAMINA"*

```json
"mechanic": "test_stamina",
"mechanic_data": { "dice": 2 },
"exits": {
    "lucky": "<section if passed>",
    "unlucky": "<section if failed>"
}
```

#### `dice_roll`

Triggered by: *"Roll one die"* / *"Roll two dice"* where specific values cause failure.

```json
"mechanic": "dice_roll",
"mechanic_data": {
    "dice": 1,
    "fail_values": [6]
},
"exits": {
    "lucky": "<section if not a fail value>",
    "unlucky": "<section if fail value>"
}
```

`fail_values` is an array of integers that cause the unlucky outcome. Parse from text such as "A roll of 6 means you slip".

---

## Worked Example

**Printed page text:**

> **298**
> The bridge is slippery from the splashings of the water. At one point you slip on a tuft of wet moss covering the timbers. Roll one die. A roll of 6 means you slip from the bridge into the water below and start swimming for the nearest bank – turn to 86. Any other roll is lucky; you managed to hold on and you reach the north bank (turn to 7).

**Resulting JSON:**

```json
"298": {
    "description": "The bridge is slippery from the splashings of the water. At one point you slip on a tuft of wet moss covering the timbers. Roll one die. A roll of 6 means you slip from the bridge into the water below and start swimming for the nearest bank – turn to 86. Any other roll is lucky; you managed to hold on and you reach the north bank (turn to 7).",
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

---

## Image Reading Tips

- **Section number**: usually centred at the top of the section block, often in bold or a larger font.
- **Dice icons**: decorative graphics at the bottom of a page spread (e.g., two dice faces) are **not** game data — ignore them.
- **Page splits**: a section may span two pages. Capture the full text before parsing exits.
- **Italic text**: often used for flavour or emphasis; include it verbatim in `description`.
- **SKILL / STAMINA labels in small caps**: these always accompany a monster or a mechanic — watch for them.
- **Multiple sections per page**: each bold/large section number starts a new JSON entry.

---

## Validation Checklist

Before committing a parsed section, verify:

- [ ] Section key is a string matching the printed number.
- [ ] All `"turn to N"` references in the description appear as exit destinations.
- [ ] Exit keys are lowercase (except cardinal directions `N/S/E/W`).
- [ ] Destination section numbers are strings, not integers.
- [ ] Mechanic sections use only `"lucky"` / `"unlucky"` as exit keys.
- [ ] `monsters` is present and is an array (empty `[]` if no monsters).
- [ ] No trailing commas in JSON (invalid JSON).
