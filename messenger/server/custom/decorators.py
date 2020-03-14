"""Модуль для декораторов"""

import inspect
from functools import wraps
from logging import getLogger
import log.log_config

LOGGER = getLogger('server_logger')


class Log:
    """Класс-декоратор для логирования имени и аргументов вызываемой функции"""
    def __call__(self, func):
        # Копируем атрибуты функции в атрибуты обернутой функции
        @wraps(func)
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            # Определяем функцию из которой была вызвана func
            stack = inspect.stack()[1][3]
            LOGGER.info(f'Выполнен вызов функции "{func.__name__}" из функции "{stack}"')
            LOGGER.info(f'Функция "{func.__name__}" из модуля '
                        f'"{func.__module__}" с аргументами ({args}, {kwargs})')
            return res
        return decorated
