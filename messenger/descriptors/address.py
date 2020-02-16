"""Дескриптор для адреса."""


import os
import re
import sys
from logging import getLogger
sys.path.append(os.path.join(os.getcwd(), '..'))
from common_files.variables import IP_REGEX
import logs.server_log_config
import logs.client_log_config

PATH = sys.argv[0].split('/')[-1][:-3]
LOGGER = getLogger(f'{PATH}_logger')


class Address:
    """
    Дескриптор для описания адреса.
    """

    def __set__(self, instance, value):
        """
        Проверка адреса.
        :param instance: экземпляр класса.
        :param value: значение для адреса, по умолчанию 127.0.0.1
        :return: если адрес прошел проверку, то добавляется в список атрибутов экземпляра.
        """
        if not re.match(IP_REGEX, value):
            LOGGER.critical(f'IP-адрес "{value}" введен некорректно.')
            sys.exit(1)
        instance.__dict__[self.address] = value

    def __set_name__(self, owner, address):
        self.address = address
