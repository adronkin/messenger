"""The module describes the server functionality"""

import hmac
import os
import sys
from binascii import hexlify, a2b_base64
from configparser import ConfigParser
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM
from select import select
from logging import getLogger
from threading import Thread, Lock
from PyQt5.QtWidgets import QApplication, QMessageBox
sys.path.append('../')
from gui.main_window import MainWindow
from gui.config_window import ConfigWindow
from custom.srv_parse_args import args_parser
from custom.srv_metaclass import ServerVerified
from database.srv_databese import ServerDataBase
from srv_descriptors.address import Address
from srv_descriptors.port import Port
from custom.srv_function import get_message, send_message
from custom.srv_variables import MAX_QUEUE, ACTION, PRESENCE, TIME, ERROR, USER, MESSAGE, \
    MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_400, EXIT, RECIPIENT, DEL_CONTACT, ACCOUNT_NAME, \
    ADD_CONTACT, GET_CONTACTS, RESPONSE_202, DATA, GET_REGISTERED, RESPONSE_205, RESPONSE, \
    PUBLIC_KEY_REQUEST, RESPONSE_511, PUBLIC_KEY
import log.log_config

# Logger initialization.
LOGGER = getLogger('server_logger')


class Server(Thread, metaclass=ServerVerified):
    # Descriptors.
    address = Address()
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.address = listen_address
        self.port = listen_port
        self.database = database

        self.sock = None

        # Sockets.
        self.listen_sockets = None
        self.error_sockets = None

        # A list of clients.
        self.clients = []
        # A dictionary with user names and sockets.
        self.names = dict()

        # Flag to continue work.
        self.running = True

        super().__init__()

    def init_socket(self):
        """
        The method preparing a server socket.
        :return:
        """
        LOGGER.info(f'Сервер запущен с параметрами - {self.address}:{self.port}')
        # Create a TCP socket (AF_INET - network socket, SOCK_STREAM - work with TCP packets).
        server_sock = socket(AF_INET, SOCK_STREAM)
        server_sock.bind((self.address, self.port))
        server_sock.settimeout(0.5)
        # Put the server in standby mode (listening to the port).
        self.sock = server_sock
        self.sock.listen(MAX_QUEUE)

    def run(self):
        """
        The main server loop.
        :return:
        """
        # Socket initialization.
        self.init_socket()

        while self.running:
            # Accept Connection Request.
            try:
                client_sock, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                LOGGER.info(f'Установлено соединение с клиентом {client_address}')
                client_sock.settimeout(5)
                self.clients.append(client_sock)

            # List of objects ready for input.
            clients_senders = []

            try:
                if self.clients:
                    # Request information on readiness for input and output.
                    clients_senders, self.listen_sockets, self.error_sockets = select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                LOGGER.info(f'Ошибка работы с сокетами: {err.error}.')

            # Receive messages, if an error is returned,
            # exclude the client from the list of clients.
            if clients_senders:
                for client_with_message in clients_senders:
                    try:
                        self.processing_message(
                            get_message(client_with_message), client_with_message)
                    except (OSError, JSONDecodeError, TypeError):
                        self.remove_client(client_with_message)

    def message_handler(self, message):
        """
        The method processes the message. Accepts a message dictionary,
        list of users and listening sockets. Sends a message to the recipient.
        :param {str} message: message to send.
        :return:
        """
        if message[RECIPIENT] in self.names \
                and self.names[message[RECIPIENT]] in self.listen_sockets:
            try:
                send_message(self.names[message[RECIPIENT]], message)
                LOGGER.info(f'Сообщение от пользователя {message[SENDER]}'
                            f' передано пользователю {message[RECIPIENT]}.')
            except OSError:
                self.remove_client(message[RECIPIENT])

        elif message[RECIPIENT] in self.names \
                and self.names[message[RECIPIENT]] not in self.listen_sockets:
            LOGGER.error(f'Доставка невозможна. Связь с клиентом {message[RECIPIENT]} потеряна.')
            self.remove_client(self.names[message[RECIPIENT]])

        else:
            LOGGER.error(f'Отправка сообщения невозможна. Пользователь с именем'
                         f' {message[RECIPIENT]} не зарегистрирован на сервере.')

    def processing_message(self, message, client):
        """
        The method processes the message.
        :param {str} message: message.
        :param client: client.
        :return:
        """
        LOGGER.debug(f'Обработка сообщения от клиента - {message}')

        # If a PRESENCE message.
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            self.user_authorization(message, client)

        # If message.
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and SENDER in message and RECIPIENT in message and MESSAGE_TEXT in message \
                and client == self.names[message[SENDER]]:
            if message[RECIPIENT] in self.names:
                # Сохраняем сообщение в БД
                self.database.save_message(message[SENDER],
                                           message[RECIPIENT],
                                           message[MESSAGE_TEXT])
                self.message_handler(message)
                try:
                    send_message(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                server_answer = RESPONSE_400
                server_answer[ERROR] = f'Пользователь {message[RECIPIENT]} не зарегистрирован.'
                try:
                    send_message(client, server_answer)
                except OSError:
                    pass
            return

        # If the user wants to shut down.
        elif ACTION in message and message[ACTION] == EXIT and TIME in message and USER in message \
                and client == self.names[message[USER]]:
            self.remove_client(client)

        # If the user requests a contact list.
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            server_answer = RESPONSE_202
            server_answer[DATA] = self.database.get_contact_list(message[USER])
            LOGGER.debug(f'Пользователь {message[USER]} запросил список контактов.')
            try:
                send_message(client, server_answer)
            except OSError:
                self.remove_client(client)

        # If the user adds to the contact list.
        elif ACTION in message and message[ACTION] == ADD_CONTACT and TIME in message \
                and USER in message and ACCOUNT_NAME in message \
                and client == self.names[message[USER]]:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            LOGGER.debug(f'Пользователь {message[USER]} добавил'
                         f' {message[ACCOUNT_NAME]} в список контактов.')
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        # If the user removes from the contact list.
        elif ACTION in message and message[ACTION] == DEL_CONTACT and TIME in message \
                and USER in message and ACCOUNT_NAME in message \
                and client == self.names[message[USER]]:
            self.database.del_contact(message[USER], message[ACCOUNT_NAME])
            LOGGER.debug(f'Пользователь {message[USER]} удалил'
                         f' {message[ACCOUNT_NAME]} из списка контактов.')
            try:
                send_message(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)

        # If the user requests a list of known users.
        elif ACTION in message and message[ACTION] == GET_REGISTERED and USER in message \
                and self.names[message[USER]] == client:
            server_answer = RESPONSE_202
            server_answer[DATA] = [user[0] for user in self.database.get_all_users()]
            # TODO оптимизировать запрос.
            LOGGER.debug(f'Пользователь {message[USER]} запросил список'
                         f' зарегистрированных пользователей.')
            try:
                send_message(client, server_answer)
            except OSError:
                self.remove_client(client)

        # If the user requests a public key.
        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and USER in message:
            server_answer = RESPONSE_511
            server_answer[DATA] = self.database.get_key(message[USER])
            # If there is no key yet, send 400 (the user has never logged in).
            if server_answer[DATA]:
                try:
                    send_message(client, server_answer)
                except OSError:
                    self.remove_client(client)
            else:
                server_answer = RESPONSE_400
                server_answer[ERROR] = 'Нет публичного ключа.'
                try:
                    send_message(client, server_answer)
                except OSError:
                    self.remove_client(client)

        else:
            server_answer = RESPONSE_400
            server_answer[ERROR] = 'Bad request.'
            LOGGER.debug(f'Получен некорректный запрос от клиента {client.getpeername()},'
                         f' отправлен ответ {server_answer}.')
            try:
                send_message(client, server_answer)
            except OSError:
                self.remove_client(client)

    def user_authorization(self, message, sock):
        """
        User authorization method on the server.
        :param {dict} message: user message.
        :param sock: user socket.
        :return:
        """
        # If the username is taken, return 400.
        if message[USER] in self.names.keys():
            server_answer = RESPONSE_400
            server_answer[ERROR] = 'Имя пользователя занято.'
            LOGGER.error(f'Попытка подключения клиента {sock.getpeername()} используя'
                         f' занятое имя пользователя. Отправлен ответ {RESPONSE_400}.')
            try:
                send_message(sock, server_answer)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        # Check that the user is registered on the server.
        if not self.database.check_user(message[USER]):
            server_answer = RESPONSE_400
            server_answer[ERROR] = 'Пользователь не зарегистрирован.'
            try:
                send_message(sock, server_answer)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        # Otherwise, answer 511 and start the authorization procedure.
        else:
            auth_answer = RESPONSE_511
            # A set of bytes in a hex representation.
            random_str = hexlify(os.urandom(64))
            # Bytes cannot be added to the dictionary, decode.
            auth_answer[DATA] = random_str.decode('ascii')
            # Create a password hash and a string with a random string,
            # save the server version of the key.
            password_hash = hmac.new(self.database.get_pass_hash(message[USER]), random_str)
            digest = password_hash.digest()

            try:
                send_message(sock, auth_answer)
                answer = get_message(sock)
            except OSError:
                sock.close()
                return
            client_digest = a2b_base64(answer[DATA])
            # If the client’s answer is correct, then save it to the list of users.
            if RESPONSE in answer and answer[RESPONSE] == 511 \
                    and hmac.compare_digest(digest, client_digest):
                self.names[message[USER]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    send_message(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER])
                # Add user to active list. Save the public key if it has changed.
                self.database.user_login(message[USER], client_ip, client_port, message[PUBLIC_KEY])
            else:
                server_answer = RESPONSE_400
                server_answer[ERROR] = 'Неверный пароль.'
                try:
                    send_message(sock, server_answer)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def remove_client(self, client):
        """
        The method searches for a client in the client dictionary
        and removes it from the lists and databases.
        :param client:
        :return:
        """
        LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
        # Ищем и удаляем клиента из словаря клиентов.
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def send_update_list(self):
        """
        The method sends a message 205 asking customers to update the lists.
        :return:
        """
        for client in self.names:
            try:
                send_message(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])
        LOGGER.debug('Ответ 205 отправлен пользователям.')


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

    # Создаем графическое окружение для сервера.
    server_app = QApplication(sys.argv)
    main_window = MainWindow(server, database)

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
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом.')
        else:
            # TODO добавить проверку корректности IP-адреса.
            config['SETTINGS']['default_ip'] = config_window.ip_address_field.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = config_window.port_field.text()
                # Записываем новы порт в файл.
                with open(os.path.join(dir_path, 'server.ini'), 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'Ok', 'Настройки сохранены.')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536.')

    # Связываем кнопки с процедурами.
    main_window.setting_button.triggered.connect(server_config)

    # Запускаем GUI.
    server_app.exec_()

    # By closing the windows, we stop the message handler.
    server_app.running = False


if __name__ == '__main__':
    main()

# TODO сервер падает если завершить работу клиента ctrl+D.
# TODO удается зарегать пользователя без пароля.
