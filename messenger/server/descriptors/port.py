"""Port descriptor."""

import sys
from logging import getLogger
sys.path.append('../')
import server.log.log_config

LOGGER = getLogger('server_logger')


class Port:
    """
    Class is the handle to the port number. Allows only ports 1023 through
    65536 to be used. When you try to set the wrong port number, the
    application terminates.
    """

    def __set__(self, instance, value):
        """
        Check port.
        :param instance: class instance.
        :param value: value for port.
        :return: if the port passes the check, it is added to the list of instance attributes.
        """
        if not 1023 < value < 65536:
            LOGGER.critical(f'Порт "{value}" введен некорректно. '
                            f'Необходимо ввести значение от 1024 до 65535.')
            sys.exit(1)
        instance.__dict__[self.port] = value

    def __set_name__(self, owner, port):
        self.port = port
