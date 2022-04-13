import random


class Character:
    def __init__(self, hp, dmg, cooldown_limit, hp_max):
        self.hp = hp
        self.dmg = dmg
        self.cooldown_limit = cooldown_limit
        self.hp_max = hp_max
        self.cooldown = 0
        self.is_alive = True
        self.current_stage = 1
        self.current_round = 1

    def attack(self, enemy):
        random_dmg = random.randint(1, self.dmg)
        enemy.take_damage(random_dmg)
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

    def skill(self, target):
        pass

    def receive_healing(self, amount):
        if self.hp + amount > self.hp_max:
            self.hp = self.hp_max
        else:
            self.hp += amount

    def revive(self):
        self.hp = self.hp_max
        self.alive()

    def stage_up(self):
        self.current_stage += 1
        self.current_round = 1
        self.cooldown = 0
        if self.alive():
            if (self.hp + self.hp/4) > self.hp_max:
                self.hp = self.hp_max
            else:
                self.hp += self.hp_max/4

    def round_up(self):
        self.current_round += 1
        self.cooldown -= 1
        if self.cooldown < 0:
            self.cooldown = 0


class CooldownError(Exception):
    def __init__(self, msg):
        super().__init__("{}".format(msg))


class Bookworm(Character):
    HP = 25
    DMG = 9
    COOLDOWN_LIMIT = 4

    def __init__(self):
        super().__init__(Bookworm.HP, Bookworm.DMG, Bookworm.COOLDOWN_LIMIT, Bookworm.HP)

    def skill(self, character):
        if self.cooldown == 0:
            character.revive()
            self.cooldown = Bookworm.COOLDOWN_LIMIT
        else:
            raise CooldownError("You must wait {} rounds".format(self.cooldown))

    @staticmethod
    def character_info():
        return '''Bookworm -> 
        Stats: {}HP and {}DMG. 
        Skill: Revives one player ({} rounds)
        '''.format(Bookworm.HP, Bookworm.DMG, Bookworm.COOLDOWN_LIMIT)


class Worker(Character):
    HP = 40
    DMG = 10
    COOLDOWN_LIMIT = 3

    def __init__(self):
        super().__init__(Worker.HP, Worker.DMG, Worker.COOLDOWN_LIMIT, Worker.HP)

    def skill(self, enemy):
        if self.cooldown == 0:
            random_dmg = random.randint(1, self.dmg)
            amount = (self.dmg + random_dmg) * 1.5
            enemy.take_damage(amount)
            self.cooldown = Worker.COOLDOWN_LIMIT
            return amount
        else:
            raise CooldownError("You must wait {} rounds".format(self.cooldown))

    @staticmethod
    def character_info():
        return '''Worker -> 
        Stats: {}HP and {}DMG. 
        Skill: 1.5 * (DMG + DMG roll) damage to one enemy ({} rounds)
        '''.format(Worker.HP, Worker.DMG, Worker.COOLDOWN_LIMIT)


class Whatsapper(Character):
    HP = 20
    DMG = 6
    COOLDOWN_LIMIT = 3

    def __init__(self):
        super().__init__(Whatsapper.HP, Whatsapper.DMG, Whatsapper.COOLDOWN_LIMIT, Whatsapper.HP)

    def skill(self, character):
        if self.cooldown == 0:
            amount = 2 * self.dmg
            character.receive_healing(amount)
            self.cooldown = Whatsapper.COOLDOWN_LIMIT
            return amount
        else:
            raise CooldownError("You must wait {} rounds".format(self.cooldown))

    @staticmethod
    def character_info():
        return '''Whatsapper -> 
        Stats: {}HP and {}DMG. 
        Skill: Heals 2 * DMG to one player ({} rounds)
        '''.format(Whatsapper.HP, Whatsapper.DMG, Whatsapper.COOLDOWN_LIMIT)


class Procrastinator(Character):
    HP = 30
    DMG = 6
    COOLDOWN_LIMIT = 3

    def __init__(self):
        super().__init__(Procrastinator.HP, Procrastinator.DMG, Procrastinator.COOLDOWN_LIMIT, Procrastinator.HP)
        self.cooldown = Procrastinator.COOLDOWN_LIMIT
        self.dmg_bonus = 0
        self.stage_used = False

    def skill(self, enemy_list):
        if self.cooldown == 0 and not self.stage_used:
            dmg_roll = random.randint(1, self.dmg)
            amount = self.dmg + dmg_roll + self.current_stage
            for enemy in enemy_list:
                enemy.take_damage(amount)
            self.stage_used = True
            return amount
        elif self.cooldown == 0 and self.stage_used:
            raise CooldownError("You have used your skill. Please, wait for the next stage to use it")
        else:
            raise CooldownError("You must wait {} rounds".format(self.cooldown))

    def attack(self, enemy):
        random_dmg = random.randint(1, self.dmg)
        amount = random_dmg + self.dmg_bonus
        enemy.take_damage(amount)
        return amount

    def round_up(self):
        self.dmg_bonus += 1
        super().round_up()

    def stage_up(self):
        self.dmg_bonus = 0
        self.stage_used = False
        super().stage_up()
        self.cooldown = Procrastinator.COOLDOWN_LIMIT

    @staticmethod
    def character_info():
        return '''Procrastinator -> 
        Stats: {}HP and {}DMG.
        Passive: Adds +1 DMG each round. Resets at the beginning of each stage
        Skill: DMG + DMG roll + stage level to all the enemies
        after the third round of each stage and once per stage
        '''.format(Procrastinator.HP, Procrastinator.DMG)
