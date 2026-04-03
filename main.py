import random


class Player:
    def __init__(self):
        self.skill = random.randint(1, 6) + 6
        self.stamina = random.randint(2, 12) + 12
        self.luck = random.randint(1, 6) + 6
