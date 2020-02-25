"""Функции для использования server.py и client.py"""

import sys
import json
from time import time
from logging import getLogger
from clt_variables import ACTION, PRESENCE, TIME, USER, RESPONSE, ERROR, MAX_DATA, ENCODING
sys.path.append('../')
import logs.client_log_config
from decorators import Log
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError, NonDictInputError

# Инициализируем логгера
LOGGER = getLogger('client_logger')


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


@Log()
def confirm_presence(username):
    """
    Функция генерирует словарь для отправки сообщения о присутствии пользователя
    :param {str} username: имя пользователя-клиента.
    :return {dict}: словарь для подтверждения присутствия пользователя.
    """
    message = {
        ACTION: PRESENCE,
        TIME: time(),
        USER: username
    }
    LOGGER.info(f'Сгенерировано {PRESENCE} сообщение для пользователя {username}')
    return message


@Log()
def receive_message(message):
    """
    Функция парсит ответ от сервера
    :param {dict} message: сообщение от ервера.
    :return {str}: response 200.
    """
    LOGGER.debug(f'Обработка сообщения от сервера {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            LOGGER.info('Сообщение корректно обработано. Response 200: OK')
            return 'Response 200: OK'
        elif message[RESPONSE] == 400 and ERROR in message:
            LOGGER.error(f'Сервер не смог отбратать клиентский запрос. '
                         f'Получен отвен "Response 400: {message[ERROR]}".')
            raise ServerError(f'400: {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@Log()
def add_contact_to_server(sock, username, contact):
    pass
