"""Функции для использования server.py"""

import json
import sys
sys.path.append('../')
from srv_variables import MAX_DATA, ENCODING
from custom.errors import IncorrectDataReceivedError, NonDictInputError
from custom.decorators import Log


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
def get_help():
    """
    Печатает справочную информацию.
    """
    print('Доступные команды:')
    print('1 - вывести подсказки по командам.')
    print('2 - список всех пользователей.')
    print('3 - список пользователей online.')
    print('4 - история посещений пользователя.')
    print('5 - выйти из программы.')


@Log()
def main_loop(database):
    """
    Основное меню сервера.
    :param database: база данных.
    :return:
    """
    while True:
        get_help()
        command = input('Выберите действие (помощь "1"): ')
        if command == '1':
            get_help()
        elif command == '2':
            for user in database.get_all_users():
                print(f'Пользователь: {user.username}. Последний вход: {user.last_login}.')
        elif command == '3':
            for user in database.get_all_active_users():
                print(f'Пользователь: {user.username} ({user.ip_address}:{user.port}).'
                      f' Время подключения: {user.login_time}.')
        elif command == '4':
            username = input('Введите имя пользователя для просмотра истории.'
                             ' Для вывода всей истории, просто нажмите Enter: ')
            for user in database.get_connect_history(username):
                print(f'Пользователь: {user.username} ({user.ip_address}:{user.port}).'
                      f' Login: {user.login_time}. Logout: {user.logout_time}.')
        elif command == '5':
            break
        else:
            print('Команда не распознана.')
