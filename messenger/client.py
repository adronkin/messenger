"""Программа-клиент"""

import re
import sys
from time import strftime, strptime, ctime, time, sleep
from logging import getLogger
from argparse import ArgumentParser
from json import JSONDecodeError
from socket import socket, SOCK_STREAM, AF_INET
from threading import Thread
import logs.client_log_config
from decorators import Log
from errors import ServerError, ReqFieldMissingError, IncorrectDataReceivedError
from common_files.function import send_message, get_message
from common_files.variables import DEFAULT_PORT, DEFAULT_IP, IP_REGEX, ACTION, \
    PRESENCE, TIME, USER, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, RECIPIENT, \
    EXIT

# Инициализируем логгера
LOGGER = getLogger('client_logger')


@Log()
def server_message_handler(sock, username):
    """Функция обрабатывает сообщения от других пользователей, поступившие с сервера"""
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and TIME in message \
                    and SENDER in message and RECIPIENT in message and MESSAGE_TEXT in message \
                    and message[RECIPIENT] == username:
                message_time = strftime("%d.%m.%Y %H:%m:%S", strptime(ctime(message[TIME])))
                print(f'{message_time} - {message[SENDER]}: {message[MESSAGE_TEXT]}')
                LOGGER.info(f'Пользователь {username} получил сообщение {message[MESSAGE_TEXT]}'
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


@Log()
def create_message(sock, username):
    """Функция запрашивает текст сообщения и формирует словарь для сервера.
    При вводе команды завершает работу"""
    recipient = input('Введите имя получателя: ')
    message = input('Введите сообщение: ')
    dict_message = {
        ACTION: MESSAGE,
        TIME: time(),
        SENDER: username,
        RECIPIENT: recipient,
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформирован словарь-сообщение: {dict_message}')
    try:
        send_message(sock, dict_message)
        LOGGER.info(f'Сообщение отправлено пользователю {recipient}')
    except:
        LOGGER.critical(f'Потеряно соединение с сервером')
        sys.exit(1)


def get_help():
    """Функция возвращает справочную информацию"""
    print('Доступные команды:')
    print('1 - отправить сообщение.')
    print('2 - вывести подсказки по командам.')
    print('3 - выйти из программы.')


@Log()
def exit_message(username):
    """Функция формирует сообщение для сервера о завершении работы пользователя"""
    return {
        ACTION: EXIT,
        TIME: time(),
        USER: username
    }


@Log()
def user_menu(sock, username):
    """Функция пользовательское меню"""
    get_help()
    while True:
        command = input('Выберите действие (помощь "2"): ')
        if command == '1':
            create_message(sock, username)
        elif command == '2':
            get_help()
        elif command == '3':
            send_message(sock, exit_message(username))
            print('Работа программы завершена.')
            LOGGER.info(f'Клиент {username} завершил работу.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            sleep(0.5)
            break
        else:
            print('Команда не распознана.')


@Log()
def confirm_presence(user_name):
    """Функция генерирует словарь для отправки сообщения о присутствии пользователя"""
    message = {
        ACTION: PRESENCE,
        TIME: time(),
        USER: user_name
    }
    LOGGER.info(f'Сгенерировано {PRESENCE} сообщение для пользователя {user_name}')
    return message


@Log()
def receive_message(msg):
    """Функция парсит ответ от сервера"""
    LOGGER.debug(f'Обработка сообщения от сервера {msg}')
    if RESPONSE in msg:
        if msg[RESPONSE] == 200:
            LOGGER.info('Сообщение корректно обработано. Response 200: OK')
            return 'Response 200: OK'
        elif msg[RESPONSE] == 400:
            LOGGER.error(f'Сервер не смог отбратать клиентский запрос. '
                         f'Получен отвен "Response 400: {msg[ERROR]}".')
            raise ServerError(f' 400: {msg[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@Log()
def args_parser():
    """Парсит аргументы командной строки, проверяет корректность порта и IP-адреса.
    Возвращает IP-адрес и порт, если параметры введены корретно"""
    parser = ArgumentParser()
    parser.add_argument('address', default=DEFAULT_IP, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    if not 1023 < namespace.port < 65536:
        LOGGER.critical(f'Порт "{namespace.port}" введен некорректно. '
                        f'Необходимо ввести значение от 1024 до 65535.')
        sys.exit(1)
    if not re.match(IP_REGEX, namespace.address):
        LOGGER.critical(f'IP-адрес "{namespace.address}" введен некорректно.')
        sys.exit(1)
    return namespace.address, namespace.port, namespace.name


def main():
    """Код запуска client"""
    server_ip, server_port, client_name = args_parser()
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
        receiver = Thread(target=server_message_handler, args=(client_sock, client_name))
        receiver.daemon = True
        receiver.start()

        # Запускаем отправку сообщений и взаимодействие с пользователем
        user_interface = Thread(target=user_menu, args=(client_sock, client_name))
        user_interface.daemon = True
        user_interface.start()

        # Если один из потоков завершён, значит или потеряно соединение или пользователь
        # ввёл exit. Т.к. все события обработываются в потоках, достаточно завершить цикл.
        while True:
            sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
