"""Переменные для использования client.py"""

from time import time

# IP-адрес по умолчанию
DEFAULT_IP = '127.0.0.1'
# Сетевой порт по умолчанию
DEFAULT_PORT = 7777
# Кодировка
ENCODING = 'utf-8'
# Максимальная длина сообщения (байт)
MAX_DATA = 10240

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
PUBLIC_KEY_REQUEST = 'public_key_request'
PUBLIC_KEY = 'public_key'

# Регулярное выражение для проверки корректности IP
IP_REGEX = r'^([0-9]\.|[1]?[0-9][0-9]\.|[2][0-4][0-9]\.|[2][5][0-5]\.){3}([0-9]|[1]?[0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])$'

# Подтверждение присутствия.
CONFIRM_PRESENCE = {
    ACTION: PRESENCE,
    TIME: time(),
    USER: None,
    PUBLIC_KEY: None
}

# Сообщение о выходе.
EXIT_MESSAGE = {
    ACTION: EXIT,
    TIME: time(),
    USER: None
}

# Сообщение.
DICT_MESSAGE = {
    ACTION: MESSAGE,
    TIME: time(),
    SENDER: None,
    RECIPIENT: None,
    MESSAGE_TEXT: None
}

# Добавить в список контактов.
ADD_CONTACT_DICT = {
    ACTION: ADD_CONTACT,
    TIME: time(),
    USER: None,
    ACCOUNT_NAME: None
}

# Удалить из списка контактов.
DEL_CONTACT_DICT = {
    ACTION: DEL_CONTACT,
    TIME: time(),
    USER: None,
    ACCOUNT_NAME: None
}
# Запрос списка контактов.
GET_CONTACTS_DICT = {
    ACTION: GET_CONTACTS,
    TIME: time(),
    USER: None
}

# Запрос списка зарегистрированных пользователей.
GET_REGISTERED_DICT = {
    ACTION: GET_REGISTERED,
    TIME: time(),
    USER: None
}

# Запрос открытого ключа.
GET_PUBLIC_KEY = {
    ACTION: PUBLIC_KEY_REQUEST,
    TIME: time(),
    USER: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}

GET_HELP = """
Доступные команды:
1 - Отправить сообщение.
2 - Вывести подсказки по командам.
3 - Список контактов.
4 - История сообщений.
5 - Выйти из программы.
"""

CONTACT_HELP = """
Доступные команды:
1 - Показать список контактов.
2 - Добавить пользователя в контакты.
3 - Удалить пользовател из контактов.
4 - Вывести подсказки по командам.
5 - Назад.
"""

MESSAGE_HELP = """
Доступные команды:
1 - Вывести входящие сообщения.
2 - Вывести исходящие сообщения.
3 - Вывести все сообщения.
4 - Вывести подсказки по командам.
5 - Назад.
"""
