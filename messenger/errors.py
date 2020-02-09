"""Ошибки"""


class ServerError(Exception):
    """Исключение - ошибка на стороне сервера"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class ReqFieldMissingError(Exception):
    """Исключение - отсутствует поле RESPONSE"""
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле: {self.missing_field}.'


class IncorrectDataReceivedError(Exception):
    """Исключение - из сокета получены некорректные данные"""
    def __str__(self):
        return 'От удаленного компьютера принято некорректное сообщение.'
