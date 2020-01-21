"""Программа-сервер"""

import sys
import re
from socket import socket, AF_INET, SOCK_STREAM
from common_files.function import get_message, send_message
from common_files.variables import DEFAULT_IP, DEFAULT_PORT, MAX_QUEUE, IP_REGEX, ACTION, \
    PRESENCE, TIME, RESPONSE, ERROR, USER


def identify_ip_port():
    """Если в командной строке введены порт и/или IP-адресс, то привязывает к ним сокет"""
    sys_args = sys.argv
    if '-p' in sys_args:
        try:
            temp_port = sys_args[sys_args.index('-p') + 1]
            if temp_port.isdigit() and 1024 < int(temp_port) < 65535:
                listen_port = int(temp_port)
            else:
                print('Порт введен некорректно.')
                sys.exit(1)
        except IndexError:
            print('После параметра "-p" необходимо указать номер порта.')
            sys.exit(1)
    else:
        listen_port = DEFAULT_PORT
    if '-a' in sys_args:
        try:
            temp_ip = sys_args[sys_args.index('-a') + 1]
            if re.match(IP_REGEX, temp_ip):
                listen_ip = temp_ip
            else:
                print('IP-адрес введен некорректно.')
                sys.exit(1)
        except IndexError:
            print('После параметра "-a" необходимо указать ip-адрес.')
            sys.exit(1)
    else:
        listen_ip = DEFAULT_IP
    return SERVER_SOCK.bind((listen_ip, listen_port))


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
