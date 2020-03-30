"""
The module contains functions for parsing startup parameters
from the command line.
"""

import re
import sys
from argparse import ArgumentParser
from logging import getLogger
sys.path.append('../')
from client.custom.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX
from client.custom.decorators import Log

# Logger initialization.
LOGGER = getLogger('client_logger')


@Log()
def args_parser(*args):
    """
    Function for parsing arguments from the command line.\n
    :param tuple args: tuple with arguments for the parser.
    :return: object namespace with arguments.
    """
    parser = ArgumentParser(description='[Установить адрес и порт сервера.')
    parser.add_argument('address', default=DEFAULT_IP, type=str, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, type=str, nargs='?')
    parser.add_argument('-p', '--password', default=None, type=str, nargs='?')
    return parser.parse_args(*args)


@Log()
def check_port(port):
    """
    The function checks the port for correctness.\n
    :param int port: server port.
    :return bool: True if the port is correct, False if not.
    """
    if 1023 < port < 65536:
        return True
    LOGGER.critical(f'Порт "{port}" введен некорректно. Необходимо ввести'
                    f' значение от 1024 до 65535.')
    return False


@Log()
def check_address(address):
    """
    The function checks the correctness of the address.\n
    :param str address: server address.
    :return bool: True if the address is correct, False if not.
    """
    if re.match(IP_REGEX, address):
        return True
    LOGGER.critical(f'IP-адрес "{address}" введен некорректно.')
    return False


@Log()
def get_command_args(*args):
    """
    The function returns the IP address and port of the server
    if it was entered on the command line.
    The default is IP address 127.0.0.1, port 7777.\n
    :param tuple args: tuple with arguments for the parser.
    :return: object namespace with arguments.
    """
    namespace = args_parser(*args)
    if not check_address(namespace.address):
        sys.exit(1)
    if not check_port(namespace.port):
        sys.exit(1)
    return namespace
