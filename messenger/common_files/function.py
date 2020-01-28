"""Функции для использования server.py и client.py"""
import json
from common_files.variables import MAX_DATA, ENCODING
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
        raise ValueError
    raise ValueError


@Log()
def send_message(recipient, message):
    """Принимает словарь message, сериальзует его в json и отправляет"""
    json_message = json.dumps(message)
    encode_message = json_message.encode(ENCODING)
    recipient.send(encode_message)
