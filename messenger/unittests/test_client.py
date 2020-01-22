"""Unit-тесты для модуля client.py"""

import unittest
from client import confirm_presence, receive_message
from common_files.variables import TIME, ACTION, PRESENCE, USER, RESPONSE, ERROR


class TestClient(unittest.TestCase):
    """Класс для тестирования модуля client.py"""

    def test_confirm_presence(self):
        """Тест функции генерации сообщения о присутствии"""
        test_message = confirm_presence()
        test_message[TIME] = 1579634479.64
        self.assertEqual(
            test_message, {
                ACTION: PRESENCE, TIME: 1579634479.64, USER: 'Guest'})

    def test_receive_message_200(self):
        """Тест ответа 200"""
        self.assertEqual(receive_message({RESPONSE: 200}), 'Response 200: OK')

    def test_receive_message_400(self):
        """Тест ответа 400"""
        self.assertEqual(receive_message(
            {RESPONSE: 400, ERROR: 'Bad request'}), 'Response 400: Bad request')

    def test_receive_message_error(self):
        """Тест ответа Server error"""
        self.assertEqual(receive_message(
            {RESPONSE: 444, ERROR: 'Bad request'}), 'Server error')

    def test_receive_message_value(self):
        """Тест ответа исключения ValueError"""
        self.assertRaises(ValueError, receive_message, {ERROR: 'Bad request'})


if __name__ == '__main__':
    unittest.main()
