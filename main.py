import json
import random
import sys
import time


class Player:
    def __init__(self):
        self.skill = random.randint(1, 6) + 6
        self.stamina = random.randint(2, 12) + 12
        self.luck = random.randint(1, 6) + 6

    def test_luck(self):
        roll = random.randint(2, 12)
        lucky = roll <= self.luck
        self.luck -= 1
        return lucky

    def fight(self, monster, round_delay=1.5):
        round_num = 0

        while self.stamina > 0 and monster.stamina > 0:
            round_num += 1
            print(f"\n--- Round {round_num} ---")
            print(f"  You:     SKILL={self.skill}  STAMINA={self.stamina}  LUCK={self.luck}")
            print(f"  Monster: SKILL={monster.skill}  STAMINA={monster.stamina}")

            player_roll = random.randint(2, 12)
            monster_roll = random.randint(2, 12)
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


class Location:
    def __init__(self, location_id, adventure):
        data = adventure[location_id]
        self.id = location_id
        self.description = data["description"]
        self.exits = data["exits"]
        self.monsters = [
            Monster(m["skill"], m["stamina"]) for m in data["monsters"]
        ]


class Monster:
    def __init__(self, skill, stamina):
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

    player = Player()
    print("=" * 60)
    print("Welcome to " + adventure.get("config", {}).get("title", "the adventure") + "!")
    print("Author: " + adventure.get("config", {}).get("author", "Unknown"))    
    print("=" * 60)
    print(f"\nYour character has been created:")
    print(f"  SKILL:   {player.skill}")
    print(f"  STAMINA: {player.stamina}")
    print(f"  LUCK:    {player.luck}")
    print(f"\nYour adventure begins...\n")
