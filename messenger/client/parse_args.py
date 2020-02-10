"""Функции для парсинга из командной строки server.py"""

import os
import re
import sys
from argparse import ArgumentParser
from logging import getLogger
sys.path.append(os.path.join(os.getcwd(), '..'))
from decorators import Log
from common_files.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX

# Инициализируем логгера
LOGGER = getLogger('client_logger')


@Log()
def args_parser(*args):
    """
    Парсит аргументы командной строки.
    :param (Tuple) args: кортеж с аргументами для парсера.
    :return (argparse.Namespace): пространство имен с аргументами.
    """
    parser = ArgumentParser(description='[Установить адрес и порт сервера.')
    parser.add_argument('address', default=DEFAULT_IP, type=str, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, type=str, nargs='?')
    return parser.parse_args(*args)


@Log()
def check_port(port):
    """
    Проверяет корректность порта.
    :param (int) port: порт сервера.
    :return (bool): True если порт корректный, False если нет.
    """
    if 1023 < port < 65536:
        return True
    else:
        LOGGER.critical(f'Порт "{port}" введен некорректно. '
                        f'Необходимо ввести значение от 1024 до 65535')
        return False


@Log()
def check_address(address):
    """
    Проверяет корректность адреса.
    :param (str) address: порт сервера.
    :return (bool): True если адрес корректный, False если нет.
    """
    if re.match(IP_REGEX, address):
        return True
    else:
        LOGGER.critical(f'IP-адрес "{address}" введен некорректно')
        return False


@Log()
def get_command_args(*args):
    """
    Возвращает IP-адрес и порт сервера, если были введены в командной строке.
    По умолчанию - IP-адрес 127.0.0.1, порт 7777.
    :param (Tuple) args: кортеж с аргументами для парсера.
    :return (argparse.Namespace): пространство имен с аргументами.
    """
    namespace = args_parser(*args)
    if not check_address(namespace.address):
        sys.exit(1)
    if not check_port(namespace.port):
        sys.exit(1)
    return namespace
