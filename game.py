import random
import characters
import enemies


class Player:
    def __init__(self, number, name, client_socket, client_address):
        self.number = number
        self.character = None
        self.name = name
        self.client_socket = client_socket
        self.client_address = client_address

    def add_character(self, character):
        self.character = character


class Game:
    AVAILABLE_CHARACTERS = [characters.Bookworm, characters.Worker, characters.Procrastinator, characters.Whatsapper]
    AVAILABLE_ENEMIES = [enemies.PartialExam, enemies.FinalExam, enemies.TheoreticalClass, enemies.Teacher]

    NUMBER_OF_CHARACTERS = 4
    NUMBER_OF_ENEMIES = 4

    def __init__(self, starter_player, number_of_players, number_of_stages):
        self.starter_player = starter_player
        self.number_of_stages = number_of_stages
        self.number_of_players = number_of_players
        self.current_stage = 1
        self.current_round = 1
        self.finished = False
        self.players = []
        self.dead_players = []
        self.enemies = []
        self.current_number_of_players = 0
        self.player_turn = 0

    def __str__(self):
        info = "------ GAME ------\n"
        info += "Total players: {}\n".format(self.current_number_of_players)
        info += "Dead players: {}\n".format(len(self.dead_players))
        info += "Current stage: {}\n".format(self.current_stage)
        info += "Total stages: {}\n".format(self.number_of_stages)
        info += "------------------\n"
        return info

    def all_players_stage_up(self):
        for player in self.players:
            player.character.stage_up()

        for player in self.dead_players:
            player.character.stage_up()

    def all_players_round_up(self):
        for player in self.players:
            player.character.round_up()

        for player in self.dead_players:
            player.character.round_up()

    def is_full(self):
        return self.current_number_of_players == self.number_of_players

    def choose_random_enemies(self):
        for _ in range(Game.NUMBER_OF_ENEMIES):
            is_valid_enemy = False
            while not is_valid_enemy:
                enemy = random.choice(Game.AVAILABLE_ENEMIES)
                if enemy != enemies.FinalExam or (enemy == enemies.FinalExam and self.current_stage >= 4):
                    self.enemies.append(enemy())
                    is_valid_enemy = True

    def add_player(self, name, client_socket, client_address):
        player = Player(self.number_of_players + 1, name, client_socket, client_address)
        self.players.append(player)
        self.current_number_of_players += 1
        if self.is_full():
            self.choose_random_enemies()

    def add_character_to_player(self, client_address, option):
        for player in self.players:
            if client_address == player.client_address:
                player.add_character(Game.AVAILABLE_CHARACTERS[option - 1]())
                break

    def obtain_player(self, client_address):
        for player in self.players:
            if client_address == player.client_address:
                return player
        return None

    def contains_player(self, client_address):
        for player in self.alive_and_dead_players():
            if client_address == player.client_address:
                return True
        return False

    @staticmethod
    def available_characters():
        text = "\t\t\t--- AVAILABLE CHARACTERS ---\n"
        text += "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
        for index, character in enumerate(Game.AVAILABLE_CHARACTERS):
            text += "{} .- {}\n".format(index + 1, character.character_info())
        text += "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
        return text

    def all_enemies_are_dead(self):
        return len(self.enemies) == 0

    def all_players_are_dead(self):
        return len(self.players) == 0

    def stage_info(self):
        info = "\t\t\t***********************\n"
        info += "\t\t\t*       STAGE {}       *\n".format(self.current_stage)
        info += "\t\t\t***********************\n"
        info += self.enemies_info()
        return info

    def enemies_info(self):
        info = "\t\t\t--- CURRENT ENEMIES ---\n"
        info += "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
        for enemy in self.enemies:
            info += "{}\n".format(enemy.enemy_info())
        info += "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
        return info

    def first_stage_info(self):
        info = "\t--- A game with {} stages will be set up for {} players ---\n".format(self.number_of_stages,
                                                                                        self.number_of_players)
        info += self.stage_info()
        return info

    def current_player_turn(self):
        result = self.players[self.player_turn]
        return result

    def current_player_turn_info(self):
        current_player = self.current_player_turn()
        character_name = current_player.character.__class__.__name__
        return "{} ({}) - What are you going to do? ".format(character_name, current_player.name)

    def last_player_turn(self):
        result = self.player_turn == len(self.players) - 1
        return result

    def change_turn(self):
        if self.last_player_turn():
            self.player_turn = 0
        else:
            self.player_turn += 1
        return self.player_turn

    def player_attack(self, player):
        character_name = player.character.__class__.__name__
        enemy = random.choice(self.enemies)
        dmg = player.character.attack(enemy)
        enemy_name = enemy.__class__.__name__
        attack_info = "{} ({}) did {} damage to {}. {} has {} hp left.\n".format(character_name, player.name,
                                                                                 dmg, enemy_name, enemy_name,
                                                                                 enemy.hp)
        if not enemy.alive():
            attack_info += "{} has died.\n".format(enemy_name)
            self.enemies.remove(enemy)
        return attack_info

    def bookworm_skill(self, player):
        if len(self.dead_players) == 0:
            skill_info = "There are no players dead. You can not use your skill. You attack automatically.\n"
            skill_info += self.player_attack(player)
        else:
            character_name = player.character.__class__.__name__
            player_to_revive = random.choice(self.dead_players)
            character_to_revive_name = player_to_revive.character.__class__.__name__
            player.character.skill(player_to_revive.character)
            self.dead_players.remove(player_to_revive)
            self.players.append(player_to_revive)
            skill_info = "{} ({}) used his/her skill. {} ({}) revived.\n".format(character_name, player.name,
                                                                                 character_to_revive_name,
                                                                                 player_to_revive.name)
        return skill_info

    def worker_skill(self, player):
        character_name = player.character.__class__.__name__
        enemy = random.choice(self.enemies)
        dmg = player.character.skill(enemy)
        enemy_name = enemy.__class__.__name__
        skill_info = "{} ({}) used his/her skill. {} did {} damage to {}. {} has {} hp left.\n".format(character_name,
                                                                                                       player.name,
                                                                                                       character_name,
                                                                                                       dmg, enemy_name,
                                                                                                       enemy_name,
                                                                                                       enemy.hp)
        if not enemy.alive():
            skill_info += "{} has died".format(enemy_name)
            self.enemies.remove(enemy)
        return skill_info

    def procrastinator_skill(self, player):
        character_name = player.character.__class__.__name__
        dmg = player.character.skill(self.enemies)
        skill_info = "{} ({}) used his/her skill.\n".format(character_name, player.name)
        dead_attacked_enemies = []
        for enemy in self.enemies:
            enemy_name = enemy.__class__.__name__
            skill_info += "{} did {} damage to {}. {} has {} hp left.\n".format(character_name, dmg, enemy_name,
                                                                                enemy_name, enemy.hp)
            if not enemy.alive():
                dead_attacked_enemies.append(enemy)
        for enemy in dead_attacked_enemies:
            enemy_name = enemy.__class__.__name__
            skill_info += "{} has died".format(enemy_name)
            self.enemies.remove(enemy)
        return skill_info

    def whatsapper_skill(self, player):
        skill_info = ""
        character_name = player.character.__class__.__name__
        player_to_heal = random.choice(self.players)
        character_to_heal_name = player_to_heal.character.__class__.__name__
        if player_to_heal.character.alive():
            hp = player.character.skill(player_to_heal.character)
            skill_info = "{} ({}) used his/her skill. {} ({}) received {} hp. Now he/she has {} hp.\n".\
                format(character_name, player.name, character_to_heal_name, player_to_heal.name, hp,
                       player_to_heal.character.hp)
        return skill_info

    def player_skill(self, player):
        try:
            character_name = player.character.__class__.__name__
            if character_name == "Bookworm":
                skill_info = self.bookworm_skill(player)
            elif character_name == "Worker":
                skill_info = self.worker_skill(player)
            elif character_name == "Procrastinator":
                skill_info = self.procrastinator_skill(player)
            else:
                skill_info = self.whatsapper_skill(player)
        except characters.CooldownError as err:
            skill_info = "{}. You attack automatically.\n".format(err)
            skill_info += self.player_attack(player)
        return skill_info

    def enemies_turn(self):
        attack_info = "\n"
        attack_info += "\t\t\t--- ENEMIES TURN ---\n"
        attack_info += "***************************************************************************\n"
        for enemy in self.enemies:
            player = random.choice(self.players)
            enemy_name = enemy.__class__.__name__
            character_name = player.character.__class__.__name__
            dmg = enemy.attack(player.character)
            attack_info += "{} did {} damage to {} ({}). {} has {} hp left.\n".format(enemy_name, dmg, character_name,
                                                                                      player.name, character_name,
                                                                                      player.character.hp)
            if not player.character.alive():
                self.players.remove(player)
                self.dead_players.append(player)
                attack_info += "{} ({}) has died.\n".format(character_name, player.name)
            if self.all_players_are_dead():
                self.finished = True
                break
        attack_info += "***************************************************************************\n"
        self.player_turn = 0
        return attack_info

    def player_action(self, client_address, command):
        player = self.obtain_player(client_address)
        action = ""
        if command == 'a':
            action += self.player_attack(player)
        elif command == 's':
            action += self.player_skill(player)
        if self.all_enemies_are_dead():
            if self.current_stage == self.number_of_stages:
                self.finished = True
            else:
                self.change_turn()
                self.current_stage += 1
                self.current_round = 1
                self.all_players_stage_up()
                self.choose_random_enemies()
                action += self.stage_info()
        else:
            if self.last_player_turn():
                action += self.enemies_turn()
                if not self.all_players_are_dead():

                    self.all_players_round_up()
            else:
                self.change_turn()
        return action

    def game_finished(self):
        return self.finished

    def info(self):
        return "Players: {}/{}".format(self.current_number_of_players, self.number_of_players)

    def alive_and_dead_players(self):
        return self.players + self.dead_players

    def remove_player(self, player):
        if player in self.players:
            self.players.remove(player)
        if player in self.dead_players:
            self.dead_players.remove(player)

    def finish(self):
        if self.all_players_are_dead():
            info = "\t*****************************************\n"
            info += "\tAll players have been defeated. Try again\n"
            info += "\t*****************************************\n"
        else:
            info = "\t***************************************************\n"
            info += "\tAll the stages have been cleared. You won the game!\n"
            info += "\t***************************************************\n"
        return info
