"""Module for parsing from the command line"""

import sys
from argparse import ArgumentParser
from logging import getLogger
sys.path.append('../')
from custom.decorators import Log

# Logger initialization.
LOGGER = getLogger('server_logger')


@Log()
def args_parser(default_ip, default_port, *args):
    """
    Function for parsing arguments from the command line.
    :param default_ip: The default IP address.
    :param default_port: default port.
    :param (Tuple) args: tuple with arguments for the parser.
    :return (argparse.Namespace): namespace with arguments.
    """
    parser = ArgumentParser(description='Установить адрес и порт сервера.')
    parser.add_argument('-p', '--port', default=default_port, type=int)
    parser.add_argument('-a', '--address', default=default_ip, type=str)
    namespace = parser.parse_args()
    return namespace.address, namespace.port
