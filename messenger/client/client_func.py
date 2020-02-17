"""Функции для использования server.py и client.py"""

import sys
from time import time
from logging import getLogger
sys.path.append('../')
import logs.client_log_config
from decorators import Log
from errors import ServerError, ReqFieldMissingError
from common_files.variables import ACTION, PRESENCE, TIME, USER, RESPONSE, ERROR

# Инициализируем логгера
LOGGER = getLogger('client_logger')


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
