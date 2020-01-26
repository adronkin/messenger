"""Логирование client.py"""

import os
import sys
from logging import getLogger, Formatter, StreamHandler, ERROR, FileHandler
sys.path.append(os.path.join(os.getcwd(), '..'))
from common_files.variables import ENCODING, LOGGING_LEVEL, LOGGING_FORMAT

try:
    os.mkdir(f'{os.path.join(os.path.dirname(__file__))}/log_files')
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/client.log')
except OSError:
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/client.log')

LOG = getLogger('client_logger')

CLIENT_FORMATTER = Formatter(LOGGING_FORMAT)

# Создаем обработчик, подключеаем Formatter, задаем уровень отслеживания
ERROR_HANDLER = StreamHandler(sys.stderr)
ERROR_HANDLER.setFormatter(CLIENT_FORMATTER)
ERROR_HANDLER.setLevel(ERROR)

# Создаем обработчик, задаем формат
LOG_FILE = FileHandler(PATH, encoding=ENCODING)
LOG_FILE.setFormatter(CLIENT_FORMATTER)
LOG.setLevel(LOGGING_LEVEL)

# Добавляем обработчик к регистратору
LOG.addHandler(ERROR_HANDLER)
LOG.addHandler(LOG_FILE)

# Отладка
if __name__ == '__main__':
    LOG.debug('Отладочная информация')
    LOG.info('Информационное сообщение')
    LOG.warning('Предупреждение')
    LOG.error('Ошибка')
    LOG.critical('Критическая ошибка')
