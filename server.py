from threading import Thread
import socket
import os
import signal
import json
import getopt
import sys
import protocols
from game import Game
from double_linked_list import DoubleLinkedList
from double_linked_list import Cursor


class ClientController(Thread):
    def __init__(self, client_socket, client_address, active_games, finished_games):
        Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.end = False
        self.active_games = active_games
        self.finished_games = finished_games
        self.name = ""

    def control_join_message(self, message):
        self.name = message["name"]
        print("(WELCOME) {} joined the server".format(self.name))
        self.send_welcome_message()

    def send_welcome_message(self):
        menu = '''\t*****************************
        *   Welcome to the server:  *
        *   1.-Create game          *
        *   2.-Join game            *
        *   3.-Exit                 *
        *****************************'''
        options_range = [1, 2, 3]
        message = {"header": protocols.WELCOME, "menu": menu, "options range": options_range}
        protocols.send_one_message(self.client_socket, json.dumps(message).encode())

    def control_send_server_option_message(self, message):
        option = message["option"]
        number_of_players = message["number of players"]
        number_of_stages = message["number of stages"]
        if option == 1:
            print("(CREATE) {} created a game".format(self.name))
            game = Game(self.name, number_of_players, number_of_stages)
            game.add_player(self.name, self.client_socket, self.client_address)
            self.active_games.add_last(game)
            self.send_choose_character()
        elif option == 2:
            self.send_games()
        else:
            print("(EXIT) {} disconnected".format(self.name))
            reason = "{} disconnected.".format(self.name)
            message = {"header": protocols.SEND_DC_SERVER, "reason": reason}
            protocols.send_one_message(self.client_socket, json.dumps(message).encode())
            self.end = True

    def send_choose_character(self):
        menu = Game.available_characters()
        options_range = [1, 2, 3, 4]
        message = {"header": protocols.CHOOSE_CHARACTER, "menu": menu, "options range": options_range}
        protocols.send_one_message(self.client_socket, json.dumps(message).encode())

    def available_games(self):
        games_list = []
        cursor = Cursor(self.active_games)
        cursor.first()
        while cursor.has_next():
            game = cursor.get()
            if not game.is_full():
                games_list.append(game)
            cursor.next()
        return games_list

    def available_games_id(self):
        ids = []
        for game in self.available_games():
            ids.append(self.available_games().index(game) + 1)
        return ids

    def send_games(self):
        games_list = "---------------------------------------------------------------------------\n"
        for game in self.available_games():
            games_list += "\t\t(Game {} ({}'s game)) - {}\n".format(self.available_games().index(game) + 1,
                                                                    game.starter_player, game.info())
        games_list += "---------------------------------------------------------------------------\n"
        games_id = self.available_games_id()
        message = {"header": protocols.SEND_GAMES, "games list": games_list, "games id": games_id}
        protocols.send_one_message(self.client_socket, json.dumps(message).encode())

    def obtain_game(self):
        cursor = Cursor(self.active_games)
        cursor.first()
        found = False
        game = None
        while not found and cursor.has_next():
            game = cursor.get()
            if game.contains_player(self.client_address):
                found = True
            cursor.next()
        if found:
            return game
        return None

    def obtain_game_by_id(self):
        cursor = Cursor(self.active_games)
        cursor.first()
        found = False
        game = None
        while cursor.has_next():
            game = cursor.get()
            if game.contains_player(self.client_address):
                found = True
            cursor.next()
        if found:
            return game
        return None

    def send_dc_server(self):
        game = self.obtain_game()
        for player in game.alive_and_dead_players():
            reason = "{} disconnected. The game can not continue".format(self.name)
            message = {"header": protocols.SEND_DC_SERVER, "reason": reason}
            protocols.send_one_message(player.client_socket, json.dumps(message).encode())

    def control_send_character_message(self, message):
        option = message["option"]
        game = self.obtain_game()
        print(game.starter_player)
        game.add_character_to_player(self.client_address, option)
        if game.is_full():
            print("(START) {} started a game".format(game.starter_player))
            info = game.first_stage_info()
            message = {"header": protocols.SERVER_MSG, "message": info}
            for player in game.alive_and_dead_players():
                protocols.send_one_message(player.client_socket, json.dumps(message).encode())
            self.send_your_turn_message()
        else:
            msg = "You must wait for more players: {}".format(game.info())
            message = {"header": protocols.SERVER_MSG, "message": msg}
            for player in game.alive_and_dead_players():
                protocols.send_one_message(player.client_socket, json.dumps(message).encode())

    def send_your_turn_message(self):
        game = self.obtain_game()
        current_player = game.current_player_turn()
        msg = game.current_player_turn_info()
        options_range = ['a', 's']
        message = {"header": protocols.YOUR_TURN, "message": msg, "options range": options_range}
        protocols.send_one_message(current_player.client_socket, json.dumps(message).encode())

    def control_send_character_command(self, message):
        command = message["command"]
        game = self.obtain_game()
        action = game.player_action(self.client_address, command)
        for player in game.alive_and_dead_players():
            message = {"header": protocols.SERVER_MSG, "message": action}
            protocols.send_one_message(player.client_socket, json.dumps(message).encode())
        if game.game_finished():
            self.send_end_game_message()
        else:
            self.send_your_turn_message()

    def send_end_game_message(self):
        game = self.obtain_game()
        print("(ENDGAME) {}'s game ended".format(game.starter_player))
        win = None
        if game.all_enemies_are_dead():
            win = True
        elif game.all_players_are_dead():
            win = False
        for player in game.alive_and_dead_players():
            message = {"header": protocols.SEND_END_GAME, "win": win}
            protocols.send_one_message(player.client_socket, json.dumps(message).encode())
        self.end = True
        self.active_games.delete(game)
        self.finished_games.add_last(game)

    def control_send_game_choice_message(self, message):
        game_id = message["game id"]
        games_for_join = self.available_games()
        if 1 <= game_id <= len(games_for_join):
            game = games_for_join[game_id - 1]
            if game.is_full():
                joined = False
                message = {"header": protocols.SEND_VALID_GAME, "joined": joined}
                protocols.send_one_message(self.client_socket, json.dumps(message).encode())
            else:
                game.add_player(self.name, self.client_socket, self.client_address)
                print("(JOIN) {} joined {}'s game".format(self.name, game.starter_player))
                joined = True
                message = {"header": protocols.SEND_VALID_GAME, "joined": joined}
                protocols.send_one_message(self.client_socket, json.dumps(message).encode())
                self.send_choose_character()
        else:
            msg = "This game does not exist."
            message = {"header": protocols.SERVER_MSG, "message": msg}
            protocols.send_one_message(self.client_socket, json.dumps(message).encode())
            self.send_games()

    def control_send_dc_me(self):
        game = self.obtain_game()
        print("(EXIT) {} disconnected".format(self.name))
        reason = "{} disconnected. The game can not continue".format(self.name)
        message = {"header": protocols.SEND_DC_SERVER, "reason": reason}
        if game is not None:
            for player in game.alive_and_dead_players():
                if player.client_address != self.client_address:
                    print("(DC) {} was disconnected".format(player.name))
                    protocols.send_one_message(player.client_socket, json.dumps(message).encode())
        self.end = True
        self.active_games.delete(game)
        self.finished_games.add_last(game)

    def control_message(self, message):
        header = message["header"]
        print("{} message received".format(header))
        if header == protocols.JOIN:
            self.control_join_message(message)
        elif header == protocols.SEND_SERVER_OPTION:
            self.control_send_server_option_message(message)
        elif header == protocols.SEND_CHARACTER:
            self.control_send_character_message(message)
        elif header == protocols.SEND_CHARACTER_COMMAND:
            self.control_send_character_command(message)
        elif header == protocols.SEND_GAME_CHOICE:
            self.control_send_game_choice_message(message)
        elif header == protocols.SEND_DC_ME:
            self.control_send_dc_me()
        else:
            print("ERROR: Invalid message received")

    def run(self):
        ip, port = self.client_address
        print("Connection established with {}:{}".format(ip, port))
        while not self.end:
            try:
                buffer = protocols.recv_one_message(self.client_socket)
                message = json.loads(buffer.decode())
                self.control_message(message)
            except TypeError:
                self.end = True
            except AttributeError:
                self.end = True
        self.client_socket.close()


class Server(Thread):
    DEFAULT_PORT = 8080

    def __init__(self, port):
        Thread.__init__(self)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.bind((socket.gethostname(), port))
        self.my_socket.listen()
        self.active_games = DoubleLinkedList()
        self.finished_games = DoubleLinkedList()

    def run(self):
        ip, port = self.my_socket.getsockname()
        print("Server started at {}:{}".format(ip, port))
        while True:
            client_socket, client_address = self.my_socket.accept()
            client_controller = ClientController(client_socket, client_address, self.active_games, self.finished_games)
            client_controller.start()

    @staticmethod
    def send_dc_server(recipient):
        reason = "The server has been shut down by the admin. You have been disconnected"
        message = {"header": protocols.SEND_DC_SERVER, "reason": reason}
        protocols.send_one_message(recipient, json.dumps(message).encode())

    def shutdown(self):
        cursor = Cursor(self.active_games)
        cursor.first()
        while cursor.has_next():
            game = cursor.get()
            for player in game.alive_and_dead_players():
                Server.send_dc_server(player.client_socket)
            cursor.next()

    def ngames(self):
        print("Active games: {}".format(self.active_games.size))
        print("Finished games: {}".format(self.finished_games.size))

    def gamesinfo(self):
        self.active_games.print_linked_list_backwards_v2()


class ArgsError(Exception):
    def __init__(self, msg):
        super().__init__("Error: {}".format(msg))


def parse_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:", "port=")
    except getopt.GetoptError:
        raise ArgsError("You enter wrong arguments. Finishing program")

    port_address = Server.DEFAULT_PORT
    try:
        for o, a in opts:
            if o in ("-o", "--port"):
                port_address = int(a)
    except ValueError:
        raise ArgsError("Type of arguments is wrong. Finishing program")
    return port_address


if __name__ == '__main__':
    pid = os.getpid()
    try:
        port = parse_args()
        server = Server(port)
        server.start()
        end = False
        while not end:
            command = input()
            if command == 'shutdown':
                server.shutdown()
                end = True
            elif command == 'ngames':
                server.ngames()
            elif command == 'gamesinfo':
                server.gamesinfo()
            else:
                print("Invalid command")
        os.kill(pid, signal.SIGKILL)
    except ArgsError as err:
        print(err)
    except KeyboardInterrupt:
        print("Server closed by CTRL+C")
        os.kill(pid, signal.SIGTERM)
