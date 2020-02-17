"""Функции для использования server.py и client.py"""

import json
import sys
sys.path.append('../')
from common_files.variables import MAX_DATA, ENCODING
from errors import IncorrectDataReceivedError, NonDictInputError
from decorators import Log


@Log()
def get_message(client_server):
    """Функция принимает сообщение в байтах и возвращает словарь.
    Если преобразование неудалось, то вызывает исключение ValueError."""
    data = client_server.recv(MAX_DATA)
    # Проверяем, что data в байтах
    if isinstance(data, bytes):
        decoded_data = data.decode(ENCODING)
        dict_data = json.loads(decoded_data)
        if isinstance(dict_data, dict):
            return dict_data
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@Log()
def send_message(recipient, message):
    """Принимает словарь message, сериальзует его в json и отправляет"""
    if not isinstance(message, dict):
        raise NonDictInputError
    json_message = json.dumps(message)
    encode_message = json_message.encode(ENCODING)
    recipient.send(encode_message)
