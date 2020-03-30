"""
The module contains functions for parsing startup parameters
from the command line.
"""

import sys
from argparse import ArgumentParser
from logging import getLogger
sys.path.append('../')
from server.custom.decorators import Log

# Logger initialization.
LOGGER = getLogger('server_logger')


@Log()
def args_parser(default_ip, default_port, *args):
    """
    Function for parsing arguments from the command line.\n
    :param default_ip: The default IP address.
    :param default_port: default port.
    :param tuple args: tuple with arguments for the parser.
    :return: object namespace with arguments.
    """
    parser = ArgumentParser(description='Установить адрес и порт сервера.')
    parser.add_argument('-p', '--port', default=default_port, type=int)
    parser.add_argument('-a', '--address', default=default_ip, type=str)
    namespace = parser.parse_args()
    return namespace.address, namespace.port
