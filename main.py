import json
import random
import sys
import time


class Player:
    def __init__(self):
        self.skill = random.randint(1, 6) + 6
        self.stamina = random.randint(1, 6) + random.randint(1, 6) + 12
        self.luck = random.randint(1, 6) + 6
        self.location = None

    def roll_die(self, num_dice=1):
        return sum(random.randint(1, 6) for _ in range(num_dice))

    def test_luck(self):
        roll = random.randint(1, 6) + random.randint(1, 6)
        lucky = roll <= self.luck
        self.luck -= 1
        print(f"\n  Testing Luck: rolled {roll} against LUCK score of {self.luck + 1}")
        if lucky:
            print(f"  You are Lucky! (LUCK is now {self.luck})")
        else:
            print(f"  You are Unlucky! (LUCK is now {self.luck})")
        return lucky

    def fight(self, monster, round_delay=1.5):
        round_num = 0

        while self.stamina > 0 and monster.stamina > 0:
            round_num += 1
            print(f"\n--- Round {round_num} ---")
            print(f"  You:     SKILL={self.skill}  STAMINA={self.stamina}  LUCK={self.luck}")
            print(f"  Monster: SKILL={monster.skill}  STAMINA={monster.stamina}")

            player_roll = random.randint(1, 6) + random.randint(1, 6)
            monster_roll = random.randint(1, 6) + random.randint(1, 6)
            player_attack = player_roll + self.skill
            monster_attack = monster_roll + monster.skill

            print(f"\n  You roll {player_roll} + SKILL {self.skill} = Attack Strength {player_attack}")
            print(f"  Monster rolls {monster_roll} + SKILL {monster.skill} = Attack Strength {monster_attack}")

            if player_attack > monster_attack:
                print("\n  You HIT the monster!")
                use_luck = input("  Test your Luck to deal extra damage? (y/n): ").strip().lower()
                if use_luck == 'y' and self.luck > 0:
                    if self.test_luck():
                        monster.stamina -= 4
                        print(f"  Lucky! You deal 4 damage. Monster STAMINA: {monster.stamina}")
                    else:
                        monster.stamina -= 1
                        print(f"  Unlucky! You deal only 1 damage. Monster STAMINA: {monster.stamina}")
                else:
                    monster.stamina -= 2
                    print(f"  Monster takes 2 damage. Monster STAMINA: {monster.stamina}")

            elif monster_attack > player_attack:
                print("\n  The monster hits you!")
                use_luck = input("  Test your Luck to reduce damage? (y/n): ").strip().lower()
                if use_luck == 'y' and self.luck > 0:
                    if self.test_luck():
                        self.stamina -= 1
                        print(f"  Lucky! You take only 1 damage. Your STAMINA: {self.stamina}")
                    else:
                        self.stamina -= 3
                        print(f"  Unlucky! You take 3 damage. Your STAMINA: {self.stamina}")
                else:
                    self.stamina -= 2
                    print(f"  You take 2 damage. Your STAMINA: {self.stamina}")

            else:
                print("\n  Both attacks deflected — neither side lands a blow.")

            time.sleep(round_delay)

        print("\n" + "=" * 40)
        if self.stamina > 0:
            print("  Victory! The monster has been defeated.")
        else:
            print("  You have been slain. Your adventure ends here.")
        print("=" * 40)

        return self.stamina > 0

    def play(self, adventure):
        self.location = Location("1", adventure)

        while self.stamina > 0:
            print("\n" + "=" * 60)
            print(self.location.description)

            for monster in self.location.monsters:
                if monster.stamina > 0:
                    print(f"\nA {monster.name} blocks your path! (SKILL {monster.skill}, STAMINA {monster.stamina})")
                    input("Press Enter to fight...")
                    self.fight(monster)
                    if self.stamina <= 0:
                        break

            if self.stamina <= 0:
                break

            if not self.location.exits:
                print("\nYour quest is complete. Well done, adventurer!")
                break

            if "lucky" in self.location.exits and "unlucky" in self.location.exits:
                if self.location.mechanic == "dice_roll":
                    num_dice = self.location.mechanic_data.get("dice", 1)
                    fail_values = self.location.mechanic_data.get("fail_values", [])
                    input(f"\nPress Enter to roll {num_dice} die/dice...")
                    roll = self.roll_die(num_dice)
                    print(f"\n  You rolled: {roll}")
                    passed = roll not in fail_values
                    next_id = str(self.location.exits["lucky"] if passed else self.location.exits["unlucky"])
                    print(f"  {'You keep your footing!' if passed else 'You slip!'}")
                elif self.location.mechanic == "test_stamina":
                    num_dice = self.location.mechanic_data.get("dice", 2)
                    input(f"\nPress Enter to test your Stamina...")
                    roll = self.roll_die(num_dice)
                    passed = roll <= self.stamina
                    print(f"\n  You rolled: {roll} against STAMINA {self.stamina}")
                    print(f"  {'You make it!' if passed else 'You cannot make it.'}")
                    next_id = str(self.location.exits["lucky"] if passed else self.location.exits["unlucky"])
                elif self.location.mechanic == "test_luck":
                    input("\nPress Enter to Test your Luck...")
                    next_id = str(self.location.exits["lucky"] if self.test_luck() else self.location.exits["unlucky"])
                try:
                    self.location = Location(next_id, adventure)
                except KeyError as e:
                    print(f"\n  {e}")
                    break
                continue

            print(f"\nExits: {', '.join(self.location.exits.keys())}")
            print(f"  SKILL={self.skill}  STAMINA={self.stamina}  LUCK={self.luck}")

            try:
                choice = input("\nWhich direction? ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\nFarewell, adventurer.")
                break

            matched = next((k for k in self.location.exits if k.upper() == choice.upper()), None)
            if matched:
                try:
                    self.location = Location(str(self.location.exits[matched]), adventure)
                except KeyError as e:
                    print(f"\n  {e}")
                    break
            else:
                print(f"  You can't go that way. Choose from: {', '.join(self.location.exits.keys())}")

        if self.stamina <= 0:
            print("\nYou have been slain. Your adventure is over.")


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

    player = Player()
    print(f"\nYour character has been created:")
    print(f"  SKILL:   {player.skill}")
    print(f"  STAMINA: {player.stamina}")
    print(f"  LUCK:    {player.luck}")
    print(f"\nYour adventure begins...\n")

    player.play(adventure)


