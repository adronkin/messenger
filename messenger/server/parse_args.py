"""Функции для парсинга из командной строки server.py"""

import os
import sys
from argparse import ArgumentParser
from logging import getLogger
sys.path.append(os.path.join(os.getcwd(), '..'))
from decorators import Log
from common_files.variables import DEFAULT_PORT, DEFAULT_IP

# Инициализируем логгера
LOGGER = getLogger('server_logger')


@Log()
def args_parser(*args):
    """
    Парсит аргументы командной строки.
    :param (Tuple) args: кортеж с аргументами для парсера.
    :return (argparse.Namespace): пространство имен с аргументами.
    """
    parser = ArgumentParser(description='Установить адрес и порт сервера.')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int)
    parser.add_argument('-a', '--address', default=DEFAULT_IP, type=str)
    namespace = parser.parse_args()
    return namespace.address, namespace.port
