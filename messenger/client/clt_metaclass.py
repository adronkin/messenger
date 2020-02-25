"""Модуль для метакласса выполняющего базовую проверку клиента"""

from dis import get_instructions


class ClientVerified(type):
    """
    Метакласс выполняющий базовую проверку клиента.
    Отсутствие вызовов accept и listen для сокетов.
    Использование сокетов для работы по TCP.
    Отсутствие создания сокетов на уровне класса (class Client: s = socket()...).
    """

    def __init__(self, class_name, bases, class_dict):
        """
        :param class_name: Экземпляр класса клиент.
        :param bases: кортеж базовых классов.
        :param class_dict: словарь атрибутов и методов экземпляра метакласса.
        """
        # Список медодов используемых в функциях класса.
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
        # Вызов get_message или send_message из utils считаем корректным использованием сокетов
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')
        super().__init__(class_name, bases, class_dict)
