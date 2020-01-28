"""Программа-сервер"""

import re
import sys
from argparse import ArgumentParser
from socket import socket, AF_INET, SOCK_STREAM
from logging import getLogger
import logs.server_log_config
from decorators import Log
from common_files.function import get_message, send_message
from common_files.variables import DEFAULT_IP, DEFAULT_PORT, MAX_QUEUE, IP_REGEX, ACTION, \
    PRESENCE, TIME, RESPONSE, ERROR, USER

# Инициализируем логгера
LOGGER = getLogger('server_logger')


@Log()
def processing_message(data):
    """Проверяет корректность сообщения data и возвращает ответ для клиента в формате dict"""
    LOGGER.debug(f'Обработка сообщения от клиента - {data}')
    if ACTION in data and data[ACTION] == PRESENCE and TIME in data \
            and USER in data and data[USER] == 'Guest':
        LOGGER.info(f'Сообщение корректно. Отправлен ответ "RESPONSE: 200"')
        return {RESPONSE: 200}
    LOGGER.debug(f'Сообщение некорректно. Отправлен ответ "RESPONSE: 400"')
    return {
        RESPONSE: 400,
        ERROR: 'Bad request'
    }


@Log()
def args_parser():
    """Парсит аргументы командной строки"""
    parser = ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int)
    parser.add_argument('-a', default=DEFAULT_IP)
    return parser


def main():
    """Код запуска server"""
    # Если в командной строке введены порт и/или IP-адресс, то привязывает к ним сокет
    parser = args_parser()
    namespace = parser.parse_args(sys.argv[1:])
    if not 1023 < namespace.p < 65536:
        LOGGER.critical(f'Порт "{namespace.p}" введен некорректно. '
                        f'Необходимо ввести значение от 1024 до 65535')
        sys.exit(1)
    if not re.match(IP_REGEX, namespace.a):
        LOGGER.critical(f'IP-адрес "{namespace.a}" введен некорректно')
        sys.exit(1)
    LOGGER.debug(f'Сервер запущен с параметрами - {namespace.a}:{namespace.p}')

    # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind((namespace.a, namespace.p))
    # Переводим сервер в режим ожидания запросов (слушаем порт).
    server_sock.listen(MAX_QUEUE)

    while True:
        # Принимаем запрос на соединение
        client_sock, address = server_sock.accept()
        LOGGER.info(f'Установлено соединение с клиентом {address}')
        try:
            # Получаем данные от клиента и преобразовываем в словарь
            data = get_message(client_sock)
            msg = processing_message(data)
            send_message(client_sock, msg)
            LOGGER.debug(f'Соединение с клиентом {address} закрыто')
            client_sock.close()
        except ValueError:
            LOGGER.error(f'От клиента {address} приняты некорректные данные. '
                         f'Соединение закрыто')
            client_sock.close()


if __name__ == '__main__':
    main()
