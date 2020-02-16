"""Программа-сервер"""

import sys
import socket
from select import select
from logging import getLogger
sys.path.append('../')
import logs.server_log_config
from metaclass import ServerVerified
from descriptors.address import Address
from descriptors.port import Port
from parse_args import args_parser
from common_files.function import get_message, send_message
from common_files.variables import MAX_QUEUE, ACTION, PRESENCE, TIME, ERROR, \
    USER, MESSAGE, MESSAGE_TEXT, SENDER, RESPONSE_200, RESPONSE_300, RESPONSE_400, \
    EXIT, RECIPIENT

# Инициализируем логгера
LOGGER = getLogger('server_logger')


class Server(metaclass=ServerVerified):
    # Дескрипторы
    address = Address()
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.address = listen_address
        self.port = listen_port

        # Список клиентов, очередь сообщений, словарь с именами и сокетами пользователей
        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        """
        Подготовка сокета сервера.
        :return:
        """
        LOGGER.info(
            f'Сервер запущен с параметрами - {self.address}:{self.port}')
        # Создаем сокет TCP (AF_INET - сетевой сокет, SOCK_STREAM - работа с TCP пакетами)
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind((self.address, self.port))
        server_sock.settimeout(0.5)

        # Переводим сервер в режим ожидания запросов (слушаем порт).
        self.sock = server_sock
        self.sock.listen(MAX_QUEUE)

    def main_loop(self):
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
            except OSError:
                print('Исключение OSError - строка 81')
            # Принимаем сообщения, если есть сообщения от клиентов, кладем в словарь.
            # Если возвращена ошибка, исключаем клиента из списка clients
            if clients_senders:
                for client_with_message in clients_senders:
                    try:
                        self.processing_message(
                            get_message(client_with_message),
                            client_with_message)
                    except Exception:
                        LOGGER.info(
                            f'Клиент {client_with_message.getpeername()} отключился от сервера.')
                        self.clients.remove(client_with_message)

            # Если есть сообщения для отправки, обрабатываем.
            for message in self.messages:
                try:
                    self.message_handler(message, clients_recipients)
                except Exception:
                    LOGGER.info(
                        f'Клиент {message[RECIPIENT]} отключился от сервера.')
                    no_user_dict = RESPONSE_300
                    no_user_dict[ERROR] = f'Пользователь {message[RECIPIENT]} отключился от сервера.'
                    send_message(self.names[message[SENDER]], no_user_dict)
                    del self.names[message[RECIPIENT]]
            self.messages.clear()

    def message_handler(self, message, listen_sock):
        """
        Функция обрабатывает сообщение. Принимает словарь сообщения,
        список пользователей и слушащие сокеты. Отправляет сообщение адресату.
        :param message: сообщение для обработки.
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
        :param message: сообщение.
        :param client: список клиентов.
        :return:
        """
        LOGGER.debug(f'Обработка сообщения от клиента - {message}')
        # Если PRESENCE-сообщение, проверяем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
            # Проверяем зарегистрирован пользователь или нет
            if message[USER] not in self.names.keys():
                self.names[message[USER]] = client
                send_message(client, RESPONSE_200)
                LOGGER.info(f'Клиент {client.getpeername()} подключился.'
                            f' Отправлен ответ {RESPONSE_200}')
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя занято.'
                send_message(client, response)
                LOGGER.error(f'Попытка подключения клиента {client.getpeername()} используя'
                             f' занятое имя пользователя. Отправлен ответ {RESPONSE_400}')
                self.clients.remove(client)
                client.close()
            return
        # Если сообщение, то проверяем и добовляем его в очередь сообщений
        elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and SENDER in message \
                and RECIPIENT in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        # Если пользоваталь хочет завершить работу
        elif ACTION in message and message[ACTION] == EXIT and TIME in message and USER in message:
            LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
            self.clients.remove(self.names[message[USER]])
            self.names[message[USER]].close()
            del self.names[message[USER]]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Bad request.'
            LOGGER.debug(f'Получен некорректный запрос от клиента {client.getpeername()},'
                         f' отправлен ответ {response}')
            send_message(client, response)
            return


def main():
    """
    Запуск сервера.
    :return:
    """
    # Парсим параметры из командной строки или установка значений по умолчанию.
    listen_address, listen_port = args_parser()

    # Создаем экземпляр сервера
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
