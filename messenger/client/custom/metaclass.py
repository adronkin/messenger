"""Module with metaclass performing basic client check."""

from dis import get_instructions


class ClientVerified(type):
    """
    A metaclass that performs basic client validation.
    Lack of accept and listen calls for sockets. Using sockets to work on TCP.
    Lack of creating sockets at the class level (class Client: s = socket()).
    """

    def __init__(self, class_name, bases, class_dict):
        """
        :param class_name: instance of the Server class.
        :param bases: tuple of base classes.
        :param class_dict: a dictionary of attributes and methods of an instance of a metaclass.
        """
        # List of methods used in class functions.
        methods = []

        for func in class_dict:
            try:
                ret = get_instructions(class_dict[func])
            except TypeError:
                pass
            else:
                for operation in ret:
                    # operation - Instruction(opname='LOAD_GLOBAL', opcode=116,
                    # arg=9, argval='send_message', argrepr='send_message',
                    # offset=308, starts_line=201, is_jump_target=False)
                    if operation.opname == 'LOAD_GLOBAL':
                        if operation.argval not in methods:
                            methods.append(operation.argval)
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError(
                    f'Использование метода {command} недопустимо в клиентском классе.')
        # Call get_message or send_message from utils considered correct using sockets.
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(class_name, bases, class_dict)
