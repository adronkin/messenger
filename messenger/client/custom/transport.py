"""The module describes the interaction with the server."""

import hmac
import sys
import time
from _hashlib import pbkdf2_hmac
from binascii import hexlify, b2a_base64
from logging import getLogger
from json import JSONDecodeError
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock
from PyQt5.QtCore import QObject, pyqtSignal
sys.path.append('../')
from client.custom.errors import ServerError
from client.custom.function import send_message, get_message
from client.custom.variables import CONFIRM_PRESENCE, USER, RESPONSE, ERROR, \
    ACTION, MESSAGE, TIME, SENDER, RECIPIENT, MESSAGE_TEXT, GET_CONTACTS_DICT, \
    DATA, GET_REGISTERED_DICT, ADD_CONTACT_DICT, ACCOUNT_NAME, DICT_MESSAGE, \
    DEL_CONTACT_DICT, EXIT_MESSAGE, ENCODING, PUBLIC_KEY, RESPONSE_511,\
    GET_PUBLIC_KEY

# The socket lock object.
SOCK_LOCK = Lock()

# Initialize the logger.
LOGGER = getLogger('client_logger')


class ClientTransport(Thread, QObject):
    """
    Class - Transport, is responsible for interacting with the server.
    """
    # New message alert and connection loss.
    new_message = pyqtSignal(dict)
    """The slot handler of incoming messages, decrypts incoming messages 
    and stores them in the message history. Asks the user if a message was 
    received not from the current interlocutor. If necessary, change the 
    interlocutor."""
    message_205 = pyqtSignal()
    """Message slot 205 - a request by the server to update directories 
    of available users and contacts. It may turn out that the current 
    person is deleted, you need to check this and close the chat with a 
    warning. Otherwise, just update the contact list without giving a warning 
    to the user."""
    connection_loss = pyqtSignal()
    """The slot handler is a loss of connection to the server. 
    Gives a warning window and terminates the application."""

    def __init__(self, ip_address, port, database, username, password, keys):
        # Ancestor constructor call.
        Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        self.password = password
        self.keys = keys
        # Server socket.
        self.client_sock = None

        # Establish a connection.
        self.connection_init(ip_address, port)

        try:
            self.get_registered_user_from_server()
            self.get_contact_list_from_server()
        except OSError as err:
            if err.errno:
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
        The method initiates a connection to the server.\n
        :param str ip_address: server IP-address.
        :param int port: server port.
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

        LOGGER.info(f'Установлено соединение с сервером {ip_address}:{port}.')

        # Start Authorization Procedure.
        # Get password hash.
        password_bytes = self.password.encode(ENCODING)
        salt = self.username.lower().encode(ENCODING)
        password_hash = pbkdf2_hmac('sha512', password_bytes, salt, 10000)
        password_hash_string = hexlify(password_hash)

        # Get the public key and decode it from bytes.
        public_key = self.keys.publickey().export_key().decode('ascii')

        # Authorization on the server.
        with SOCK_LOCK:
            presence_dict = CONFIRM_PRESENCE
            presence_dict[USER] = self.username
            presence_dict[PUBLIC_KEY] = public_key
        # Send server confirmation of presence.
            try:
                send_message(self.client_sock, presence_dict)
                server_answer = get_message(self.client_sock)
                if RESPONSE in server_answer:

                    if server_answer[RESPONSE] == 400 and ERROR in server_answer:
                        LOGGER.error(f'Сервер не смог обработать клиентский'
                                     f' запрос. Получен ответ "Response 400:'
                                     f' {server_answer[ERROR]}".')
                        raise ServerError(server_answer[ERROR])

                    elif server_answer[RESPONSE] == 511 and DATA in server_answer:
                        answer_data = server_answer[DATA]
                        answer_hash = hmac.new(
                            password_hash_string,
                            answer_data.encode(ENCODING)
                        )
                        hash_digest = answer_hash.digest()
                        client_answer = RESPONSE_511
                        client_answer[DATA] = b2a_base64(hash_digest).decode('ascii')
                        send_message(self.client_sock, client_answer)
                        self.receive_message(get_message(self.client_sock))

            except (OSError, JSONDecodeError):
                LOGGER.critical('Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером.')

    def transport_shutdown(self):
        """
        The method of closing the connection, sends an exit message.
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
        The function processes the server response.\n
        :param dict message: message from the server.
        """
        LOGGER.debug(f'Обработка сообщения от сервера {message}.')

        if RESPONSE in message:
            if message[RESPONSE] == 200:
                LOGGER.info('Сообщение корректно обработано. Response 200: OK.')
                return
            elif message[RESPONSE] == 400 and ERROR in message:
                LOGGER.error(f'Сервер не смог обработать клиентский запрос. '
                             f'Получен ответ "Response 400: {message[ERROR]}".')
                raise ServerError(message[ERROR])
            elif message[RESPONSE] == 205:
                self.get_contact_list_from_server()
                self.get_registered_user_from_server()
                self.message_205.emit()
            else:
                LOGGER.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')

        # If this message from the user is added to the database
        # and give a signal about a new message.
        elif ACTION in message and message[ACTION] == MESSAGE \
                and TIME in message and SENDER in message \
                and RECIPIENT in message and MESSAGE_TEXT in message \
                and message[RECIPIENT] == self.username:
            LOGGER.info(f'Пользователь {self.username} получил сообщение'
                        f' {message[MESSAGE_TEXT]} от пользователя'
                        f' {message[SENDER]}.')
            self.new_message.emit(message)

    def get_contact_list_from_server(self):
        """
        The method requests a list of user contacts from the server.\n
        :return: user contact list.
        """
        self.database.clear_contacts()
        LOGGER.debug(f'Запрос списка контактов пользователя {self.username}.')
        get_contacts_dict = GET_CONTACTS_DICT
        get_contacts_dict[USER] = self.username
        LOGGER.debug(f'Сформирован запрос {get_contacts_dict}.')

        # Send a message to the server.
        with SOCK_LOCK:
            send_message(self.client_sock, get_contacts_dict)
            # Get a response from the server.
            server_answer = get_message(self.client_sock)
        LOGGER.debug(f'Получен ответ {server_answer}.')

        if RESPONSE in server_answer and server_answer[RESPONSE] == 202 \
                and DATA in server_answer:
            for contact in server_answer[DATA]:
                self.database.add_contact(contact)
        else:
            LOGGER.error('Не удалось обновить список контактов.')

    def get_registered_user_from_server(self):
        """
        The method requests from the server a list of registered users.\n
        :return: list of registered users.
        """
        LOGGER.debug(f'Запрос зарегистрированных пользователей {self.username}.')
        get_registered_dict = GET_REGISTERED_DICT
        get_registered_dict[USER] = self.username
        # Send a message to the server.
        LOGGER.debug(f'Сформирован запрос {get_registered_dict}.')
        with SOCK_LOCK:
            send_message(self.client_sock, get_registered_dict)
            # Get a response from the server.
            server_answer = get_message(self.client_sock)
        LOGGER.debug(f'Получен ответ {server_answer}.')
        if RESPONSE in server_answer and server_answer[RESPONSE] == 202 \
                and DATA in server_answer:
            self.database.add_register_users(server_answer[DATA])
            return server_answer[DATA]
        else:
            LOGGER.error('Не удалось обновить список известных пользователей.')

    def add_contact_to_server(self, contact):
        """
        The method sends information about adding a contact to the server.\n
        :param str contact: username to add to your contact list.
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
        :param str contact: username to remove from the contact list.
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
        Method for sending a message to the server.\n
        :param obj recipient: socket object.
        :param str message: message to the recipient.
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

    def get_key_from_server(self, username):
        """
        The method requests the public key from the server.\n
        :param str username: username.
        """
        LOGGER.debug(f'Запрос публичного ключа для {username}.')
        dict_message = GET_PUBLIC_KEY
        dict_message[USER] = username
        with SOCK_LOCK:
            send_message(self.client_sock, dict_message)
            server_answer = get_message(self.client_sock)
        if RESPONSE in server_answer and server_answer[RESPONSE] == 511 \
                and DATA in server_answer:
            return server_answer[DATA]
        LOGGER.error(f'Не удалось получить ключ собеседника{username}.')

    def run(self):
        """
        Method for starting the process of receiving messages from the server.
        """
        LOGGER.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            # If you do not delay, sending can wait a long time until the socket is released.
            time.sleep(1)
            message = None
            with SOCK_LOCK:
                try:
                    self.client_sock.settimeout(0.5)
                    message = get_message(self.client_sock)
                except OSError as err:
                    if err.errno:
                        LOGGER.critical('Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_loss.emit()
                except (ConnectionError, ConnectionResetError,
                        ConnectionAbortedError, TypeError, JSONDecodeError):
                    LOGGER.critical('Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_loss.emit()
                finally:
                    self.client_sock.settimeout(5)

            if message:
                LOGGER.debug(f'Принято сообщение с сервера: {message}')
                self.receive_message(message)
