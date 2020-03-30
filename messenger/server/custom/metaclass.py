"""Module with metaclass performing basic server check."""

from dis import get_instructions


class ServerVerified(type):
    """
    A metaclass that checks that there are no client calls in the resulting
    class such as: connect. It is also verified that the server socket is TCP
    and works over the IPv4 protocol.
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
                # Save the iterator to the variable according to
                # the instructions of the function.
                ret = get_instructions(class_dict[func])
            # If not a function.
            except TypeError:
                pass
            else:
                for operation in ret:
                    # print(operation)
                    # operation - Instruction(opname='LOAD_GLOBAL', opcode=116,
                    # arg=9, argval='send_message', argrepr='send_message',
                    # offset=308, starts_line=201, is_jump_target=False)
                    # opname - name for the operation.
                    if operation.opname == 'LOAD_GLOBAL':
                        if operation.argval not in methods:
                            # Add to the list the method used in the class function.
                            methods.append(operation.argval)
        # print(f'Методы - {methods}')
        if 'connect' in methods:
            raise TypeError(
                'Использование метода connect недопустимо в серверном классе'
            )
        if not ('AF_INET' in methods and 'SOCK_STREAM' in methods):
            raise TypeError('Некорректная инициализация сокета.')
        # Be sure to call the constructor of the ancestor.
        super().__init__(class_name, bases, class_dict)
