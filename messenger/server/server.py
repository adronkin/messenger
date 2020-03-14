"""Программа-сервер"""

import os
import sys
from configparser import ConfigParser
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from logging import getLogger
from threading import Thread, Lock
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox
from srv_gui import MainWindow, gui_active_users, ConfigWindow
sys.path.append('../')
from srv_parse_args import args_parser
from srv_metaclass import ServerVerified
from srv_databese import ServerDataBase
from srv_descriptors.address import Address
from srv_descriptors.port import Port
from srv_function import get_message, send_message
from srv_variables import MAX_QUEUE, ACTION, PRESENCE, TIME, ERROR, USER, MESSAGE, MESSAGE_TEXT, \
    SENDER, RESPONSE_200, RESPONSE_300, RESPONSE_400, EXIT, RECIPIENT, DEL_CONTACT, ACCOUNT_NAME, \
    ADD_CONTACT, GET_CONTACTS, RESPONSE_202, DATA, GET_REGISTERED
import log.log_config


# Инициализируем логгера.
LOGGER = getLogger('server_logger')

# Флаг что был подключён новый пользователь, нужен чтобы не мучить BD
# постоянными запросами на обновление.
NEW_CONNECTION = False
CON_FLAG_LOCK = Lock()


class Server(Thread, metaclass=ServerVerified):
    # Дескрипторы
    address = Address()
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.address = listen_address
        self.port = listen_port
        self.database = database

        # Список клиентов, очередь сообщений, словарь с именами и сокетами пользователей
        self.clients = []
        self.messages = []
        self.names = dict()

        super().__init__()

    def init_socket(self):
        """
        Подготовка сокета сервера.
        :return:
        """
        LOGGER.info(
            f'Сервер запущен с параметрами - {self.address}:{self.port}')
        # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.bind((self.address, self.port))
        server_sock.settimeout(0.5)

        # Переводим сервер в режим ожидания запросов (слушаем порт).
        self.sock = server_sock
        self.sock.listen(MAX_QUEUE)

    def run(self):
        """
        Основной цикл сервера.
        :return:
        """
        # Инициализация сокета
        self.init_socket()

        while True:
            # Принимаем запрос на соединение
            try:
                client_sock, address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соединение с клиентом {address}')
                self.clients.append(client_sock)

            # Списки объектов готовых к вводу, выводу и проверяемых на наличие исключений
            clients_senders = []
            clients_recipients = []
            errors_lst = []

            try:
                if self.clients:
                    # Запрашиваем информацию о готовности к вводу и выводу
                    clients_senders, clients_recipients, errors_lst = select(
                        self.clients, self.clients, [], 0)
            except OSError as error:
                print(f'Ошибка работы с сокетами: {error}.')

            # Принимаем сообщения, если возвращена ошибка, исключаем клиента из списка clients.
            if clients_senders:
                for client_with_message in clients_senders:
                    try:
                        self.processing_message(
                            get_message(client_with_message), client_with_message)
                    except OSError:
                        LOGGER.info(
                            f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        # Ищем и удаляем клиента из словаря клиентов.
                        for name in self.names:
                            if self.names[name] == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                        self.clients.remove(client_with_message)

            # Если есть сообщения для отправки, обрабатываем.
            for message in self.messages:
                try:
                    self.message_handler(message, clients_recipients)
                except (ConnectionAbortedError, ConnectionError,
                        ConnectionResetError, ConnectionRefusedError):
                    LOGGER.info(
                        f'Клиент {message[RECIPIENT]} отключился от сервера.')
                    no_user_dict = RESPONSE_300
                    no_user_dict[ERROR] = f'Пользователь {message[RECIPIENT]}' \
                                          f' отключился от сервера.'
                    send_message(self.names[message[SENDER]], no_user_dict)
                    self.clients.remove(self.names[message[RECIPIENT]])
                    del self.names[message[RECIPIENT]]
                    # Вносим информацию в БД.
                    self.database.user_logout(message[RECIPIENT])
            self.messages.clear()

    def message_handler(self, message, listen_sock):
        """
        Функция обрабатывает сообщение. Принимает словарь сообщения,
        список пользователей и слушающие сокеты. Отправляет сообщение адресату.
        :param {str} message: сообщение для обработки.
        :param listen_sock: список клиентов.
        :return:
        """
        if message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] in listen_sock:
            send_message(self.names[message[RECIPIENT]], message)
            LOGGER.info(f'Сообщение от пользователя {message[SENDER]}'
                        f' передано пользователю {message[RECIPIENT]}.')
        elif message[RECIPIENT] in self.names and self.names[message[RECIPIENT]] not in listen_sock:
            raise ConnectionError
        else:
            no_user_dict = RESPONSE_300
            no_user_dict[ERROR] = f'Пользователь с именем {message[RECIPIENT]}' \
                                  f' не зарегистрирован на сервере.'
            send_message(self.names[message[SENDER]], no_user_dict)
            LOGGER.error(f'{no_user_dict[ERROR]} Отправка сообщения невозможна.')
            LOGGER.debug(f'Пользователю {message[SENDER]} отправлен ответ {no_user_dict}')

    def processing_message(self, message, client):
        """
        Проверяет корректность сообщения.
        :param {str} message: сообщение.
        :param client: список клиентов.
        :return:
        """
        global NEW_CONNECTION
        LOGGER.debug(f'Обработка сообщения от клиента - {message}')

        # Если PRESENCE-сообщение, проверяем и отвечаем.
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            # Проверяем зарегистрирован пользователь или нет
            if message[USER] not in self.names.keys():
                self.names[message[USER]] = client
                send_message(client, RESPONSE_200)
                LOGGER.info(f'Клиент {client.getpeername()} подключился.'
                            f' Отправлен ответ {RESPONSE_200}')
                client_ip, client_port = client.getpeername()
                # фиксируем login в БД
                self.database.user_login(message[USER], client_ip, client_port)
                with CON_FLAG_LOCK:
                    NEW_CONNECTION = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя занято.'
                send_message(client, response)
                LOGGER.error(f'Попытка подключения клиента {client.getpeername()} используя'
                             f' занятое имя пользователя. Отправлен ответ {RESPONSE_400}')
                self.clients.remove(client)
                client.close()
            return

        # Если сообщение, то проверяем и добавляем его в очередь сообщений.
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and SENDER in message and RECIPIENT in message and MESSAGE_TEXT in message:
            if message[RECIPIENT] in self.names:
                self.messages.append(message)
                # Сохраняем сообщение в БД
                self.database.save_message(message[SENDER],
                                           message[RECIPIENT],
                                           message[MESSAGE_TEXT])
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = f'Пользователь {message[RECIPIENT]} не зарегистрирован.'
                send_message(client, response)
            return

        # Если пользователь хочет завершить работу.
        elif ACTION in message and message[ACTION] == EXIT and TIME in message and USER in message:
            LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
            self.clients.remove(self.names[message[USER]])
            self.names[message[USER]].close()
            # Фиксируем logout в БД.
            self.database.user_logout(message[USER])
            del self.names[message[USER]]
            with CON_FLAG_LOCK:
                NEW_CONNECTION = True
            return

        # Если пользователь запрашивает список контактов.
        elif ACTION in message and message[ACTION] == GET_CONTACTS and TIME in message \
                and USER in message:
            server_answer = RESPONSE_202
            server_answer[DATA] = self.database.get_contact_list(message[USER])
            LOGGER.debug(f'Пользователь {message[USER]} запросил список контактов.')
            send_message(client, server_answer)

        # Если пользователь добавляет в список контактов.
        elif ACTION in message and message[ACTION] == ADD_CONTACT and TIME in message \
                and USER in message and ACCOUNT_NAME in message:
            if not self.database.check_contact(message[USER], message[ACCOUNT_NAME]):
                self.database.add_contact(message[USER], message[ACCOUNT_NAME])
                LOGGER.debug(f'Пользователь {message[USER]} добавил'
                             f' {message[ACCOUNT_NAME]} в список контактов.')
                send_message(client, RESPONSE_200)
            else:
                LOGGER.debug(f'Пользователь {message[ACCOUNT_NAME]} уже есть в '
                             f'списке контактов пользователя {message[USER]}.')
                server_answer = RESPONSE_300
                server_answer[ERROR] = f'Пользователь {message[ACCOUNT_NAME]}' \
                                       f' есть в списке контактов.'
                send_message(client, RESPONSE_300)

        # Если пользователь удаляет из списка контактов.
        elif ACTION in message and message[ACTION] == DEL_CONTACT and TIME in message \
                and USER in message and ACCOUNT_NAME in message:
            self.database.del_contact(message[USER], message[ACCOUNT_NAME])
            LOGGER.debug(f'Пользователь {message[USER]} удалил'
                         f' {message[ACCOUNT_NAME]} из списка контактов.')
            send_message(client, RESPONSE_200)

        # Если пользователь запрашивает список известных пользователей.
        elif ACTION in message and message[ACTION] == GET_REGISTERED and TIME in message \
                and USER in message:
            server_answer = RESPONSE_202
            server_answer[DATA] = [user[0] for user in self.database.get_all_users()]
            # TODO оптимизировать запрос.
            LOGGER.debug(f'Пользователь {message[USER]}'
                         f' запросил список зарегистрированных пользователей.')
            send_message(client, server_answer)

        else:
            response = RESPONSE_400
            response[ERROR] = 'Bad request.'
            LOGGER.debug(f'Получен некорректный запрос от клиента {client.getpeername()},'
                         f' отправлен ответ {response}.')
            send_message(client, response)
            return


def main():
    """
    Запуск сервера.
    :return:
    """
    # Загружаем файл конфигурации сервера.
    config = ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server.ini')

    # Парсим параметры из командной строки или установка значений по умолчанию.
    listen_address, listen_port = args_parser(config['SETTINGS']['default_ip'],
                                              config['SETTINGS']['default_port'])

    # Инициализируем БД.
    database = ServerDataBase(os.path.join(config['SETTINGS']['db_path'],
                                           config['SETTINGS']['db_file']))

    # Создаем экземпляр сервера.
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Запуск основного меню сервера.
    # main_loop(database)

    # Создаем графическое окружение для сервера.
    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    # Инициализируем параметры окна.
    main_window.statusBar().showMessage('Server Working')
    main_window.active_clients_table.setModel(gui_active_users(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def active_list_update():
        """
        Функция для обновления списка активных пользователей в GUI сервера.
        Проверяет флаг подключения, если необходимо, обновляет список подключенных пользователей.
        :return:
        """
        global NEW_CONNECTION
        if NEW_CONNECTION:
            main_window.active_clients_table.setModel(gui_active_users(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with CON_FLAG_LOCK:
                NEW_CONNECTION = False

    def server_config():
        """
        Функция создает окно настроек сервера.
        :return:
        """
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['db_path'])
        config_window.db_file_name.insert(config['SETTINGS']['db_file'])
        config_window.ip_address_field.insert(config['SETTINGS']['default_ip'])
        config_window.port_field.insert(str(config['SETTINGS']['default_port']))
        config_window.save_button.clicked.connect(save_server_config)

    def save_server_config():
        """
        Функция сохранения настроек.
        :return:
        """
        global config_window
        message = QMessageBox()
        config['SETTINGS']['db_path'] = config_window.db_path.text()
        config['SETTINGS']['db_file'] = config_window.db_file_name.text()
        try:
            port = int(config_window.port_field.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            # TODO добавить проверку корректности IP-адреса.
            config['SETTINGS']['default_ip'] = config_window.ip_address_field.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = config_window.port_field.text()
                # Записываем новы порт в файл.
                with open(os.path.join(dir_path, 'server.ini'), 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'Ok', 'Настройки сохранены')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

    # Таймер обновляет список клиентов 1 раз в секунду.
    timer = QTimer()
    timer.timeout.connect(active_list_update)
    timer.start(1000)

    # Связываем кнопки с процедурами.
    main_window.refresh_button.triggered.connect(active_list_update)
    main_window.setting_button.triggered.connect(server_config)

    # Запускаем GUI.
    server_app.exec_()


if __name__ == '__main__':
    main()

# TODO сервер падает если завершить работу клиента ctrl+D.
