"""The module contains the configuration of the client logger."""

import os
import sys
from logging import getLogger, Formatter, StreamHandler, ERROR, FileHandler
sys.path.append('../')
from client.log.log_variables import ENCODING, LOGGING_LEVEL, LOGGING_FORMAT

try:
    os.mkdir(f'{os.path.join(os.path.dirname(__file__))}/log_files')
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/client.log')
except OSError:
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/client.log')

LOG = getLogger('client_logger')

CLIENT_FORMATTER = Formatter(LOGGING_FORMAT)

# Create a handler, enable Formatter, set the tracking level.
ERROR_HANDLER = StreamHandler(sys.stderr)
ERROR_HANDLER.setFormatter(CLIENT_FORMATTER)
ERROR_HANDLER.setLevel(ERROR)

# Create a handler, set the format.
LOG_FILE = FileHandler(PATH, encoding=ENCODING)
LOG_FILE.setFormatter(CLIENT_FORMATTER)
LOG.setLevel(LOGGING_LEVEL)

# Add a handler to the registrar.
LOG.addHandler(ERROR_HANDLER)
LOG.addHandler(LOG_FILE)

if __name__ == '__main__':
    LOG.debug('Отладочная информация')
    LOG.info('Информационное сообщение')
    LOG.warning('Предупреждение')
    LOG.error('Ошибка')
    LOG.critical('Критическая ошибка')
