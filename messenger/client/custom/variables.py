"""The module contains global variables for the client application."""

from time import time

# Default IP address.
DEFAULT_IP = '127.0.0.1'
# Default network port.
DEFAULT_PORT = 7777
# Encoding.
ENCODING = 'utf-8'
# Maximum message length (bytes).
MAX_DATA = 10240

# JIM protocol keys.
ACTION = 'action'
USER = 'user'
TIME = 'time'
RESPONSE = 'response'
PRESENCE = 'presence'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
SENDER = 'sender'
EXIT = 'exit'
RECIPIENT = 'recipient'
ADD_CONTACT = 'add_contact'
ACCOUNT_NAME = 'account_name'
DEL_CONTACT = 'del_contact'
DATA = 'data'
GET_CONTACTS = 'get_contacts'
GET_REGISTERED = 'get_registered'
PUBLIC_KEY_REQUEST = 'public_key_request'
PUBLIC_KEY = 'public_key'

# Regular expression for IP validation.
IP_REGEX = r'^([0-9]\.|[1]?[0-9][0-9]\.|[2][0-4][0-9]\.|[2][5][0-5]\.){3}([0-9]|[1]?[0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])$'

# Confirmation of presence.
CONFIRM_PRESENCE = {
    ACTION: PRESENCE,
    TIME: time(),
    USER: None,
    PUBLIC_KEY: None
}

# Exit message.
EXIT_MESSAGE = {
    ACTION: EXIT,
    TIME: time(),
    USER: None
}

# Message.
DICT_MESSAGE = {
    ACTION: MESSAGE,
    TIME: time(),
    SENDER: None,
    RECIPIENT: None,
    MESSAGE_TEXT: None
}

# Add to contact list.
ADD_CONTACT_DICT = {
    ACTION: ADD_CONTACT,
    TIME: time(),
    USER: None,
    ACCOUNT_NAME: None
}

# Remove from contact list.
DEL_CONTACT_DICT = {
    ACTION: DEL_CONTACT,
    TIME: time(),
    USER: None,
    ACCOUNT_NAME: None
}

# Contact list request.
GET_CONTACTS_DICT = {
    ACTION: GET_CONTACTS,
    TIME: time(),
    USER: None
}

# Request a list of registered users.
GET_REGISTERED_DICT = {
    ACTION: GET_REGISTERED,
    TIME: time(),
    USER: None
}

# Request public key.
GET_PUBLIC_KEY = {
    ACTION: PUBLIC_KEY_REQUEST,
    TIME: time(),
    USER: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
