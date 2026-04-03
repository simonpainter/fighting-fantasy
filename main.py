import random


class Player:
    def __init__(self):
        self.skill = random.randint(1, 6) + 6
        self.stamina = random.randint(2, 12) + 12
        self.luck = random.randint(1, 6) + 6

    def fight(self, monster):
        while self.stamina > 0 and monster.stamina > 0:
            player_attack = random.randint(2, 12) + self.skill
            monster_attack = random.randint(2, 12) + monster.skill

            if player_attack > monster_attack:
                monster.stamina -= 2
            elif monster_attack > player_attack:
                self.stamina -= 2

        return self.stamina > 0


class Monster:
    def __init__(self, skill, stamina):
        self.skill = skill
        self.stamina = stamina
