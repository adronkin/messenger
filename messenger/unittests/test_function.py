"""Unit-тесты для модуля function.py"""

import json
import os
import sys
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common_files.variables import ENCODING, RESPONSE, ERROR, ACTION, PRESENCE, TIME, USER
from common_files.function import send_message, get_message


class TestSocket:
    """Класс для тестирования функций get_message и send_message"""

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.to_send_message = None

    def send(self, message_to_send):
        """Функция сериализует сообщение в json, кодирует его и сохраняет сообщение,
         которое должно было быть отправлено в сокет"""
        test_json_message = json.dumps(self.test_dict)
        self.encoded_message = test_json_message.encode(ENCODING)
        # Сохраняем сообщение, которое должно было быть отправлено в сокет
        self.to_send_message = message_to_send

    def recv(self, max_data):
        """Функция для получения данных из сокета"""
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class TestFunction(unittest.TestCase):
    """Тесты для модуля function.py"""

    test_dict_send = {ACTION: PRESENCE, TIME: 1579634479.64, USER: 'Guest'}
    correct = {RESPONSE: 200}
    error = {RESPONSE: 400, ERROR: 'Bad request'}

    def test_send_message(self):
        """Тестирование функции отправки"""
        # Экземпляр тестового словаря
        test_socket = TestSocket(self.test_dict_send)
        # Запускаем тестируемую функцию
        send_message(test_socket, self.test_dict_send)
        # Проверка корретности кодирования словаря.
        # Сравниваем результат кодирования в TestSocket и результат от тестируемой функции
        self.assertEqual(test_socket.encoded_message, test_socket.to_send_message)

    def test_get_message(self):
        """Тестирование функции приема сообщений"""
        test_correct = TestSocket(self.correct)
        test_error = TestSocket(self.error)
        # Тест расшифровки корректного словаря
        self.assertEqual(get_message(test_correct), self.correct)
        # Тест расшифровки некорректного словаря
        self.assertEqual(get_message(test_error), self.error)
        # Проверка исключения ValueError, если принят не словарь
        self.assertRaises(AttributeError, get_message, 'not_dict')


if __name__ == '__main__':
    unittest.main()
