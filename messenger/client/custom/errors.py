"""The module contains custom exceptions."""


class ServerError(Exception):
    """Class is an exception for handling server errors. During generation,
    it requires a string describing the error received from the server."""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
