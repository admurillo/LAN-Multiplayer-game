import struct


JOIN = "JOIN"
WELCOME = "WELCOME"
SEND_SERVER_OPTION = "SEND_SERVER_OPTION"
CHOOSE_CHARACTER = "CHOOSE_CHARACTER"
SEND_CHARACTER = "SEND_CHARACTER"
SERVER_MSG = "SERVER_MSG"
YOUR_TURN = "YOUR_TURN"
SEND_CHARACTER_COMMAND = "SEND_CHARACTER_COMMAND"
SEND_GAMES = "SEND_GAMES"
SEND_GAME_CHOICE = "SEND_GAME_CHOICE"
SEND_VALID_GAME = "SEND_VALID_GAME"
SEND_END_GAME = "SEND_END_GAME"
SEND_DC_ME = "SEND_DC_ME"
SEND_DC_SERVER = "SEND_DC_SERVER"
HEADER = [JOIN, WELCOME, SEND_SERVER_OPTION, CHOOSE_CHARACTER, SEND_CHARACTER, SERVER_MSG, YOUR_TURN,
          SEND_CHARACTER_COMMAND, SEND_GAMES, SEND_GAME_CHOICE, SEND_VALID_GAME, SEND_END_GAME, SEND_DC_ME,
          SEND_DC_SERVER]


def recv_all(recipient, length):
    buffer = b''
    while length != 0:
        buffer_aux = recipient.recv(length)
        if not buffer_aux:
            return None
        buffer = buffer + buffer_aux
        length = length - len(buffer_aux)
    return buffer


def send_one_message(recipient, encoded_data):
    try:
        length = len(encoded_data)
        header = struct.pack("!I", length)
        recipient.sendall(header)
        recipient.sendall(encoded_data)
    except OSError:
        return None


def recv_one_message(recipient):
    header_buffer = recv_all(recipient, 4)
    header = struct.unpack("!I", header_buffer)
    length = header[0]
    return recv_all(recipient, length)
