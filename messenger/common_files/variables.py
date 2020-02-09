"""Переменные для использования server.py и client.py"""

from logging import DEBUG

# IP-адрес по умолчанию
DEFAULT_IP = '127.0.0.1'
# Сетевой порт по умолчанию
DEFAULT_PORT = 7777
# Кодаровка
ENCODING = 'utf-8'
# Максимальная длина очереди на подключение
MAX_QUEUE = 3
# Максимальная длина сообщения (байт)
MAX_DATA = 1024
# Уровень логирования
LOGGING_LEVEL = DEBUG
# Формат сообщений лога
LOGGING_FORMAT = '%(asctime)s - %(levelname)-8s - %(module)s - %(message)s'

# Ключи JIM протокола
ACTION = 'action'
USER = 'user'
TIME = 'time'
ROOM = 'room'
RESPONSE = 'response'
PRESENCE = 'presence'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
SENDER = 'sender'
EXIT = 'exit'
RECIPIENT = 'recipient'

# Реглярное выражение для проверки корректности IP
IP_REGEX = r'^([0-9]\.|[1]?[0-9][0-9]\.|[2][0-4][0-9]\.|[2][5][0-5]\.){3}([0-9]|[1]?[0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])$'

# Ответы
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_300 = {
    RESPONSE: 300,
    ERROR: None
}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}
