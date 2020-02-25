"""Программа-клиент"""

import sys
from socket import socket, AF_INET, SOCK_STREAM
from time import strftime, strptime, ctime, time, sleep
from logging import getLogger
from json import JSONDecodeError
from threading import Thread, Lock
from clt_parse_args import get_command_args
from clt_metaclass import ClientVerified
from clt_database import ClientDataBase
from clt_function import confirm_presence, receive_message, add_contact_to_server, send_message,\
    get_message
from clt_variables import ACTION, TIME, USER, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER,\
    RECIPIENT, EXIT
sys.path.append('../')
import logs.client_log_config
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError

# Инициализируем логгера
LOGGER = getLogger('client_logger')

# Обхект блокировки сокета и работы БД
SOCK_LOCK = Lock()
DB_LOCK = Lock()


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
        self.get_help()
        while True:
            command = input('Выберите действие (помощь "2"): ')
            if command == '1':
                self.create_message()
            elif command == '2':
                self.get_help()
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
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                sleep(0.5)
                break
            else:
                print('Команда не распознана.')

    def contact_menu(self):
        """
        Меню для работы со списком контактов.
        :return:
        """
        contact_help = """
        1 - Показать список контактов.
        2 - Добавить пользователя в контакты.
        3 - Удалить пользовател из контактов.
        4 - Вывести подсказки по командам.
        5 - Назад.
        """
        while True:
            command = input('Выберите действие (помощь "4"): ')
            if command == '1':
                with DB_LOCK:
                    contacts = self.database.get_all_contact()
                for num, contact in enumerate(contacts):
                    print(f'{num + 1}. {contact}')
            elif command == '2':
                username = input('Введите имя пользователя: ')
                if self.database.check_contact(username):
                    # Вносим информацию в БД.
                    with DB_LOCK:
                        self.database.add_contact(username)
                    # Отправляем информацию на сервер.
                    with SOCK_LOCK:
                        try:
                            # TODO создать функцию
                            add_contact_to_server(self.sock, self.client_name, username)
                        except ServerError:
                            LOGGER.error('Неудачная попытка отправки информации на сервер.')
            elif command == '3':
                username = input('Введите имя пользователя: ')
                with DB_LOCK:
                    if self.database.check_contact(username):
                        self.database.delete_contact(username)
                        print(f'Пользователь {username} удален из списка контактов.')
                    else:
                        print(f'Удаление невозможно.'
                              f' Пользователя {username} нет в списке контактов.')
                        LOGGER.error(
                            'Попытка удаления пользователя отсутствующего в списке котактов.')
            elif command == '4':
                print(contact_help)
            elif command == '5':
                break

    def message_history(self):
        message_help = """
        1 - Вывести входящие сообщения.
        2 - Вывести исходящие сообщения.
        3 - Вывести все сообщения.
        4 - Вывести подсказки по командам.
        5 - Назад.
        """
        command = input('Выберите действие (помощь "3"): ')
        while True:
            if command == '1':
                message_list = self.database.get_message_history(recipient=self.client_name)
                for msg in message_list:
                    print(f'{msg.date} от {msg.sender}: {msg.message}')
            elif command == '2':
                message_list = self.database.get_message_history(sender=self.client_name)
                for msg in message_list:
                    print(f'{msg.date} пользователю {msg.sender}: {msg.message}')
            elif command == '3':
                message_list = self.database.get_message_history()
                for msg in message_list:
                    print(f'{msg.date} отправитель {msg.sender} получатель {msg.recipient}: '
                          f'{msg.message}')
            elif command == '4':
                print(message_help)
            elif command == '5':
                break

    @staticmethod
    def get_help():
        """
        Печатает справочную информацию.
        """
        print('Доступные команды:')
        print('1 - Отправить сообщение.')
        print('2 - Вывести подсказки по командам.')
        print('3 - Список контактов.')
        print('4 - История сообщений.')
        print('5 - Выйти из программы.')

    def exit_message(self):
        """
        Формирует сообщение для сервера о завершении работы пользователя.
        :return {dict}: словарь с информацией о завершении работы пользователя.
        """
        return {
            ACTION: EXIT,
            TIME: time(),
            USER: self.client_name
        }

    def create_message(self):
        """
        Запрашивает текст сообщения и формирует словарь для сервера.
        При вводе команды завершает работу.
        :return:
        """
        recipient = input('Введите имя получателя: ')

        # Проверяем, что пользователь зарегистрирован на сервере.
        with DB_LOCK:
            if not self.database.check_registered_user(recipient):
                LOGGER.error(f'Попытка отправки сообщения'
                             f' незарегистрированому получателю: {recipient}.')
                print(f'Пользователь {recipient} не зарегистрирован.')
                return

        message = input('Введите сообщение: ')

        dict_message = {
            ACTION: MESSAGE,
            TIME: time(),
            SENDER: self.client_name,
            RECIPIENT: recipient,
            MESSAGE_TEXT: message
        }
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
        Функция обрабатывает сообщения от других пользователей, поступившие с сервера
        :return:
        """
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                        and SENDER in message and RECIPIENT in message and MESSAGE_TEXT in message \
                        and message[RECIPIENT] == self.client_name:
                    message_time = strftime("%d.%m.%Y %H:%m:%S", strptime(ctime(message[TIME])))
                    print(f'{message_time} - {message[SENDER]}: {message[MESSAGE_TEXT]}')
                    LOGGER.info(f'Пользователь {self.client_name} получил сообщение'
                                f' {message[MESSAGE_TEXT]} от пользователя {message[SENDER]}')
                elif message[RESPONSE] == 300:
                    LOGGER.debug(f'Получен отвен "Response 300: {message[ERROR]}".')
                    print(f'{message[ERROR]}')
                else:
                    LOGGER.error(f'Принято некорректное сообщение {message}')
            except IncorrectDataReceivedError:
                LOGGER.error('Не удалось декодировать полученное сообщение')
            except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError,
                    OSError, JSONDecodeError):
                LOGGER.critical(f'Соединение с сервером потеряно')
                break


def main():
    """
    Запуск клиента.
    :return:
    """
    parser = get_command_args()
    server_ip, server_port, client_name = parser.address, parser.port, parser.name
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {server_ip},'
                f' порт сервера: {server_port}, имя пользователя: {client_name}.')

    try:
        # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
        client_sock = socket(AF_INET, SOCK_STREAM)
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
        # Если соединение с сервером установлено корректно, запускаем процесс приема сообщений

        receiver = ClientRead(client_sock, client_name)
        receiver.daemon = True
        receiver.start()

        # Запускаем отправку сообщений и взаимодействие с пользователем
        sender = ClientSend(client_sock, client_name)
        sender.daemon = True
        sender.start()

        # Если один из потоков завершён, значит или потеряно соединение или пользователь
        # ввёл exit. Т.к. все события обработываются в потоках, достаточно завершить цикл.
        while True:
            sleep(1)
            if receiver.is_alive() and sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()

# TODO удалить из контактов (на сервере)
