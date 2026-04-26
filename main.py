import json
import random
import sys
import time


class Player:
    def __init__(self, config=None, rng=None, input_fn=None, output_fn=None):
        config = config or {}
        self._rng = rng if rng is not None else random
        self._input = input_fn if input_fn is not None else input
        self._print = output_fn if output_fn is not None else print
        self._sleep = (lambda s: None) if rng is not None else time.sleep
        self.skill = self._rng.randint(1, 6) + 6
        self.initial_stamina = self._rng.randint(1, 6) + self._rng.randint(1, 6) + 12
        self.stamina = self.initial_stamina
        self.luck = self._rng.randint(1, 6) + 6
        self.initial_luck = self.luck
        self.location = None
        self.return_to = None
        self.keys = []
        self.inventory = {name: int(qty) for name, qty in config.get("inventory", {}).items()}
        self.gold = int(config.get("starting_gold", 0))
        self.provisions = int(config.get("starting_provisions", 0))

    def has_item(self, item):
        return self.inventory.get(item, 0) > 0

    def grant_item(self, item, qty=1):
        self.inventory[item] = self.inventory.get(item, 0) + qty
        self._print(f"  + {item.replace('_', ' ').title()} (now have {self.inventory[item]})")

    def consume_item(self, item, qty=1):
        if self.inventory.get(item, 0) >= qty:
            self.inventory[item] -= qty
            self._print(f"  - {item.replace('_', ' ').title()} used (now have {self.inventory[item]})")
            return True
        return False

    def show_inventory(self):
        self._print("\n  --- Inventory ---")
        self._print(f"  Gold: {self.gold}   Provisions: {self.provisions}")
        held = {k: v for k, v in self.inventory.items() if v > 0}
        if held:
            for item, qty in sorted(held.items()):
                label = item.replace('_', ' ').title()
                self._print(f"    {label}" + (f" x{qty}" if qty > 1 else ""))
        else:
            self._print("    (no items)")
        if self.keys:
            self._print(f"  Keys: {self.keys}")
        self._print("  -----------------")

    def eat_provisions(self):
        if self.provisions <= 0:
            self._print("  You have no Provisions left.")
            return
        if self.stamina >= self.initial_stamina:
            self._print("  Your STAMINA is already at its initial level — you cannot benefit from eating.")
            return
        self.provisions -= 1
        gain = min(4, self.initial_stamina - self.stamina)
        self.stamina += gain
        self._print(f"  You eat a meal. STAMINA +{gain} (now {self.stamina}). Provisions left: {self.provisions}")

    def _advance_to(self, next_id, adventure):
        """Move to next section. Returns True if game should continue, False to break.
        Empty/None destination means a fatal branch (e.g., 'the lightning kills you')."""
        if not next_id:
            self._print("\nThis path proves fatal. Your adventure ends here.")
            self.stamina = 0
            return False
        try:
            self.location = Location(str(next_id), adventure)
        except KeyError as e:
            self._print(f"\n  {e}")
            return False
        return True

    def roll_die(self, num_dice=1):
        return sum(self._rng.randint(1, 6) for _ in range(num_dice))

    def apply_effects(self, effects):
        if not effects:
            return
        for stat, delta in effects.items():
            if stat not in ("skill", "stamina", "luck"):
                continue
            old = getattr(self, stat)
            new = max(0, old + int(delta))
            setattr(self, stat, new)
            sign = "+" if delta >= 0 else ""
            self._print(f"  {stat.upper()} {sign}{delta} (now {new})")

    def test_luck(self):
        roll = self._rng.randint(1, 6) + self._rng.randint(1, 6)
        lucky = roll <= self.luck
        self.luck -= 1
        self._print(f"\n  Testing Luck: rolled {roll} against LUCK score of {self.luck + 1}")
        if lucky:
            self._print(f"  You are Lucky! (LUCK is now {self.luck})")
        else:
            self._print(f"  You are Unlucky! (LUCK is now {self.luck})")
        return lucky

    def fight(self, monster, round_delay=1.5):
        round_num = 0

        while self.stamina > 0 and monster.stamina > 0:
            round_num += 1
            self._print(f"\n--- Round {round_num} ---")
            self._print(f"  You:     SKILL={self.skill}  STAMINA={self.stamina}  LUCK={self.luck}")
            self._print(f"  Monster: SKILL={monster.skill}  STAMINA={monster.stamina}")

            player_roll = self._rng.randint(1, 6) + self._rng.randint(1, 6)
            monster_roll = self._rng.randint(1, 6) + self._rng.randint(1, 6)
            player_attack = player_roll + self.skill
            monster_attack = monster_roll + monster.skill

            self._print(f"\n  You roll {player_roll} + SKILL {self.skill} = Attack Strength {player_attack}")
            self._print(f"  Monster rolls {monster_roll} + SKILL {monster.skill} = Attack Strength {monster_attack}")

            if player_attack > monster_attack:
                self._print("\n  You HIT the monster!")
                use_luck = self._input("  Test your Luck to deal extra damage? (y/n): ").strip().lower()
                if use_luck == 'y' and self.luck > 0:
                    if self.test_luck():
                        monster.stamina -= 4
                        self._print(f"  Lucky! You deal 4 damage. Monster STAMINA: {monster.stamina}")
                    else:
                        monster.stamina -= 1
                        self._print(f"  Unlucky! You deal only 1 damage. Monster STAMINA: {monster.stamina}")
                else:
                    monster.stamina -= 2
                    self._print(f"  Monster takes 2 damage. Monster STAMINA: {monster.stamina}")

            elif monster_attack > player_attack:
                self._print("\n  The monster hits you!")
                use_luck = self._input("  Test your Luck to reduce damage? (y/n): ").strip().lower()
                if use_luck == 'y' and self.luck > 0:
                    if self.test_luck():
                        self.stamina -= 1
                        self._print(f"  Lucky! You take only 1 damage. Your STAMINA: {self.stamina}")
                    else:
                        self.stamina -= 3
                        self._print(f"  Unlucky! You take 3 damage. Your STAMINA: {self.stamina}")
                else:
                    self.stamina -= 2
                    self._print(f"  You take 2 damage. Your STAMINA: {self.stamina}")

            else:
                self._print("\n  Both attacks deflected — neither side lands a blow.")

            self._sleep(round_delay)

        self._print("\n" + "=" * 40)
        if self.stamina > 0:
            self._print("  Victory! The monster has been defeated.")
        else:
            self._print("  You have been slain. Your adventure ends here.")
        self._print("=" * 40)

        return self.stamina > 0

    def play(self, adventure):
        return self.start_at(adventure, "1")

    def start_at(self, adventure, section_id="1"):
        self.location = Location(section_id, adventure)

        while self.stamina > 0:
            self._print("\n" + "=" * 60)
            self._print(self.location.description)

            self.apply_effects(self.location.on_entry_effects)

            if self.location.grants_gold:
                amount = int(self.location.grants_gold)
                self.gold += amount
                self._print(f"  + {amount} Gold Pieces (now {self.gold})")

            if self.location.grants_provisions:
                amount = int(self.location.grants_provisions)
                self.provisions += amount
                self._print(f"  + {amount} Provisions (now {self.provisions})")

            if self.location.grants_item:
                items = self.location.grants_item
                if isinstance(items, str):
                    items = [items]
                for it in items:
                    label = it.replace('_', ' ')
                    offer = self._input(f"\nYou can take the {label}. Take it? (y/n): ").strip().lower()
                    if offer == 'y':
                        self.grant_item(it)

            if self.location.consumes_item:
                items = self.location.consumes_item
                if isinstance(items, str):
                    items = [items]
                for it in items:
                    self.consume_item(it)

            if self.location.grants_key is not None:
                key_num = int(self.location.grants_key)
                offer = self._input(f"\nYou can take a key numbered {key_num}. Take it? (y/n): ").strip().lower()
                if offer == 'y':
                    self.keys.append(key_num)
                    self._print(f"  Key #{key_num} added. You now hold: {self.keys}")

            if self.location.mechanic == "key_sum":
                if len(self.keys) < 3:
                    self._print(f"\n  You only have {len(self.keys)} keys ({self.keys}). You need three.")
                    self._print("  Your quest ends here.")
                    break
                self._print(f"\n  You have keys: {self.keys}")
                # Allow choice of three if more than three
                if len(self.keys) > 3:
                    sel = self._input(f"  Choose three (comma-separated, e.g. {','.join(str(k) for k in self.keys[:3])}): ").strip()
                    try:
                        chosen = [int(x.strip()) for x in sel.split(',')]
                        # Verify these keys are actually held (handle duplicates)
                        held = list(self.keys)
                        for k in chosen:
                            held.remove(k)
                        if len(chosen) != 3:
                            raise ValueError
                    except (ValueError, IndexError):
                        self._print("  Invalid selection. Quest ends here.")
                        break
                else:
                    chosen = list(self.keys)
                total = sum(chosen)
                self._print(f"  Sum: {' + '.join(str(k) for k in chosen)} = {total}")
                next_id = str(total)
                try:
                    self.location = Location(next_id, adventure)
                except KeyError as e:
                    self._print(f"\n  {e}")
                    break
                continue

            if self.location.mechanic == "pre_combat_luck":
                self._input("\nPress Enter to Test your Luck before combat...")
                if not self.test_luck():
                    self.apply_effects(self.location.mechanic_data.get("unlucky_effects"))
                else:
                    self.apply_effects(self.location.mechanic_data.get("lucky_effects"))
                if self.stamina <= 0:
                    break

            if self.location.mechanic == "random_encounter" and not self.location.monsters:
                self._input("\nPress Enter to roll a die to see what creature appears...")
                roll = self.roll_die(1)
                table = self.location.mechanic_data.get("table", {})
                monster_data = table.get(str(roll))
                if monster_data:
                    self.location.monsters = [Monster(monster_data["name"], monster_data["skill"], monster_data["stamina"])]
                    self._print(f"\n  You rolled a {roll} — a {monster_data['name']} appears!")
                else:
                    self._print(f"\n  You rolled a {roll} — no creature appears.")

            for monster in self.location.monsters:
                if monster.stamina > 0:
                    self._print(f"\nA {monster.name} blocks your path! (SKILL {monster.skill}, STAMINA {monster.stamina})")
                    self._input("Press Enter to fight...")
                    self.fight(monster)
                    if self.stamina <= 0:
                        break

            if self.stamina <= 0:
                break

            if self.location.mechanic == "fight" and "fight" in self.location.exits:
                self.return_to = self.location.id
                try:
                    self.location = Location(str(self.location.exits["fight"]), adventure)
                except KeyError as e:
                    self._print(f"\n  {e}")
                    break
                continue

            if self.location.mechanic in ("return", "random_encounter"):
                if self.return_to:
                    return_id = self.return_to
                    self.return_to = None
                    try:
                        self.location = Location(return_id, adventure)
                    except KeyError as e:
                        self._print(f"\n  {e}")
                        break
                    continue
                else:
                    self._print("\n  (No return destination recorded — continuing normally.)")

            # `dice_table` and `key_sum` route via mechanic_data, not exits,
            # so an empty exits dict is normal for them.
            if not self.location.exits and self.location.mechanic not in ("dice_table", "key_sum"):
                self._print("\nYour quest is complete. Well done, adventurer!")
                break

            if self.location.mechanic == "dice_table":
                num_dice = self.location.mechanic_data.get("dice", 1)
                table = self.location.mechanic_data.get("table", [])
                self._input(f"\nPress Enter to roll {num_dice} die/dice...")
                roll = self.roll_die(num_dice)
                self._print(f"\n  You rolled: {roll}")
                next_id = None
                for entry in table:
                    if roll in entry.get("rolls", []):
                        self.apply_effects(entry.get("effects"))
                        next_id = str(entry["destination"])
                        break
                if next_id is None:
                    self._print(f"  No table entry for roll {roll} — staying put.")
                    continue
                try:
                    self.location = Location(next_id, adventure)
                except KeyError as e:
                    self._print(f"\n  {e}")
                    break
                continue

            if self.location.mechanic == "test_luck_choice":
                self._input("\nPress Enter to Test your Luck...")
                if self.test_luck():
                    self.apply_effects(self.location.mechanic_data.get("lucky_effects"))
                    next_id = str(self.location.exits["lucky"])
                    try:
                        self.location = Location(next_id, adventure)
                    except KeyError as e:
                        self._print(f"\n  {e}")
                        break
                    continue
                else:
                    self.apply_effects(self.location.mechanic_data.get("unlucky_effects"))
                    remaining = {k: v for k, v in self.location.exits.items() if k != "lucky"}
                    self._print(f"\nUnlucky! You must now choose:")
                    self._print(f"Exits: {', '.join(remaining.keys())}")
                    try:
                        choice = self._input("\nWhich? ").strip()
                    except (EOFError, KeyboardInterrupt):
                        self._print("\n\nFarewell, adventurer.")
                        break
                    matched = next((k for k in remaining if k.upper() == choice.upper()), None)
                    if matched:
                        try:
                            self.location = Location(str(remaining[matched]), adventure)
                        except KeyError as e:
                            self._print(f"\n  {e}")
                            break
                    else:
                        self._print(f"  Invalid choice.")
                    continue

            if "lucky" in self.location.exits and "unlucky" in self.location.exits:
                if self.location.mechanic == "dice_roll":
                    num_dice = self.location.mechanic_data.get("dice", 1)
                    fail_values = self.location.mechanic_data.get("fail_values", [])
                    self._input(f"\nPress Enter to roll {num_dice} die/dice...")
                    roll = self.roll_die(num_dice)
                    self._print(f"\n  You rolled: {roll}")
                    passed = roll not in fail_values
                    next_id = str(self.location.exits["lucky"] if passed else self.location.exits["unlucky"])
                    self._print(f"  {'You keep your footing!' if passed else 'You slip!'}")
                elif self.location.mechanic == "test_stamina":
                    num_dice = self.location.mechanic_data.get("dice", 2)
                    self._input(f"\nPress Enter to test your Stamina...")
                    roll = self.roll_die(num_dice)
                    passed = roll <= self.stamina
                    self._print(f"\n  You rolled: {roll} against STAMINA {self.stamina}")
                    self._print(f"  {'You make it!' if passed else 'You cannot make it.'}")
                    next_id = str(self.location.exits["lucky"] if passed else self.location.exits["unlucky"])
                elif self.location.mechanic == "test_luck":
                    self._input("\nPress Enter to Test your Luck...")
                    passed = self.test_luck()
                    next_id = str(self.location.exits["lucky"] if passed else self.location.exits["unlucky"])
                if passed:
                    self.apply_effects(self.location.mechanic_data.get("lucky_effects"))
                else:
                    self.apply_effects(self.location.mechanic_data.get("unlucky_effects"))
                if not self._advance_to(next_id, adventure):
                    break
                continue

            if self.location.mechanic == "item_check":
                item = self.location.mechanic_data.get("item")
                consume = self.location.mechanic_data.get("consume", False)
                has = self.has_item(item)
                label = (item or "").replace('_', ' ')
                if has:
                    self._print(f"\n  You have the {label}.")
                    if consume:
                        self.consume_item(item)
                    next_id = str(self.location.exits.get("have"))
                else:
                    self._print(f"\n  You don't have a {label}.")
                    next_id = str(self.location.exits.get("missing"))
                try:
                    self.location = Location(next_id, adventure)
                except KeyError as e:
                    self._print(f"\n  {e}")
                    break
                continue

            if self.location.mechanic == "gold_check":
                amount = int(self.location.mechanic_data.get("amount", 1))
                consume = self.location.mechanic_data.get("consume", False)
                if self.gold >= amount:
                    self._print(f"\n  You have at least {amount} Gold Pieces.")
                    if consume:
                        self.gold -= amount
                        self._print(f"  - {amount} Gold (now {self.gold})")
                    next_id = str(self.location.exits.get("have"))
                else:
                    self._print(f"\n  You only have {self.gold} Gold Pieces — not enough.")
                    next_id = str(self.location.exits.get("missing"))
                try:
                    self.location = Location(next_id, adventure)
                except KeyError as e:
                    self._print(f"\n  {e}")
                    break
                continue

            self._print(f"\nExits: {', '.join(self.location.exits.keys())}")
            self._print(f"  SKILL={self.skill}  STAMINA={self.stamina}  LUCK={self.luck}")

            matched = None
            while matched is None:
                try:
                    raw = self._input("\nWhich direction? (or 'inv' / 'eat') ").strip()
                except (EOFError, KeyboardInterrupt):
                    self._print("\n\nFarewell, adventurer.")
                    return
                if raw.lower() in ("inv", "i", "inventory"):
                    self.show_inventory()
                    continue
                if raw.lower() in ("eat", "e"):
                    self.eat_provisions()
                    continue
                matched = next((k for k in self.location.exits if k.upper() == raw.upper()), None)
                if matched is None:
                    self._print(f"  You can't go that way. Choose from: {', '.join(self.location.exits.keys())}")

            try:
                self.location = Location(str(self.location.exits[matched]), adventure)
            except KeyError as e:
                self._print(f"\n  {e}")
                break

        if self.stamina <= 0:
            self._print("\nYou have been slain. Your adventure is over.")


class Location:
    def __init__(self, location_id, adventure):
        data = adventure.get(location_id)
        if data is None:
            raise KeyError(f"Section {location_id} has not yet been added to this adventure.")
        self.id = location_id
        self.description = data["description"]
        self.exits = data["exits"]
        self.mechanic = data.get("mechanic")
        self.mechanic_data = data.get("mechanic_data", {})
        self.on_entry_effects = data.get("on_entry_effects", {})
        self.grants_key = data.get("grants_key")
        self.grants_item = data.get("grants_item")
        self.grants_gold = data.get("grants_gold")
        self.grants_provisions = data.get("grants_provisions")
        self.consumes_item = data.get("consumes_item")
        self.monsters = [
            Monster(m["name"], m["skill"], m["stamina"]) for m in data["monsters"]
        ]


class Monster:
    def __init__(self, name, skill, stamina):
        self.name = name
        self.skill = skill
        self.stamina = stamina


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path/to/adventure.json>")
        sys.exit(1)

    adventure_file = sys.argv[1]
    try:
        with open(adventure_file) as f:
            adventure = json.load(f)
    except FileNotFoundError:
        print(f"Error: Adventure file '{adventure_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Could not parse adventure file — {e}")
        sys.exit(1)

    config = adventure.get("config", {})
    print("=" * 60)
    print("Welcome to " + config.get("title", "the adventure") + "!")
    print("Author: " + config.get("author", "Unknown"))
    print("=" * 60)

    if config.get("description"):
        print(f"\n{config['description']}")

    if config.get("background"):
        print(f"\n--- BACKGROUND ---\n")
        print(config["background"])

    input("\nPress Enter to create your character...")
    player = Player(config)
    print(f"\nYour character has been created:")
    print(f"  SKILL:   {player.skill}")
    print(f"  STAMINA: {player.stamina}")
    print(f"  LUCK:    {player.luck}")
    if player.gold or player.provisions:
        print(f"  GOLD:    {player.gold}")
        print(f"  PROV:    {player.provisions}")
    print(f"\nYour adventure begins...\n")

    player.play(adventure)


