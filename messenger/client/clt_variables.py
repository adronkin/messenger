"""Переменные для использования client.py"""

# IP-адрес по умолчанию
DEFAULT_IP = '127.0.0.1'
# Сетевой порт по умолчанию
DEFAULT_PORT = 7777
# Кодаровка
ENCODING = 'utf-8'
# Максимальная длина сообщения (байт)
MAX_DATA = 1024

# Ключи JIM протокола
ACTION = 'action'
USER = 'user'
TIME = 'time'
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
