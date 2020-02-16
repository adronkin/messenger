"""Дескриптор для порта."""

import os
import sys
from logging import getLogger
sys.path.append(os.path.join(os.getcwd(), '..'))
import logs.server_log_config
import logs.client_log_config

PATH = sys.argv[0].split('/')[-1][:-3]
LOGGER = getLogger(f'{PATH}_logger')


class Port:
    """
    Дескриптор для описания порта.
    """

    def __set__(self, instance, value):
        """
        Проерка порта.
        :param instance: экземпляр класса.
        :param value: значение для порта, по умолчанию 7777.
        :return: если порт прошел проверку, то добавляется в список атрибутов экземпляра.
        """
        if not 1023 < value < 65536:
            LOGGER.critical(f'Порт "{value}" введен некорректно. '
                            f'Необходимо ввести значение от 1024 до 65535')
            sys.exit(1)
        instance.__dict__[self.port] = value

    def __set_name__(self, owner, port):
        self.port = port
