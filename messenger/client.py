"""Программа-клиент"""

import re
import sys
import time
from socket import socket, SOCK_STREAM, AF_INET
from lesson_3.common_files.function import send_message, get_message
from lesson_3.common_files.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX, ACTION, \
    PRESENCE, TIME, USER, RESPONSE, ERROR


def identify_ip_port():
    """Если в командной строке введены порт и IP-адресс, то привязывает к ним сокет"""
    sys_args = sys.argv
    if len(sys_args) == 1:
        # Подключаемся к серверу
        return CLIENT_SOCK.connect((DEFAULT_IP, DEFAULT_PORT))
    if len(sys_args) == 3:
        if sys_args[2].isdigit() and 1024 < int(sys_args[2]) < 65535 and\
                re.match(IP_REGEX, sys_args[1]):
            return CLIENT_SOCK.connect((sys_args[1], int(sys_args[2])))
    print(f'Параметры введены некорректно, пример корректного ввода -'
          f' "имя_скрипта.py <ip_address> <port>.\n'
          f'Будут использованы стандартные параметры - {DEFAULT_IP}:{DEFAULT_PORT}')
    return CLIENT_SOCK.connect((DEFAULT_IP, DEFAULT_PORT))


def confirm_presence(user_name='Guest'):
    """Функция генерирует словарь для отправки сообщения о присутствии пользователя"""
    return {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: user_name
    }


def receive_message(msg):
    """Функция парсит ответ от сервера"""
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            return 'Response 200: OK'
        elif msg[RESPONSE] == 400:
            return f'Response 400: {msg[ERROR]}'
        return 'Server error'
    raise ValueError


# Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
CLIENT_SOCK = socket(AF_INET, SOCK_STREAM)
# Подключаемся к серверу
identify_ip_port()
MSG = confirm_presence()
send_message(CLIENT_SOCK, MSG)
try:
    ANSWER = receive_message(get_message(CLIENT_SOCK))
    print(ANSWER)
except ValueError:
    print('Не удалось декодировать сообщение от сервера')
