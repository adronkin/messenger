"""Дескриптор для порта."""

import sys
from logging import getLogger
sys.path.append('../')
import log.log_config

LOGGER = getLogger('server_logger')


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
