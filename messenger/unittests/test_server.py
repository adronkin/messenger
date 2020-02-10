"""Unit-тесты для модуля server.py"""

import os
import sys
import unittest
sys.path.append(os.path.join(os.getcwd(), '..'))
from server.server import args_parser


class TestServer(unittest.TestCase):
    """Тесты для модуля server.py"""

    def test_args_parser(self):
        """Тест парсера командной строки без аргументов"""
        self.assertEqual(args_parser(), ('127.0.0.1', 7777))


# TODO message_handler
# TODO args_parser
# TODO processing_message


if __name__ == '__main__':
    unittest.main()
