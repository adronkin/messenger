"""Программа-клиент"""

import re
import sys
from time import strftime, strptime, ctime, time
from logging import getLogger
from argparse import ArgumentParser
from json import JSONDecodeError
from socket import socket, SOCK_STREAM, AF_INET
import logs.client_log_config
from decorators import Log
from errors import ClientError, ReqFieldMissingError
from common_files.function import send_message, get_message
from common_files.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX, ACTION, \
    PRESENCE, TIME, USER, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER

# Инициализируем логгера
LOGGER = getLogger('client_logger')


@Log()
def user_message_handler(message):
    """Функция обрабатывает сообщения от других пользователей"""
    if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
            and MESSAGE_TEXT in message and SENDER in message:
        message_time = strftime("%d.%m.%Y %H:%m:%S", strptime(ctime(message[TIME])))
        print(f'{message_time} - {message[SENDER]}: {message[MESSAGE_TEXT]}')
        LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                    f' {message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Принято некорректное сообщение {message}')


@Log()
def create_message(sock, user_name):
    """Функция запрашивает текст сообщения и формирует словарь для сервера.
    При вводе команды завершает работу"""
    message = input('Для завершения работы введите "--exit".\n'
                    'Введите текст сообщения: ')
    if message == '--exit':
        sock.close()
        LOGGER.info(f'Пользователь {user_name} завершил работу.')
        print('Работа завершена.')
        sys.exit(0)
    dict_message = {
        ACTION: MESSAGE,
        TIME: time(),
        USER: user_name,
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформировано сообщение для отправки {dict_message}')
    return dict_message


@Log()
def confirm_presence(user_name):
    """Функция генерирует словарь для отправки сообщения о присутствии пользователя"""
    message = {
        ACTION: PRESENCE,
        TIME: time(),
        USER: user_name
    }
    LOGGER.info(f'Сгенерировано {PRESENCE} сообщение для пользователя {user_name}')
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
                         f'Получен отвен "Response 400: {msg[ERROR]}".')
            raise ClientError(f' 400: {msg[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@Log()
def args_parser():
    """Парсит аргументы командной строки, проверяет корректность порта и IP-адреса.
    Возвращает IP-адрес и порт, если параметры введены корретно"""
    parser = ArgumentParser()
    parser.add_argument('address', default=DEFAULT_IP, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    parser.add_argument('-n', '--name', default='Guest', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    if not 1023 < namespace.port < 65536:
        LOGGER.critical(f'Порт "{namespace.port}" введен некорректно. '
                        f'Необходимо ввести значение от 1024 до 65535.')
        sys.exit(1)
    if not re.match(IP_REGEX, namespace.address):
        LOGGER.critical(f'IP-адрес "{namespace.address}" введен некорректно.')
        sys.exit(1)
    if namespace.mode not in ('listen', 'send'):
        LOGGER.critical(f'Введен некорректный режим работы.'
                        f' Необходимо ввести заначение "listen" или "send".')
        sys.exit(1)
    return namespace.address, namespace.port, namespace.mode, namespace.name


def main():
    """Код запуска client"""
    server_ip, server_port, client_mode, client_name = args_parser()
    LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера - {server_ip},'
                f' порт сервера - {server_port}, режим работы клиента - {client_mode} ')
    try:
        # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
        client_sock = socket(AF_INET, SOCK_STREAM)
        # Подключаемся к серверу
        client_sock.connect((server_ip, server_port))
        send_message(client_sock, confirm_presence(client_name))
        answer = receive_message(get_message(client_sock))
        LOGGER.info(f'Установлено соединение с сервером {server_ip}:{server_port}.'
                    f' Ответ сервера: {answer}')
        print('Соединение с сервером установлено.')
    except ClientError as error:
        LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as error:
        LOGGER.error(f'В ответе сервера отсутствует обязательное поле: {error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось подключиться к серверу {server_ip}:{server_port}')
        sys.exit(1)
    except JSONDecodeError:
        LOGGER.error(f'Не удалось декодировать принятое JSON сообщение.')
        sys.exit(1)
    # Если соединение с сервером установлено корректно
    else:
        if client_mode == 'listen':
            print('Режим работы: прием сообщений.')
        else:
            print('Режим работы: отправка сообщений.')
        while True:
            if client_mode == 'listen':
                try:
                    user_message_handler(get_message(client_sock))
                except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError):
                    LOGGER.error(f'Соединение с сервером {server_ip}:{server_port} потеряно')
                    sys.exit(1)
            if client_mode == 'send':
                try:
                    send_message(client_sock, create_message(client_sock, client_name))
                except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError):
                    LOGGER.error(f'Соединение с сервером {server_ip}:{server_port} потеряно')
                    sys.exit(1)


if __name__ == '__main__':
    main()
