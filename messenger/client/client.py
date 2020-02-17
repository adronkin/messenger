"""Программа-клиент"""

import sys
from socket import socket, AF_INET, SOCK_STREAM
from time import strftime, strptime, ctime, time, sleep
from logging import getLogger
from json import JSONDecodeError
from threading import Thread
sys.path.append('../')
import logs.client_log_config
from client_func import confirm_presence, receive_message
from parse_args import get_command_args
from metaclass import ClientVerified
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError
from common_files.function import send_message, get_message
from common_files.variables import ACTION, TIME, USER, RESPONSE, ERROR, \
    MESSAGE, MESSAGE_TEXT, SENDER, RECIPIENT, EXIT

# Инициализируем логгера
LOGGER = getLogger('client_logger')


class ClientSend(Thread, metaclass=ClientVerified):
    def __init__(self, sock, client_name):
        self.sock = sock
        self.client_name = client_name
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
                send_message(self.sock, self.exit_message())
                print('Работа программы завершена.')
                LOGGER.info(f'Клиент {self.client_name} завершил работу.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                sleep(0.5)
                break
            else:
                print('Команда не распознана.')

    def get_help(self):
        """
        Возвращает справочную информацию.
        :return:
        """
        print('Доступные команды:')
        print('1 - отправить сообщение.')
        print('2 - вывести подсказки по командам.')
        print('3 - выйти из программы.')

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
        message = input('Введите сообщение: ')
        dict_message = {
            ACTION: MESSAGE,
            TIME: time(),
            SENDER: self.client_name,
            RECIPIENT: recipient,
            MESSAGE_TEXT: message
        }
        LOGGER.debug(f'Сформирован словарь-сообщение: {dict_message}')
        try:
            send_message(self.sock, dict_message)
            LOGGER.info(f'Сообщение отправлено пользователю {recipient}')
        except Exception:
            LOGGER.critical(f'Потеряно соединение с сервером')
            sys.exit(1)


class ClientRead(Thread, metaclass=ClientVerified):
    def __init__(self, sock, client_name):
        self.sock = sock
        self.client_name = client_name
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
                    LOGGER.info(f'Пользователь {self.client_name} получил сообщение {message[MESSAGE_TEXT]}'
                                f' от пользователя {message[SENDER]}')
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
