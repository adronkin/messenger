"""Программа-клиент"""

import re
import sys
import time
from logging import getLogger
from socket import socket, SOCK_STREAM, AF_INET
import logs.client_log_config
from decorators import Log
from common_files.function import send_message, get_message
from common_files.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX, ACTION, \
    PRESENCE, TIME, USER, RESPONSE, ERROR

# Инициализируем логгера
LOGGER = getLogger('client_logger')


@Log()
def confirm_presence(user_name='Guest'):
    """Функция генерирует словарь для отправки сообщения о присутствии пользователя"""
    message = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: user_name
    }
    LOGGER.info(f'Сгенерировано сообщение для отправки на сервер - {message}')
    return message


@Log()
def receive_message(msg):
    """Функция парсит ответ от сервера"""
    LOGGER.debug(f'Обработка сообщения от сервера {msg}')
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            LOGGER.info('Сообщение корректно обработано. Response 200: OK')
            return 'Response 200: OK'
        elif msg[RESPONSE] == 400:
            LOGGER.error(f'Сервер не смог отбратать клиентский запрос. '
                         f'Получен отвен "Response 400: {msg[ERROR]}"')
            return f'Response 400: {msg[ERROR]}'
        LOGGER.error(f'Получено некорректное сообщение от сервера')
        return 'Server error'
    raise ValueError


def main():
    """Код запуска client"""
    sys_args = sys.argv
    if len(sys_args) == 3:
        if sys_args[2].isdigit() and 1024 < int(sys_args[2]) < 65535 and\
                re.match(IP_REGEX, sys_args[1]):
            server_ip, server_port = sys_args[1], int(sys_args[2])
        else:
            LOGGER.critical(f'Попытка запуска клиента с некорректными параметрами. '
                            f'Пример корректного ввода - "имя_скрипта.py <ip_address> <port>. '
                            f'Значение port от 1024 до 65535')
            sys.exit(1)
    elif len(sys_args) == 1:
        server_ip, server_port = DEFAULT_IP, DEFAULT_PORT
    try:
        # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
        client_sock = socket(AF_INET, SOCK_STREAM)
        # Подключаемся к серверу
        client_sock.connect((server_ip, server_port))
        LOGGER.info(f'Установлено соединение с сервером {server_ip}:{server_ip}')
        msg = confirm_presence()
        LOGGER.info(f'Сообщение отправлено на сервер {server_ip}:{server_ip}')
        send_message(client_sock, msg)
        answer = receive_message(get_message(client_sock))
        print(answer)
    except ValueError:
        LOGGER.error('Не удалось декодировать сообщение от сервера')
    except ConnectionRefusedError:
        LOGGER.critical('Не удалось подключиться к серверу {server_ip}:{server_ip}')


if __name__ == '__main__':
    main()
