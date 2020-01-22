"""Программа-сервер"""

import sys
import re
from socket import socket, AF_INET, SOCK_STREAM
from common_files.function import get_message, send_message
from common_files.variables import DEFAULT_IP, DEFAULT_PORT, MAX_QUEUE, IP_REGEX, ACTION, \
    PRESENCE, TIME, RESPONSE, ERROR, USER


def processing_message(data):
    """Проверяет корректность сообщения data и возвращает ответ для клиента в формате dict"""
    if ACTION in data and data[ACTION] == PRESENCE and TIME in data \
            and USER in data and data[USER] == 'Guest':
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


def main():
    """Код запуска server"""
    # Если в командной строке введены порт и/или IP-адресс, то привязывает к ним сокет
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

    # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP
    # пакетами)
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind((listen_ip, listen_port))

    # Переводим сервер в режим ожидания запросов.
    server_sock.listen(MAX_QUEUE)

    while True:
        # Принимаем запрос на соединение
        client_sock, address = server_sock.accept()
        try:
            # Получаем данные от клиента и преобразовываем в словарь
            data = get_message(client_sock)
            print(data)
            msg = processing_message(data)
            send_message(client_sock, msg)
            client_sock.close()
        except ValueError:
            print('Принято некорректное сообщение')
            client_sock.close()


if __name__ == '__main__':
    main()
