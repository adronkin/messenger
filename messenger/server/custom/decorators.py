"""Module for server decorators"""

import inspect
from functools import wraps
from logging import getLogger
import log.log_config

LOGGER = getLogger('server_logger')


class Log:
    """
    Decorator class for logging the name and arguments of the called function.
    """
    def __call__(self, func):
        # Copy the attributes of a function to the attributes of a wrapped function.
        @wraps(func)
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            # Define the function from which func was called.
            stack = inspect.stack()[1][3]
            LOGGER.info(f'Выполнен вызов функции "{func.__name__}" из функции "{stack}".')
            LOGGER.info(f'Функция "{func.__name__}" из модуля '
                        f'"{func.__module__}" с аргументами ({args}, {kwargs}).')
            return res
        return decorated
