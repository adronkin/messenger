"""Функции для парсинга из командной строки server.py"""

import os
import sys
from argparse import ArgumentParser
from logging import getLogger
sys.path.append(os.path.join(os.getcwd(), '..'))
from decorators import Log

# Инициализируем логгера.
LOGGER = getLogger('server_logger')


@Log()
def args_parser(default_ip, default_port, *args):
    """
    Парсит аргументы командной строки.
    :param default_ip: IP-адрес по умолчанию.
    :param default_port: порт по умолчанию.
    :param (Tuple) args: кортеж с аргументами для парсера.
    :return (argparse.Namespace): пространство имен с аргументами.
    """
    parser = ArgumentParser(description='Установить адрес и порт сервера.')
    parser.add_argument('-p', '--port', default=default_port, type=int)
    parser.add_argument('-a', '--address', default=default_ip, type=str)
    namespace = parser.parse_args()
    return namespace.address, namespace.port
