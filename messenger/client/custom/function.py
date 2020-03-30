"""Module with function for send_message and get_message."""

import json
import sys
sys.path.append('../')
from client.custom.variables import MAX_DATA, ENCODING
from client.custom.decorators import Log


@Log()
def get_message(client_server):
    """
    The function of receive messages from remote computers. Receives JSON
    messages, decode the received message and verifies that the dictionary
    is received.\n
    :param obj client_server: server socket.
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
    The function takes a message dictionary, serializes it in json and sends.\n
    :param str sock: transmission socket.
    :param dict message: message to send.
    """
    json_message = json.dumps(message)
    encode_message = json_message.encode(ENCODING)
    sock.send(encode_message)
