"""Address descriptor."""

import re
import sys
from logging import getLogger
sys.path.append('../')
from server.custom.variables import IP_REGEX

LOGGER = getLogger('server_logger')


class Address:
    """
    Class is the handle to the IP address. Regular expression checks the
    validity of the entered address. When you try to set the wrong IP address,
    the application terminates.
    """

    def __set__(self, instance, value):
        """
        Check address.
        :param instance: class instance.
        :param value: value for address.
        :return: if the address passes the check, it is added to the list of instance attributes.
        """
        if not re.match(IP_REGEX, value):
            LOGGER.critical(f'IP-адрес "{value}" введен некорректно.')
            sys.exit(1)
        instance.__dict__[self.address] = value

    def __set_name__(self, owner, address):
        self.address = address
