"""Модуль для метакласса выполняющего базовую проверку сервера"""

from dis import get_instructions


class ServerVerified(type):
    """
    Метакласс выполняющий базовую проверку сервера.
    Отсутствие вызовов connect для сокетов.
    Использование сокетов для работы по TCP.
    """

    def __init__(self, class_name, bases, class_dict):
        """
        :param class_name: экземпляр класса Server.
        :param bases: кортеж базовых классов.
        :param class_dict: словарь атрибутов и методов экземпляра метакласса.
        """
        # Список медодов используемых в функциях класса.
        methods = []

        for func in class_dict:
            try:
                # Сохранем в переменную итератор по инструкциям функции.
                ret = get_instructions(class_dict[func])
            # Если не функция.
            except TypeError:
                pass
            else:
                for operation in ret:
                    # print(operation)
                    # operation - Instruction(opname='LOAD_GLOBAL', opcode=116,
                    # arg=9, argval='send_message', argrepr='send_message',
                    # offset=308, starts_line=201, is_jump_target=False)
                    # opname - имя для операции.
                    if operation.opname == 'LOAD_GLOBAL':
                        if operation.argval not in methods:
                            # Добавляем в список метод, использующийся в
                            # функции класса.
                            methods.append(operation.argval)
        # print(f'Методы - {methods}')
        if 'connect' in methods:
            raise TypeError(
                'Использование метода connect недопустимо в серверном классе')
        if not ('AF_INET' in methods and 'SOCK_STREAM' in methods):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка.
        super().__init__(class_name, bases, class_dict)
