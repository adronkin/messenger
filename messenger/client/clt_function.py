"""Функции для использования server.py и client.py"""

import sys
import json
from logging import getLogger
from clt_variables import PRESENCE, USER, RESPONSE, ERROR, MAX_DATA, ENCODING, ADD_CONTACT_DICT, \
    ACCOUNT_NAME, DEL_CONTACT_DICT, GET_CONTACTS_DICT, DATA, CONFIRM_PRESENCE, GET_REGISTERED_DICT
sys.path.append('../')
import logs.client_log_config
from decorators import Log
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError, NonDictInputError

# Инициализируем логгера.
LOGGER = getLogger('client_logger')


@Log()
def get_message(client_server):
    """
    Функция принимает сообщение в байтах и возвращает словарь.
    Если преобразование не удалось, то вызывает исключение ValueError.
    :param client_server: сокет сервера.
    :return:
    """
    data = client_server.recv(MAX_DATA)
    # Проверяем, что data в байтах
    if isinstance(data, bytes):
        decoded_data = data.decode(ENCODING)
        dict_data = json.loads(decoded_data)
        if isinstance(dict_data, dict):
            return dict_data
        raise IncorrectDataReceivedError
    raise IncorrectDataReceivedError


@Log()
def send_message(recipient, message):
    """
    Принимает словарь message, сериальзует его в json и отправляет.
    :param {str} recipient: получатель сообщения.
    :param {dict} message: сообщение для отправки.
    :return:
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    json_message = json.dumps(message)
    encode_message = json_message.encode(ENCODING)
    recipient.send(encode_message)


@Log()
def confirm_presence(username):
    """
    Функция генерирует словарь для отправки сообщения о присутствии пользователя.
    :param {str} username: имя пользователя-клиента.
    :return {dict}: словарь для подтверждения присутствия пользователя.
    """
    message = CONFIRM_PRESENCE
    message[USER] = username
    LOGGER.info(f'Сгенерировано {PRESENCE} сообщение для пользователя {username}.')
    return message


@Log()
def receive_message(message):
    """
    Функция парсит ответ сервера.
    :param {dict} message: сообщение от сервера.
    :return {str}: response 200.
    """
    LOGGER.debug(f'Обработка сообщения от сервера {message}.')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            LOGGER.info('Сообщение корректно обработано. Response 200: OK')
            return 'Response 200: OK'
        elif message[RESPONSE] == 400 and ERROR in message:
            LOGGER.error(f'Сервер не смог обработать клиентский запрос. '
                         f'Получен ответ "Response 400: {message[ERROR]}".')
            raise ServerError(f'400: {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@Log()
def add_contact_to_server(sock, username, contact):
    """
    Функция отправляет на сервер информацию о добавлении контакта.
    :param sock:
    :param {str} username: имя пользователя-клиента.
    :param {str} contact: имя пользователя для добавления в список контактов.
    :return:
    """
    LOGGER.debug(f'Создание контакта {contact}.')
    add_contact_dict = ADD_CONTACT_DICT
    add_contact_dict[USER] = username
    add_contact_dict[ACCOUNT_NAME] = contact
    # Отправляем сообщение на сервер.
    send_message(sock, add_contact_dict)
    # Получаем и обрабатываем ответ.
    server_answer = get_message(sock)
    if RESPONSE in server_answer and RESPONSE == 200:
        LOGGER.info(f'Пользователь {contact} успешно добавлен в список контактов.')
        print(f'Пользователь {contact} успешно добавлен в список контактов.')
    else:
        raise ServerError('Ошибка создания контакта')


@Log()
def remove_contact_to_server(sock, username, contact):
    """
    Функция отправляет на сервер информацию об удалении контакта.
    :param sock: сокет клиента.
    :param {str} username: имя пользователя-клиента.
    :param {str} contact: имя пользователя для удаления из списка контактов.
    :return:
    """
    LOGGER.debug(f'Удаление контакта {contact}.')
    del_contact_dict = DEL_CONTACT_DICT
    del_contact_dict[USER] = username
    del_contact_dict[ACCOUNT_NAME] = contact
    # Отправляем сообщение на сервер.
    send_message(sock, del_contact_dict)
    # Получаем и обрабатываем ответ.
    server_answer = get_message(sock)
    if RESPONSE in server_answer and RESPONSE == 200:
        LOGGER.info(f'Пользователь {contact} успешно удален из списока контактов.')
        print(f'Пользователь {contact} успешно удален из списока контактов.')
    else:
        raise ServerError('Ошибка удаления контакта')


@Log()
def get_contact_list_from_server(sock, username):
    """
    Функция запрашивает с сервера список контактов пользователя.
    :param sock: сокет клиента.
    :param {str} username: имя пользователя-клиента.
    :return {list}: контакты пользователя username.
    """
    LOGGER.debug(f'Запрос списка контактов пользователя {username}.')
    get_contacts_dict = GET_CONTACTS_DICT
    get_contacts_dict[USER] = username
    # Отправляем сообщение на сервер.
    send_message(sock, get_contacts_dict)
    # Получаем и обрабатываем ответ.
    server_answer = get_message(sock)
    if RESPONSE in server_answer and server_answer[RESPONSE] == 202 and DATA in server_answer:
        return server_answer[DATA]
    else:
        raise ServerError


@Log()
def get_registered_user_from_server(sock, username):
    """
    Функция запрашивает с сервера список зарегистрированных пользователей.
    :param sock: сокет клиента.
    :param {str} username: имя пользователя-клиента.
    :return {list}: контакты пользователя username.
    """
    LOGGER.debug(f'Запрос зарегистрированных пользователей клиентом {username}.')
    get_registered_dict = GET_REGISTERED_DICT
    get_registered_dict[USER] = username
    # Отправляем сообщение на сервер.
    send_message(sock, get_registered_dict)
    # Получаем и обрабатываем ответ.
    server_answer = get_message(sock)
    if RESPONSE in server_answer and server_answer[RESPONSE] == 202 and DATA in server_answer:
        return server_answer[DATA]
    else:
        raise ServerError


@Log()
def load_data_from_server(sock, database, username):
    """
    Функция загрузки данных в БД с сервера.
    :param sock: сокет клиента.
    :param database: база данных.
    :param username: имя пользователя-клиента.
    :return:
    """
    # Получаем с сервера список зарегистрированных пользователей и загружаем в БД.
    try:
        user_list = get_registered_user_from_server(sock, username)
    except ServerError:
        LOGGER.error('Ошибка запроса списка зарегистрированных пользователей.')
    else:
        database.add_register_users(user_list)
    # Получаем с сервера список контактов и загружаем в БД.
    try:
        contact_list = get_contact_list_from_server(sock, username)
    except ServerError:
        LOGGER.error(f'Ошибка запроса списка контактов пользователя {username}.')
    else:
        for contact in contact_list:
            database.add_contact(contact)
