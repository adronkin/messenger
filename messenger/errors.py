"""Ошибки"""


class ClientError(Exception):
    """Исключение - ошибка на стороне клиента"""
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
