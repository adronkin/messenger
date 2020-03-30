"""The module contains decorators for the server application."""

import inspect
import sys
from functools import wraps
from logging import getLogger
sys.path.append('../')
import server.log.log_config

LOGGER = getLogger('server_logger')


class Log:
    """
    A decorator that logs function calls. Saves events containing information
    about the name of the called function, the parameters with which the
    function is called, and the module that calls the function.
    """
    def __call__(self, func):
        # Copy the attributes of a function to the attributes of a wrapped function.
        @wraps(func)
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            # Define the function from which func was called.
            stack = inspect.stack()[1][3]
            LOGGER.info(f'Выполнен вызов функции {func.__name__} из функции {stack}.')
            LOGGER.info(f'Функция {func.__name__} из модуля {func.__module__}'
                        f' с аргументами ({args}, {kwargs}).')
            return res
        return decorated
