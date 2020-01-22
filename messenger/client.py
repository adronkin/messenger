"""Программа-клиент"""

import re
import sys
import time
from socket import socket, SOCK_STREAM, AF_INET
from common_files.function import send_message, get_message
from common_files.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX, ACTION, \
    PRESENCE, TIME, USER, RESPONSE, ERROR


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


def main():
    """Код запуска client"""
    sys_args = sys.argv
    if len(sys_args) == 3:
        if sys_args[2].isdigit() and 1024 < int(sys_args[2]) < 65535 and\
                re.match(IP_REGEX, sys_args[1]):
            listen_ip, listen_port = sys_args[1], int(sys_args[2])
        else:
            print(
                f'Параметры введены некорректно, пример корректного ввода -'
                f' "имя_скрипта.py <ip_address> <port>.')
            sys.exit(1)
    elif len(sys_args) == 1:
        listen_ip, listen_port = DEFAULT_IP, DEFAULT_PORT
    # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
    client_sock = socket(AF_INET, SOCK_STREAM)
    # Подключаемся к серверу
    client_sock.connect((listen_ip, listen_port))
    msg = confirm_presence()
    send_message(client_sock, msg)
    try:
        answer = receive_message(get_message(client_sock))
        print(answer)
    except ValueError:
        print('Не удалось декодировать сообщение от сервера')


if __name__ == '__main__':
    main()
