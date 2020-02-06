"""Программа-сервер"""

import re
import sys
import time
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from logging import getLogger
import logs.server_log_config
from decorators import Log
from common_files.function import get_message, send_message
from common_files.variables import DEFAULT_IP, DEFAULT_PORT, MAX_QUEUE, IP_REGEX, ACTION, \
    PRESENCE, TIME, RESPONSE, ERROR, USER, MESSAGE, MESSAGE_TEXT, SENDER

# Инициализируем логгера
LOGGER = getLogger('server_logger')


@Log()
def processing_message(client, data, message_lst):
    """Проверяет корректность сообщения data и возвращает ответ для клиента в формате dict"""
    LOGGER.debug(f'Обработка сообщения от клиента - {data}')
    if ACTION in data and data[ACTION] == PRESENCE and TIME in data \
            and USER in data:
        LOGGER.info(f'Сообщение корректно. Отправлен ответ "RESPONSE: 200"')
        return send_message(client, {RESPONSE: 200})
    elif ACTION in data and data[ACTION] == MESSAGE and TIME in data and MESSAGE_TEXT in data:
        message_lst.append((data[USER], data[MESSAGE_TEXT]))
    LOGGER.debug(f'Сообщение некорректно. Отправлен ответ "RESPONSE: 400"')
    return send_message(client, {
        RESPONSE: 400,
        ERROR: 'Bad request'
    })


@Log()
def args_parser():
    """Парсит аргументы командной строки, проверяет корректность порта и IP-адреса.
    Возвращает IP-адрес и порт, если параметры введены корретно"""
    parser = ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int)
    parser.add_argument('-a', default=DEFAULT_IP)
    namespace = parser.parse_args(sys.argv[1:])
    if not 1023 < namespace.p < 65536:
        LOGGER.critical(f'Порт "{namespace.p}" введен некорректно. '
                        f'Необходимо ввести значение от 1024 до 65535')
        sys.exit(1)
    if not re.match(IP_REGEX, namespace.a):
        LOGGER.critical(f'IP-адрес "{namespace.a}" введен некорректно')
        sys.exit(1)
    return namespace.a, namespace.p


def main():
    """Код запуска server"""
    # Инициализируем переменные IP-адреса и порта
    listen_address, listen_port = args_parser()
    LOGGER.info(
        f'Сервер запущен с параметрами - {listen_address}:{listen_port}')
    # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP
    # пакетами)
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind((listen_address, listen_port))
    server_sock.settimeout(0.5)
    # Переводим сервер в режим ожидания запросов (слушаем порт).
    server_sock.listen(MAX_QUEUE)

    clients = []
    messages = []

    while True:
        # Принимаем запрос на соединение
        try:
            client_sock, address = server_sock.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Установлено соединение с клиентом {address}')
            clients.append(client_sock)

        # Списки объектов готовых к вводу, выводу
        # и проверяемых на наличие исключений
        clients_senders = []
        clients_recipients = []
        errors_lst = []

        try:
            if clients:
                # Запрашиваем информацию о готовности к вводу и выводу
                clients_senders, clients_recipients, errors_lst = select(
                    clients, clients, [], 0)
        except OSError:
            print('Исключение OSError - строка 93')
        # Принимаем сообщения, если есть сообщения от клиентов, кладем в словарь.
        # Если возвращена ошибка, исключаем клиента из списка clients
        if clients_senders:
            for client_with_message in clients_senders:
                try:
                    processing_message(
                        client_with_message,
                        get_message(client_with_message),
                        messages)
                except:
                    # LOGGER.info(
                    #     f'Клиент {client_with_message.getpeername()} отключился от сервера')
                    LOGGER.info(f'Клиент отключился от сервера')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки и ожидающие клиенты,
        # отправляем им сообщение.
        if messages and clients_recipients:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in clients_recipients:
                try:
                    send_message(waiting_client, message)
                except:
                    # LOGGER.info(
                    #     f'Клиент {waiting_client.getpeername()} отключился от сервера')
                    LOGGER.info(f'Клиент отключился от сервера')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
