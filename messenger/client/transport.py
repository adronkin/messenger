"""The module describes the interaction with the server"""

import sys
import time
from logging import getLogger
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal
sys.path.append('../')
from custom.errors import ServerError
from clt_function import send_message, get_message
from clt_variables import SOCK_LOCK, CONFIRM_PRESENCE, USER, PRESENCE, RESPONSE, ERROR, ACTION, \
    MESSAGE, TIME, SENDER, RECIPIENT, MESSAGE_TEXT, GET_CONTACTS_DICT, DATA, GET_REGISTERED_DICT, \
    ADD_CONTACT_DICT, ACCOUNT_NAME, DEL_CONTACT_DICT, EXIT_MESSAGE, DICT_MESSAGE
import log.log_config

# Initialize the logger.
LOGGER = getLogger('client_logger')


class ClientTransport(Thread, QObject):
    """
    Class - Transport, is responsible for interacting with the server.
    """
    # New message alert and connection loss.
    new_message = pyqtSignal(str)
    connection_loss = pyqtSignal()

    def __init__(self, ip_address, port, database, username):
        # Ancestor constructor call.
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        # Server socket.
        self.client_sock = None

        # Establish a connection.
        self.connection_init(ip_address, port)

        try:
            self.get_registered_user_from_server()
            self.get_contact_list_from_server()
        except OSError as error:
            if error.errno:
                LOGGER.critical('Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером.')
            LOGGER.error('Timeout соединения при обновлении списков пользователей.')
        except JSONDecodeError:
            LOGGER.critical('Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        # Flag to continue the work of transport.
        self.running = True

    def connection_init(self, ip_address, port):
        """
        The method initiates a connection to the server.
        :param {str} ip_address: server IP-address.
        :param {int} port: server port
        :return:
        """
        # Create a socket (AF_INET - network socket, SOCK_STREAM - work with TCP packets).
        self.client_sock = socket(AF_INET, SOCK_STREAM)
        # A timeout is required to free the socket.
        self.client_sock.settimeout(5)

        # Connect, 5 connection attempts, set success flag to True if possible.
        connected = False
        for attempt in range(5):
            LOGGER.info(f'Попытка подключения №{attempt + 1}.')
            try:
                self.client_sock.connect((ip_address, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)

        # If connection failed, return an exception.
        if not connected:
            LOGGER.critical('Не удалось установить соединение с сервером.')
            raise ServerError('Не удалось установить соединение с сервером.')

        LOGGER.debug('Установлено соединение с сервером.')

        # Send server confirmation of presence.
        try:
            with SOCK_LOCK:
                send_message(self.client_sock, self.confirm_presence())
                self.receive_message(get_message(self.client_sock))
        except (OSError, JSONDecodeError):
            LOGGER.critical('Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером.')

        LOGGER.info(f'Установлено соединение с сервером {ip_address}:{port}.')

    def confirm_presence(self):
        """
        The function generates a dictionary to send a message about the user's presence.
        :return {dict}: presence message dict.
        """
        message = CONFIRM_PRESENCE
        message[USER] = self.username
        LOGGER.info(f'Сгенерировано {PRESENCE} сообщение для пользователя {self.username}.')
        return message

    def transport_shutdown(self):
        """
        The method of closing the connection, sends an exit message.
        :return:
        """
        self.running = False
        exit_message = EXIT_MESSAGE
        exit_message[USER] = self.username
        # Send a message to the server.
        with SOCK_LOCK:
            try:
                send_message(self.client_sock, exit_message)
            except OSError:
                pass
        LOGGER.debug('Клиент завершает работу.')
        time.sleep(0.5)

    def receive_message(self, message):
        """
        The function processes the server response.
        :param {dict} message: message from the server.
        :return:
        """
        LOGGER.debug(f'Обработка сообщения от сервера {message}.')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                LOGGER.info('Сообщение корректно обработано. Response 200: OK')
            elif message[RESPONSE] == 400 and ERROR in message:
                LOGGER.error(f'Сервер не смог обработать клиентский запрос. '
                             f'Получен ответ "Response 400: {message[ERROR]}".')
                raise ServerError(f'400: {message[ERROR]}')
            else:
                # raise ReqFieldMissingError(RESPONSE)
                LOGGER.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')
        # If this message from the user is added to the database
        # and give a signal about a new message.
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                and SENDER in message and RECIPIENT in message and MESSAGE_TEXT in message \
                and message[RECIPIENT] == self.username:
            LOGGER.info(f'Пользователь {self.username} получил сообщение {message[MESSAGE_TEXT]}'
                        f' от пользователя {message[SENDER]}.')
            self.database.save_message(message[SENDER], message[RECIPIENT], message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def get_contact_list_from_server(self):
        """
        The method requests a list of user contacts from the server.
        :return {list}: user contact list.
        """
        LOGGER.debug(f'Запрос списка контактов пользователя {self.username}.')
        get_contacts_dict = GET_CONTACTS_DICT
        get_contacts_dict[USER] = self.username
        # Send a message to the server.
        with SOCK_LOCK:
            send_message(self.client_sock, get_contacts_dict)
            # Get a response from the server.
            server_answer = get_message(self.client_sock)
        if RESPONSE in server_answer and server_answer[RESPONSE] == 202 and DATA in server_answer:
            for contact in server_answer[DATA]:
                self.database.add_contact(contact)
        else:
            LOGGER.error('Не удалось обновить список контактов.')

    def get_registered_user_from_server(self):
        """
        The method requests from the server a list of registered users.
        :return {list}: list of registered users.
        """
        LOGGER.debug('Запрос зарегистрированных пользователей.')
        get_registered_dict = GET_REGISTERED_DICT
        get_registered_dict[USER] = self.username
        # Send a message to the server.
        with SOCK_LOCK:
            send_message(self.client_sock, get_registered_dict)
            # Get a response from the server.
            server_answer = get_message(self.client_sock)
        if RESPONSE in server_answer and server_answer[RESPONSE] == 202 and DATA in server_answer:
            self.database.add_register_users(server_answer[DATA])
        else:
            LOGGER.error('Не удалось обновить список известных пользователей.')

    def add_contact_to_server(self, contact):
        """
        The method sends information about adding a contact to the server.
        :param {str} contact: username to add to your contact list.
        :return:
        """
        LOGGER.debug(f'Создание контакта {contact}.')
        add_contact_dict = ADD_CONTACT_DICT
        add_contact_dict[USER] = self.username
        add_contact_dict[ACCOUNT_NAME] = contact
        # Send a message to the server.
        with SOCK_LOCK:
            send_message(self.client_sock, add_contact_dict)
            # Get a response from the server.
            self.receive_message(get_message(self.client_sock))

    def remove_contact_to_server(self, contact):
        """
        The function sends contact deletion information to the server.
        :param {str} contact: username to remove from the contact list.
        :return:
        """
        LOGGER.debug(f'Удаление контакта {contact}.')
        del_contact_dict = DEL_CONTACT_DICT
        del_contact_dict[USER] = self.username
        del_contact_dict[ACCOUNT_NAME] = contact
        # Send a message to the server.
        with SOCK_LOCK:
            send_message(self.client_sock, del_contact_dict)
            # Get a response from the server.
            self.receive_message(get_message(self.client_sock))

    def create_message(self, recipient, message):
        """
        Method for sending a message to the server.
        :param {obj} recipient: socket object.
        :param {str} message: message to the recipient.
        :return:
        """
        dict_message = DICT_MESSAGE
        dict_message[SENDER] = self.username
        dict_message[RECIPIENT] = recipient
        dict_message[MESSAGE_TEXT] = message
        LOGGER.debug(f'Сформирован словарь-сообщение: {dict_message}.')
        # Send a message to the server.
        with SOCK_LOCK:
            send_message(self.client_sock, dict_message)
            self.receive_message(get_message(self.client_sock))
            LOGGER.info(f'Сообщение отправлено пользователю {recipient}.')

    def run(self):
        """
        Method for starting the process of receiving messages from the server.
        :return:
        """
        LOGGER.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            # If you do not delay, sending can wait a long time until the socket is released.
            time.sleep(1)
            with SOCK_LOCK:
                try:
                    self.client_sock.settimeout(0.5)
                    message = get_message(self.client_sock)
                except OSError as error:
                    if error.errno:
                        LOGGER.critical('Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_loss.emit()
                except (ConnectionError, ConnectionResetError,
                        ConnectionAbortedError, TypeError, JSONDecodeError):
                    LOGGER.critical('Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_loss.emit()
                else:
                    LOGGER.debug(f'Принято сообщение с сервера: {message}')
                    self.receive_message(message)
                finally:
                    self.client_sock.settimeout(5)
