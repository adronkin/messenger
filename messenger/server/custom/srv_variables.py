"""Переменные для использования server.py"""

import os

# IP-адрес по умолчанию
DEFAULT_IP = '127.0.0.1'
# Сетевой порт по умолчанию
DEFAULT_PORT = 7777
# Кодировка
ENCODING = 'utf-8'
# Максимальная длина очереди на подключение
MAX_QUEUE = 3
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
ADD_CONTACT = 'add_contact'
ACCOUNT_NAME = 'account_name'
DEL_CONTACT = 'del_contact'
DATA = 'data'
GET_CONTACTS = 'get_contacts'
GET_REGISTERED = 'get_registered'

# Регулярное выражение для проверки корректности IP
IP_REGEX = r'^([0-9]\.|[1]?[0-9][0-9]\.|[2][0-4][0-9]\.|[2][5][0-5]\.){3}([0-9]|[1]?[0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])$'

# Ответы
RESPONSE_200 = {RESPONSE: 200}

RESPONSE_205 = {RESPONSE: 205}

RESPONSE_202 = {
    RESPONSE: 202,
    DATA: None
}

RESPONSE_300 = {
    RESPONSE: 300,
    ERROR: None
}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

# Имя файла БД
DB_FILE_NAME = 'server/database/server_database.db3'
# Путь к базе данных для хранения данных сервера:
SERVER_DATABASE = f'sqlite:///{"/".join(map(str, os.path.dirname(__file__).split("/")[:-1]))}' \
                  f'/server/database/{DB_FILE_NAME}'
