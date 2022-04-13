import random


class Enemy:
    def __init__(self, hp, dmg):
        self.hp = hp
        self.dmg = dmg
        self.is_alive = True
        self.current_stage = 1
        self.current_round = 1

    def attack(self, character):
        random_dmg = random.randint(1, self.dmg)
        character.take_damage(random_dmg)
        return random_dmg

    def alive(self):
        if self.hp > 0:
            self.is_alive = True
        else:
            self.is_alive = False
        return self.is_alive

    def take_damage(self, amount):
        if self.hp - amount <= 0:
            self.hp = 0
        else:
            self.hp -= amount
        return self.hp

    def stage_up(self):
        self.current_stage += 1
        self.current_round = 1

    def round_up(self):
        self.current_round += 1


class PartialExam(Enemy):
    HP = 20
    DMG = 6

    def __init__(self):
        super().__init__(PartialExam.HP, PartialExam.DMG)

    @staticmethod
    def enemy_info():
        return "Partial exam -> Stats: {}HP and {}DMG".format(PartialExam.HP, PartialExam.DMG)


class FinalExam(Enemy):
    HP = 40
    DMG = 12

    def __init__(self):
        super().__init__(FinalExam.HP, FinalExam.DMG)

    @staticmethod
    def enemy_info():
        return "Final exam -> Stats: {}HP and {}DMG".format(FinalExam.HP, FinalExam.DMG)


class TheoreticalClass(Enemy):
    HP = 8
    DMG = 4

    def __init__(self):
        super().__init__(TheoreticalClass.HP, TheoreticalClass.DMG)

    def attack(self, character):
        random_dmg = random.randint(1, self.dmg) + self.current_stage
        character.take_damage(random_dmg)
        return random_dmg

    @staticmethod
    def enemy_info():
        return "Theoretical class -> Stats: {}HP and {}DMG".format(TheoreticalClass.HP, TheoreticalClass.DMG)


class Teacher(Enemy):
    HP = 15
    DMG = 7

    def __init__(self):
        super().__init__(Teacher.HP, Teacher.DMG)

    def attack(self, character):
        random_dmg = random.randint(1, self.dmg)
        if random_dmg == 7:
            random_dmg *= 2
        character.take_damage(random_dmg)
        return random_dmg

    @staticmethod
    def enemy_info():
        return "Teacher -> Stats: {}HP and {}DMG".format(Teacher.HP, Teacher.DMG)
