"""Логирование server.py"""

import os
import sys
from logging import getLogger, Formatter, StreamHandler, ERROR, handlers
sys.path.append(os.path.join(os.getcwd(), '..'))
from common_files.variables import ENCODING, LOGGING_LEVEL, LOGGING_FORMAT

# Задаем путь сохранения файла лога
try:
    os.mkdir(f'{os.path.join(os.path.dirname(__file__))}/log_files')
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/server.log')
except OSError:
    PATH = os.path.join(os.path.dirname(__file__), 'log_files/server.log')

# Создаем логгер - регистратор верхнего уроовня с именем app.server
LOG = getLogger('server_logger')
# Задаем формат сообщений
SERVER_FORMATTER = Formatter(LOGGING_FORMAT)

# Создаем обработчик, который выводит сообщения в поток stderr
ERROR_HANDLER = StreamHandler(sys.stderr)
# Подключаем объект Formatter к обработчику
ERROR_HANDLER.setFormatter(SERVER_FORMATTER)
# Задаем уровень обработки сообщений
ERROR_HANDLER.setLevel(ERROR)
# Передаем данные во встроенный обработчик (создается новый файл отчета 1 раз в день)
LOG_FILE = handlers.TimedRotatingFileHandler(PATH, encoding=ENCODING, interval=1, when='D')
# Применяем формат отчета
LOG_FILE.setFormatter(SERVER_FORMATTER)
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
