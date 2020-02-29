"""Программа-клиент"""

import sys
from socket import socket, AF_INET, SOCK_STREAM
from time import strftime, strptime, ctime, sleep
from logging import getLogger
from json import JSONDecodeError
from threading import Thread
from clt_parse_args import get_command_args
from clt_metaclass import ClientVerified
from clt_database import ClientDataBase
from clt_function import confirm_presence, receive_message, add_contact_to_server, send_message, \
    get_message, remove_contact_to_server, load_data_from_server
from clt_variables import ACTION, TIME, USER, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, \
    RECIPIENT, EXIT_MESSAGE, DICT_MESSAGE, CONTACT_HELP, MESSAGE_HELP, GET_HELP, DB_LOCK, SOCK_LOCK
sys.path.append('../')
import logs.client_log_config
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError

# Инициализируем логгера.
LOGGER = getLogger('client_logger')


class ClientSend(Thread, metaclass=ClientVerified):
    def __init__(self, sock, client_name, database):
        self.sock = sock
        self.client_name = client_name
        self.database = database
        super().__init__()

    def run(self):
        """
        Пользовательское меню.
        :return:
        """
        print(GET_HELP)
        while True:
            command = input('Выберите действие (помощь "2"): ')
            if command == '1':
                self.create_message()
            elif command == '2':
                print(GET_HELP)
            elif command == '3':
                self.contact_menu()
            elif command == '4':
                self.message_history()
            elif command == '5':
                with SOCK_LOCK:
                    try:
                        send_message(self.sock, self.exit_message())
                    except Exception:
                        pass
                    print('Работа программы завершена.')
                    LOGGER.info(f'Клиент {self.client_name} завершил работу.')
                # Задержка необходима, чтобы успело уйти сообщение о выходе
                sleep(0.5)
                break
            else:
                print('Команда не распознана.')

    def contact_menu(self):
        """
        Меню для работы со списком контактов.
        :return:
        """
        print(CONTACT_HELP)
        while True:
            command = input('Выберите действие (помощь "4"): ')

            if command == '1':
                with DB_LOCK:
                    contacts = self.database.get_all_contacts()
                for num, contact in enumerate(contacts):
                    print(f'{num + 1}. {contact}')

            elif command == '2':
                username = input('Введите имя пользователя: ')
                if self.database.check_registered_user(username):
                    # Вносим информацию в БД.
                    with DB_LOCK:
                        self.database.add_contact(username)
                    # Отправляем информацию на сервер.
                    with SOCK_LOCK:
                        try:
                            add_contact_to_server(self.sock, self.client_name, username)
                        except ServerError:
                            LOGGER.error('Неудачная попытка отправки информации на сервер.')
                else:
                    print(f'Пользователь {username} не зарегистрирован.')
                    LOGGER.error('Попытка добавить в контакты не зарегистрированного пользователя.')

            elif command == '3':
                username = input('Введите имя пользователя: ')
                if self.database.check_contact(username):
                    # Вносим информацию в БД.
                    with DB_LOCK:
                        self.database.delete_contact(username)
                        LOGGER.debug(f'Пользователь {username} удален из списка контактов.')
                        print(f'Пользователь {username} удален из списка контактов.')
                    # Отправляем информацию на сервер.
                    with SOCK_LOCK:
                        try:
                            remove_contact_to_server(self.sock, self.client_name, username)
                        except ServerError:
                            LOGGER.error('Неудачная попытка отправки информации на сервер.')
                else:
                    print(f'Удаление невозможно. Пользователя {username} нет в списке контактов.')
                    LOGGER.error('Попытка удаления пользователя отсутствующего в списке контактов.')

            elif command == '4':
                print(CONTACT_HELP)

            elif command == '5':
                break

            else:
                print('Команда не распознана.')

    def message_history(self):
        print(MESSAGE_HELP)
        while True:
            command = input('Выберите действие (помощь "4"): ')
            if command == '1':
                message_list = self.database.get_message_history(recipient=self.client_name)
                for msg in message_list:
                    print(f'{msg[0]} от {msg[1]}: {msg[3]}')
            elif command == '2':
                message_list = self.database.get_message_history(sender=self.client_name)
                for msg in message_list:
                    print(f'{msg[0]} пользователю {msg[2]}: {msg[3]}')
            elif command == '3':
                message_list = self.database.get_message_history()
                for msg in message_list:
                    print(f'{msg[0]} отправитель {msg[1]} получатель {msg[2]}: {msg[3]}')
            elif command == '4':
                print(MESSAGE_HELP)
            elif command == '5':
                break

    def exit_message(self):
        """
        Формирует сообщение для сервера о завершении работы пользователя.
        :return {dict}: словарь с информацией о завершении работы пользователя.
        """
        exit_message = EXIT_MESSAGE
        exit_message[USER] = self.client_name
        return exit_message

    def create_message(self):
        """
        Запрашивает текст сообщения, формирует словарь для сервера.
        При вводе команды завершает работу.
        :return:
        """
        recipient = input('Введите имя получателя: ')

        # Проверяем, что пользователь зарегистрирован на сервере.
        with DB_LOCK:
            if not self.database.check_registered_user(recipient):
                LOGGER.error(f'Попытка отправки сообщения'
                             f' незарегистрированному получателю: {recipient}.')
                print(f'Пользователь {recipient} не зарегистрирован.')
                return

        message = input('Введите сообщение: ')

        dict_message = DICT_MESSAGE
        dict_message[SENDER] = self.client_name
        dict_message[RECIPIENT] = recipient
        dict_message[MESSAGE_TEXT] = message

        LOGGER.debug(f'Сформирован словарь-сообщение: {dict_message}.')

        # Сохраняем сообщение в БД.
        with DB_LOCK:
            self.database.save_message(self.client_name, recipient, message)

        # Ждем освобождение сокета для отправки сообщения.
        with SOCK_LOCK:
            try:
                send_message(self.sock, dict_message)
                LOGGER.info(f'Сообщение отправлено пользователю {recipient}.')
            except OSError as error:
                if error.errno:
                    LOGGER.critical(f'Потеряно соединение с сервером.')
                    sys.exit(1)
                else:
                    # TODO проверить время ожидания отправки.
                    LOGGER.error('Не удалось передать сообщение. Таймаут соединения')


class ClientRead(Thread, metaclass=ClientVerified):
    def __init__(self, sock, client_name, database):
        self.sock = sock
        self.client_name = client_name
        self.database = database
        super().__init__()

    def run(self):
        """
        Функция обрабатывает сообщения от других пользователей, поступившие с сервера.
        :return:
        """
        while True:
            # Ждем секунду и снова пробуем захватить сокет. Если не сделать тут задержку,
            # то второй поток может долго ждать освобождения сокета.
            sleep(1)
            with SOCK_LOCK:
                try:
                    message = get_message(self.sock)
                except IncorrectDataReceivedError:
                    LOGGER.error('Не удалось декодировать полученное сообщение.')
                except (ConnectionError, ConnectionRefusedError,
                        ConnectionAbortedError, JSONDecodeError):
                    LOGGER.critical(f'Соединение с сервером потеряно.')
                    break
                except OSError as error:
                    # error вернет timed out, разрываем соединение если у error есть errno.
                    if error.errno:
                        LOGGER.critical(f'Соединение с сервером потеряно.')
                        break
                else:
                    if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                            and SENDER in message and RECIPIENT in message \
                            and MESSAGE_TEXT in message and message[RECIPIENT] == self.client_name:
                        message_time = strftime("%d.%m.%Y %H:%m:%S", strptime(ctime(message[TIME])))
                        print(f'{message_time} - {message[SENDER]}: {message[MESSAGE_TEXT]}')
                        LOGGER.info(f'Пользователь {self.client_name} получил сообщение'
                                    f' {message[MESSAGE_TEXT]} от пользователя {message[SENDER]}.')
                        with DB_LOCK:
                            self.database.save_message(message[SENDER],
                                                       message[RECIPIENT],
                                                       message[MESSAGE_TEXT])

                    elif message[RESPONSE] == 300:
                        LOGGER.debug(f'Получен ответ "Response 300: {message[ERROR]}".')
                        print(f'{message[ERROR]}')

                    else:
                        LOGGER.error(f'Принято некорректное сообщение {message}')


def main():
    """
    Запуск клиента.
    :return:
    """
    # Получаем параметры из командной строки.
    parser = get_command_args()
    server_ip, server_port, client_name = parser.address, parser.port, parser.name

    if not client_name:
        client_name = input('Введите имя пользователя: ')
    LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {server_ip},'
                f' порт сервера: {server_port}, имя пользователя: {client_name}.')

    try:
        # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
        client_sock = socket(AF_INET, SOCK_STREAM)
        # Таймаут необходим для освобождения сокета.
        client_sock.settimeout(1)

        # Сообщаем серверу о подключении.
        client_sock.connect((server_ip, server_port))
        send_message(client_sock, confirm_presence(client_name))
        answer = receive_message(get_message(client_sock))
        LOGGER.info(f'Установлено соединение с сервером {server_ip}:{server_port}.'
                    f' Ответ сервера: {answer}')
        print('Соединение с сервером установлено.')
    except ServerError as error:
        LOGGER.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as error:
        LOGGER.error(f'В ответе сервера отсутствует обязательное поле: {error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(f'Не удалось подключиться к серверу {server_ip}:{server_port}')
        sys.exit(1)
    except JSONDecodeError:
        LOGGER.error(f'Не удалось декодировать принятое JSON сообщение.')
        sys.exit(1)
    else:
        # Инициализируем БД.
        database = ClientDataBase(client_name)
        load_data_from_server(client_sock, database, client_name)

        # Запускаем процесс приема сообщений.
        receiver = ClientRead(client_sock, client_name, database)
        receiver.daemon = True
        receiver.start()

        # Запускаем отправку сообщений и взаимодействие с пользователем.
        sender = ClientSend(client_sock, client_name, database)
        sender.daemon = True
        sender.start()

        # Если один из потоков завершён, значит или потеряно соединение, или пользователь
        # ввёл exit. Т.к. все события обрабатываются в потоках, достаточно завершить цикл.
        while True:
            sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
