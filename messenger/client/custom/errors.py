"""Custom exceptions"""


class ServerError(Exception):
    """Exception - Server Side Error"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
