"""Программа-сервер"""

import sys
import re
from socket import socket, AF_INET, SOCK_STREAM
from lesson_3.common_files.function import get_message, send_message
from lesson_3.common_files.variables import DEFAULT_IP, DEFAULT_PORT, MAX_QUEUE, IP_REGEX, ACTION, \
    PRESENCE, TIME, RESPONSE, ERROR, USER


def identify_ip_port():
    """Если в командной строке введены порт и IP-адресс, то привязывает к ним сокет"""
    sys_args = sys.argv
    if len(sys_args) == 1:
        # Привязываем сокет к IP-адресу и порту
        return SERVER_SOCK.bind((DEFAULT_IP, DEFAULT_PORT))
    if len(sys_args) == 5:
        if sys_args[1] == '-p' and sys_args[3] == '-a':
            if sys_args[2].isdigit() and 1024 < int(sys_args[2]) < 65535 and \
                    re.match(IP_REGEX, sys_args[4]):
                return SERVER_SOCK.bind((sys_args[4], int(sys_args[2])))
    print(f'Параметры введены некорректно, пример корректного ввода -'
          f' "имя_скрипта.py -p <port> -a <ip_address>. \n'
          f'Будут использованы стандартные параметры - {DEFAULT_IP}:{DEFAULT_PORT}')
    return SERVER_SOCK.bind((DEFAULT_IP, DEFAULT_PORT))


def processing_message(data):
    """Проверяет корректность сообщения data и возвращает ответ для клиента в формате dict"""
    if ACTION in data and data[ACTION] == PRESENCE and TIME in data \
            and USER in data and data[USER] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


# Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
SERVER_SOCK = socket(AF_INET, SOCK_STREAM)
identify_ip_port()

# Переводим сервер в режим ожидания запросов.
SERVER_SOCK.listen(MAX_QUEUE)

while True:
    # Принимаем запрос на соединение
    CLIENT_SOCK, ADDRESS = SERVER_SOCK.accept()
    try:
        # Получаем данные от клиента и преобразовываем в словарь
        DATA = get_message(CLIENT_SOCK)
        print(DATA)
        MSG = processing_message(DATA)
        send_message(CLIENT_SOCK, MSG)
        CLIENT_SOCK.close()
    except ValueError:
        print('Принято некорректное сообщение')
        CLIENT_SOCK.close()
