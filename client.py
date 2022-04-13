import socket
import protocols
import json
import getopt
import sys


class Client:
    MIN_PLAYERS = 1
    MAX_PLAYERS = 4
    MIN_STAGES = 1
    MAX_STAGES = 10
    NO_NAME = ""
    DEFAULT_IP = '127.0.0.1'
    DEFAULT_PORT = 8080

    def __init__(self, number_of_players, number_of_stages, player_name, server_hostname, server_port):
        self.number_of_players = number_of_players
        self.number_of_stages = number_of_stages
        self.player_name = player_name
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.connect((server_hostname, server_port))
        self.end = False

    def send_join_message(self):
        message = {"header": protocols.JOIN, "name": self.player_name}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())

    def control_welcome_message(self, message):
        menu = message["menu"]
        options_range = message["options range"]
        print("{}".format(menu))
        print("options range: {}".format(options_range))
        self.send_server_option()

    @staticmethod
    def choose_options():
        correct_input = False
        option = None
        while not correct_input:
            try:
                user_input = int(input("Choose an option: "))
                if user_input == 1:
                    option = 1
                    correct_input = True
                    print("You created a new game")
                elif user_input == 2:
                    option = 2
                    correct_input = True
                elif user_input == 3:
                    option = 3
                    correct_input = True
                    print("You exit from the server")
                else:
                    print("This option is not valid. You must choose 1, 2 or 3")
            except ValueError:
                print("This option is not valid. You must choose 1, 2 or 3")
        return option

    def send_server_option(self):
        message = {"header": protocols.SEND_SERVER_OPTION, "option": self.choose_options(),
                   "number of players": self.number_of_players, "number of stages": self.number_of_stages}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())

    def control_choose_character(self, message):
        menu = message["menu"]
        options_range = message["options range"]
        print("{}".format(menu))
        print("options range: {}".format(options_range))
        self.send_character()

    @staticmethod
    def choose_characters():
        correct_input = False
        option = None
        while not correct_input:
            try:
                user_input = int(input("Choose one character to play: "))
                if user_input == 1:
                    correct_input = True
                    option = 1
                    print("Your character is Bookworm")
                elif user_input == 2:
                    correct_input = True
                    option = 2
                    print("Your character is Worker")
                elif user_input == 3:
                    correct_input = True
                    option = 3
                    print("Your character is Procrastinator")
                elif user_input == 4:
                    correct_input = True
                    option = 4
                    print("Your character is Whatsapper")
                else:
                    print("This is an invalid option")
            except ValueError:
                print("This is an invalid option")
        return option

    def send_character(self):
        message = {"header": protocols.SEND_CHARACTER, "option": self.choose_characters()}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())

    def control_send_games(self, message):
        available_games = message["games list"]
        games_id = message["games id"]
        print("\t\t\t--- SERVER GAME LIST ---")
        print("{}".format(available_games))
        print("options range: {}".format(games_id))
        self.send_game_choice()

    def choose_game(self):
        try:
            user_input = int(input("Choose a game: "))
            return user_input
        except ValueError:
            print("This option is not valid. You will exit from the server.")
            self.end = True

    def send_game_choice(self):
        message = {"header": protocols.SEND_GAME_CHOICE, "game id": self.choose_game()}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())

    def control_send_valid_game(self, message):
        joined = message["joined"]
        if joined:
            print("joined: {}".format(joined))
        if not joined:
            print("The game you tried to join is full.")
            self.end = True

    @staticmethod
    def control_server_message(message):
        msg = message["message"]
        print(msg)

    def control_your_turn_message(self, message):
        msg = message["message"]
        options_range = message["options range"]
        print("{}".format(msg))
        print("options range: {}".format(options_range))
        self.send_character_command()

    @staticmethod
    def choose_command():
        correct_input = False
        user_input = ""
        while not correct_input:
            user_input = input()
            if user_input == 'a':
                correct_input = True
            elif user_input == 's':
                correct_input = True
            else:
                print("The character is not valid. Please, enter 'a' to attack or 's' to use your skill")
        return user_input

    def send_character_command(self):
        message = {"header": protocols.SEND_CHARACTER_COMMAND, "command": self.choose_command()}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())

    def control_send_end_game_message(self, message):
        win = message["win"]
        if win:
            print("***************************************************************************")
            print("\t\tAll enemies have been defeated. You won!")
            print("***************************************************************************")
        else:
            print("***************************************************************************")
            print("\t\tAll players have been defeated. Try again")
            print("***************************************************************************")
        self.end = True

    def control_send_dc_server(self, message):
        reason = message["reason"]
        print(reason)
        self.end = True

    def send_dc_me(self):
        message = {"header": protocols.SEND_DC_ME}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())

    def control_message(self, message):
        header = message["header"]
        print("{} message received".format(header))
        if header == protocols.WELCOME:
            self.control_welcome_message(message)
        elif header == protocols.CHOOSE_CHARACTER:
            self.control_choose_character(message)
        elif header == protocols.SEND_GAMES:
            self.control_send_games(message)
        elif header == protocols.SEND_VALID_GAME:
            self.control_send_valid_game(message)
        elif header == protocols.SERVER_MSG:
            self.control_server_message(message)
        elif header == protocols.YOUR_TURN:
            self.control_your_turn_message(message)
        elif header == protocols.SEND_END_GAME:
            self.control_send_end_game_message(message)
        elif header == protocols.SEND_DC_SERVER:
            self.control_send_dc_server(message)
        else:
            print("Invalid message received")

    def start(self):
        name = self.player_name
        message = {"header": protocols.JOIN, "name": name}
        protocols.send_one_message(self.my_socket, json.dumps(message).encode())
        while not self.end:
            try:
                buffer = protocols.recv_one_message(self.my_socket)
                message = json.loads(buffer.decode())
                self.control_message(message)
            except TypeError:
                self.end = True
                print("Server was disconnected")
            except KeyboardInterrupt:
                self.end = True
                self.send_dc_me()
        self.my_socket.close()


class ArgsError(Exception):
    def __init__(self, msg):
        super().__init__("Error: {}".format(msg))


def parse_args():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "p:s:n:i:o:", ["players=", "stages=", "name=", "ip=", "port="])
    except getopt.GetoptError:
        raise ArgsError("You enter wrong arguments. Finishing program")

    number_of_players = Client.MIN_PLAYERS
    number_of_stages = Client.MIN_STAGES
    ip_address = Client.DEFAULT_IP
    port_address = Client.DEFAULT_PORT
    player_name = Client.NO_NAME
    try:
        for o, a in opts:
            if o in ("-p", "--players"):
                number_of_players = int(a)
            if o in ("-s", "--stages"):
                number_of_stages = int(a)
            if o in ("-n", "--name"):
                player_name = str(a)
            if o in ("-i", "--ip"):
                ip_address = str(a)
            if o in ("-o", "--port"):
                port_address = int(a)
    except ValueError:
        raise ArgsError("Type of arguments is wrong. Finishing program")
    return number_of_players, number_of_stages, player_name, ip_address, port_address


if __name__ == '__main__':
    try:
        players, stages, nick, ip, port = parse_args()
        if (players < Client.MIN_PLAYERS or players > Client.MAX_PLAYERS) and \
                (Client.MIN_STAGES <= stages <= Client.MAX_STAGES):
            raise ArgsError("The number of players must be between 1 and 4. Finishing program")
        elif (Client.MIN_PLAYERS <= players <= Client.MAX_PLAYERS) and \
                (stages < Client.MIN_STAGES or stages > Client.MAX_STAGES):
            raise ArgsError("The number of stages must be between 1 and 10. Finishing program")
        elif (players < Client.MIN_PLAYERS or players > Client.MAX_PLAYERS) and \
                (stages < Client.MIN_STAGES or stages > Client.MAX_STAGES):
            raise ArgsError("The number of players must be between 1 and 4. "
                            "The number of stages must be between 1 and 10. Finishing program")
        elif nick == Client.NO_NAME:
            raise ArgsError("You must introduce a name for the player. Finishing program")
        client = Client(players, stages, nick, ip, port)
        client.start()
    except ArgsError as err:
        print(err)
    except KeyboardInterrupt:
        print("Client closed by CTRL+C")
    except ConnectionRefusedError:
        print("This server is not connected. Try again")
