"""Программа-сервер"""

import re
import sys
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from logging import getLogger
import logs.server_log_config
from decorators import Log
from common_files.function import get_message, send_message
from common_files.variables import DEFAULT_IP, DEFAULT_PORT, MAX_QUEUE, IP_REGEX, ACTION, \
    PRESENCE, TIME, ERROR, USER, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, \
    RESPONSE_300, RESPONSE_400, EXIT, RECIPIENT

# Инициализируем логгера
LOGGER = getLogger('server_logger')


@Log()
def processing_message(data, client, message_lst, clients, names):
    """Проверяет корректность сообщения data и возвращает ответ для клиента в формате dict"""
    LOGGER.debug(f'Обработка сообщения от клиента - {data}')
    # Если PRESENCE-сообщение, проверяем и отвечаем
    if ACTION in data and data[ACTION] == PRESENCE and TIME in data and USER in data:
        # Проверяем зарегистрирован пользователь или нет
        if data[USER] not in names.keys():
            names[data[USER]] = client
            send_message(client, RESPONSE_200)
            LOGGER.info(f'Клиент {client.getpeername()} подключился.'
                        f' Отправлен ответ {RESPONSE_200}')
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя занято.'
            send_message(client, response)
            LOGGER.error(f'Попытка подключения клиента {client.getpeername()} используя'
                         f' занятое имя пользователя. Отправлен ответ {RESPONSE_400}')
            clients.remove(client)
            client.close()
        return
    # Если сообщение, то проверяем и добовляем его в очередь сообщений
    elif ACTION in data and data[ACTION] == MESSAGE and TIME in data and SENDER in data\
            and RECIPIENT in data and MESSAGE_TEXT in data:
        message_lst.append(data)
        return
    # Если пользоваталь хочет завершить работу
    elif ACTION in data and data[ACTION] == EXIT and TIME in data and USER in data:
        LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
        clients.remove(names[data[USER]])
        names[data[USER]].close()
        del names[data[USER]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Bad request.'
        LOGGER.debug(f'Получен некорректный запрос от клиента {client.getpeername()},'
                     f' отправлен ответ {response}')
        send_message(client, response)
        return


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


@Log()
def message_handler(message, names, listen_sock):
    """Функция обрабатывает сообщение. Принимает словарь сообщения,
    список пользователей и слушащие сокеты. Отправляет сообщение адресату."""
    if message[RECIPIENT] in names and names[message[RECIPIENT]] in listen_sock:
        send_message(names[message[RECIPIENT]], message)
        LOGGER.info(f'Сообщение от пользователя {message[SENDER]}'
                    f' передано пользователю {message[RECIPIENT]}.')
    elif message[RECIPIENT] in names and names[message[RECIPIENT]] not in listen_sock:
        raise ConnectionError
    else:
        no_user_dict = RESPONSE_300
        no_user_dict[ERROR] = f'Пользователь с именем {message[RECIPIENT]}' \
                              f' не зарегистрирован на сервере.'
        send_message(names[message[SENDER]], no_user_dict)
        LOGGER.error(f'{no_user_dict[ERROR]} Отправка сообщения невозможна.')
        LOGGER.debug(f'Пользователю {message[SENDER]} отправлен ответ {no_user_dict}')


def main():
    """Код запуска server"""
    # Инициализируем переменные IP-адреса и порта
    listen_address, listen_port = args_parser()
    LOGGER.info(
        f'Сервер запущен с параметрами - {listen_address}:{listen_port}')
    # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind((listen_address, listen_port))
    server_sock.settimeout(0.5)
    # Переводим сервер в режим ожидания запросов (слушаем порт).
    server_sock.listen(MAX_QUEUE)

    # Список клиентов, очередь сообщений, словарь с именами и сокетами пользователей
    clients = []
    messages = []
    names = dict()

    while True:
        # Принимаем запрос на соединение
        try:
            client_sock, address = server_sock.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Установлено соединение с клиентом {address}')
            clients.append(client_sock)

        # Списки объектов готовых к вводу, выводу и проверяемых на наличие исключений
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
                    processing_message(get_message(client_with_message),
                                       client_with_message, messages, clients, names)
                except Exception:
                    LOGGER.info(
                        f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                    clients.remove(client_with_message)

        # Если есть сообщения для отправки, обрабатываем.
        for message in messages:
            try:
                message_handler(message, names, clients_recipients)
            except Exception:
                LOGGER.info(f'Клиент {message[RECIPIENT]} отключился от сервера.')
                no_user_dict = RESPONSE_300
                no_user_dict[ERROR] = f'Пользователь {message[RECIPIENT]} отключился от сервера.'
                send_message(names[message[SENDER]], no_user_dict)
                # clients.remove(names[message[RECIPIENT]])
                del names[message[RECIPIENT]]
        messages.clear()


if __name__ == '__main__':
    main()
