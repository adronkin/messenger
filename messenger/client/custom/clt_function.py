"""Module with functions for the client module"""

import json
import sys
sys.path.append('../')
from custom.clt_variables import MAX_DATA, ENCODING
from custom.decorators import Log


@Log()
def get_message(client_server):
    """
    The function accepts the message in bytes and returns a dictionary.
    :param client_server: server socket.
    :return:
    """
    data = client_server.recv(MAX_DATA)
    decoded_data = data.decode(ENCODING)
    dict_data = json.loads(decoded_data)
    if isinstance(dict_data, dict):
        return dict_data
    raise TypeError


@Log()
def send_message(sock, message):
    """
    The function takes a message dictionary, serializes it in json and sends.
    :param {str} sock: transmission socket.
    :param {dict} message: message to send.
    :return:
    """
    json_message = json.dumps(message)
    encode_message = json_message.encode(ENCODING)
    sock.send(encode_message)
