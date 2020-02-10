"""Unit-тесты для модуля client.py"""

import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from errors import ServerError, ReqFieldMissingError
from client.client import confirm_presence, receive_message, exit_message, args_parser
from common_files.variables import TIME, ACTION, PRESENCE, USER, RESPONSE, ERROR, EXIT


class TestClient(unittest.TestCase):
    """Класс для тестирования модуля client.py"""

    def test_confirm_presence(self):
        """Тест функции генерации сообщения о присутствии"""
        test_message = confirm_presence('Test_user')
        test_message[TIME] = 1579634479.64
        self.assertEqual(
            test_message, {
                ACTION: PRESENCE, TIME: 1579634479.64, USER: 'Test_user'})

    def test_exit_message(self):
        """Тест функции генерации сообщения о завершении работы"""
        test_message = exit_message('Test_user')
        test_message[TIME] = 1579634479.64
        self.assertEqual(test_message, {ACTION: EXIT, TIME: 1579634479.64, USER: 'Test_user'})

    def test_receive_message_200(self):
        """Тест ответа 200"""
        self.assertEqual(receive_message({RESPONSE: 200}), 'Response 200: OK')

    def test_receive_message_400(self):
        """Тест ответа 400"""
        self.assertRaises(ServerError, receive_message, {RESPONSE: 400, ERROR: 'Bad request'})

    def test_receive_message_incorrect_response(self):
        """Тест ответа исключения ReqFieldMissingError с некорректным кодом ответа"""
        self.assertRaises(ReqFieldMissingError, receive_message, {RESPONSE: 444, ERROR: 'Bad request'})

    def test_receive_message_error_not_response(self):
        """Тест ответа исключения ReqFieldMissingError с отсутствующим полем RESPONSE"""
        self.assertRaises(ReqFieldMissingError, receive_message, {ERROR: 'Bad request'})

    def test_receive_message_error_not_error(self):
        """Тест ответа исключения ReqFieldMissingError с отсутствующим полем ERROR"""
        self.assertRaises(ReqFieldMissingError, receive_message, {RESPONSE: 400})

    def test_args_parser(self):
        """Тест парсера командной строки без аргументов"""
        self.assertEqual(args_parser(), ('127.0.0.1', 7777, None))

    def test_args_parser_address(self):
        """Тест парсера командной строки без аргументов"""
        args = ['192.168.0.1']
        parser = args_parser.parse_args('address')
        print(parser)
        self.assertEqual(parser.args, ('192.168.0.1', 7777, None))


if __name__ == '__main__':
    unittest.main()


# TODO server_message_handler
# TODO create_message
# TODO user_menu
# TODO args_parser
