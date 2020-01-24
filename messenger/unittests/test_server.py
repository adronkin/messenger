"""Unit-тесты для модуля server.py"""

import os
import sys
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from common_files.variables import ACTION, PRESENCE, TIME, USER, RESPONSE, ERROR
from server import processing_message


class TestServer(unittest.TestCase):
    """Тесты для модуля server.py"""

    correct = {RESPONSE: 200}
    error = {RESPONSE: 400, ERROR: 'Bad request'}

    def test_processing_message(self):
        """Проверка формирования ответа 200 при получении корректного сообщения"""
        answer = {ACTION: PRESENCE, TIME: 1579634479.64, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.correct)

    def test_processing_message_action(self):
        """Проверка ответа при некорректном ACTION"""
        answer = {ACTION: 'Hello', TIME: 1579634479.64, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.error)

    def test_processing_message_not_action(self):
        """Проверка ответа при отсутствии ACTION"""
        answer = {TIME: 1579634479.64, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.error)

    def test_processing_message_not_time(self):
        """Проверка ответа при отсутствии TIME"""
        answer = {ACTION: PRESENCE, USER: 'Guest'}
        self.assertEqual(processing_message(answer), self.error)

    def test_processing_message_bad_user(self):
        """Проверка ответа при некорректном USER"""
        answer = {ACTION: PRESENCE, TIME: 1579634479.64, USER: 'Man'}
        self.assertEqual(processing_message(answer), self.error)

    def test_processing_message_not_user(self):
        """Проверка ответа при отсутствии USER"""
        answer = {ACTION: PRESENCE, TIME: 1579634479.64}
        self.assertEqual(processing_message(answer), self.error)


if __name__ == '__main__':
    unittest.main()
