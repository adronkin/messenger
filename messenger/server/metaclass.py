"""Модуль для метакласса выполняющего базовую проверку сервера"""

from dis import get_instructions


class ServerVerified(type):
    """
    Метакласс выполняющий базовую проверку сервера.
    Отсутствие выховов connect для сокетов.
    Использование сокетов для работы по TCP.
    """
    def __init__(self, class_name, bases, class_dct):
        """
        :param class_name: экземпляр класса Server.
        :param bases: кортеж базовых классов.
        :param class_dct: словарь атрибутов и методов экземпляра метакласса.
        """
        # Список медодов используемых в функциях класса.
        methods = []
        # Список атрибутов используемых в функциях класса.
        attributes = []

        for func in class_dct:
            try:
                # Сохранем в переменную итератор по инструкциям функции.
                ret = get_instructions(class_dct[func])
            # Если не функция.
            except TypeError:
                pass
            else:
                for i in ret:
                    print(i)
                    # i - Instruction(opname='LOAD_GLOBAL', opcode=116, arg=9,
                    # argval='send_message', argrepr='send_message', offset=308,
                    # starts_line=201, is_jump_target=False)
                    # opname - имя для операции.
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # Добавляем в список метод, использующийся в функции класса.
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            # Добавляем в список атрибут, использующийся в функции класса.
                            attributes.append(i.argval)
        print(f'Методы - {methods}')
        print(f'Атрибуты - {attributes}')
        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        if not ('AF_INET' in attributes and 'SOCK_STREAM' in attributes):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка.
        super().__init__(class_name, bases, class_dct)
