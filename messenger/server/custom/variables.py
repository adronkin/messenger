"""The module contains global variables for the server application."""

ENCODING = 'utf-8'
# Maximum Connection Queue Length.
MAX_QUEUE = 5
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

# Regular expression for validating an IP address.
IP_REGEX = r'^([0-9]\.|[1]?[0-9][0-9]\.|[2][0-4][0-9]\.|[2][5][0-5]\.){3}([0-9]|[1]?[0-9][0-9]|[2][0-4][0-9]|[2][5][0-5])$'

# The answers.
RESPONSE_200 = {RESPONSE: 200}

RESPONSE_205 = {RESPONSE: 205}

RESPONSE_202 = {
    RESPONSE: 202,
    DATA: None
}

RESPONSE_300 = {
    RESPONSE: 300,
    ERROR: None
}

RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: None
}

RESPONSE_511 = {
    RESPONSE: 511,
    DATA: None
}
