"""The module contains the configuration of the server logger."""

import os
import sys
from logging import getLogger, Formatter, StreamHandler, ERROR, handlers
sys.path.append('../')
from server.log.log_variables import ENCODING, LOGGING_LEVEL, LOGGING_FORMAT

# Set the path to save the log file.
try:
    os.mkdir(f'{os.path.join(os.path.dirname(__file__))}/log_files')
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/server.log')
except OSError:
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/server.log')

# Create a logger - top-level registrar.
LOG = getLogger('server_logger')
# Message format.
SERVER_FORMATTER = Formatter(LOGGING_FORMAT)

# Create a handler that outputs messages to the stderr stream.
ERROR_HANDLER = StreamHandler(sys.stderr)
# Attach a Formatter Object to a Handler.
ERROR_HANDLER.setFormatter(SERVER_FORMATTER)
# Set message processing level.
ERROR_HANDLER.setLevel(ERROR)
# Transfer data to the built-in handler. Create a new report file once a day.
LOG_FILE = handlers.TimedRotatingFileHandler(
    PATH,
    encoding=ENCODING,
    interval=1,
    when='D'
)
# Apply Report Format.
LOG_FILE.setFormatter(SERVER_FORMATTER)
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
