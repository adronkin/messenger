"""GUI client launcher"""

import os
import sys
from logging import getLogger
from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
sys.path.append('../')
from custom.errors import ServerError
from custom.clt_parse_args import get_command_args
from custom.transport import ClientTransport
from database.clt_database import ClientDataBase
from gui.clt_main_window import ClientMainWindow
from gui.start_menu import AuthMenu

# Initialize the logger.
LOGGER = getLogger('client_logger')

# Load command line options.
PARSER = get_command_args()
SERVER_IP = PARSER.address
SERVER_PORT = PARSER.port
CLIENT_NAME = PARSER.name
CLIENT_PASSWORD = PARSER.password

# Create a client application.
CLIENT_APP = QApplication(sys.argv)

START_DIALOG = AuthMenu()

# If the username was not specified on the command line then request it.
if not CLIENT_NAME or not CLIENT_PASSWORD:
    CLIENT_APP.exec_()
    # # If the user entered a name and clicked OK,
    # then save the entered name and delete the object, otherwise exit.
    if START_DIALOG.ok_pressed:
        CLIENT_NAME = START_DIALOG.auth_name_field.text()
        CLIENT_PASSWORD = START_DIALOG.password_field.text()
    else:
        sys.exit(0)

LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {SERVER_IP},'
            f' порт сервера: {SERVER_PORT}, имя пользователя: {CLIENT_NAME}.')

# Download the keys from the file,
# if there is no file, then generate a new pair.
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
KEY_FILE = os.path.join(DIR_PATH, f'{CLIENT_NAME}.key')
if not os.path.exists(KEY_FILE):
    KEYS = RSA.generate(2048, os.urandom)
    with open(KEY_FILE, 'wb') as key:
        key.write(KEYS.export_key())
else:
    with open(KEY_FILE, 'rb') as key:
        KEYS = RSA.import_key(key.read())

KEYS.publickey().export_key()

# DB initialization.
DATABASE = ClientDataBase(CLIENT_NAME)

try:
    TRANSPORT = ClientTransport(
        SERVER_IP,
        SERVER_PORT,
        DATABASE,
        CLIENT_NAME,
        CLIENT_PASSWORD,
        KEYS
    )
    TRANSPORT.setDaemon(True)
    TRANSPORT.start()
except ServerError as error:
    MESSAGE = QMessageBox()
    MESSAGE.critical(START_DIALOG, 'Ошибка сервера', error.text)
    sys.exit(1)

del START_DIALOG

# Create GUI.
MAIN_WINDOW = ClientMainWindow(CLIENT_NAME, DATABASE, TRANSPORT, KEYS)
MAIN_WINDOW.make_connection(TRANSPORT)
CLIENT_APP.exec_()

# If the graphical shell is closed, close the transport.
TRANSPORT.transport_shutdown()
TRANSPORT.join()

# TODO TypeError, обновить список пользователей, если зарегистрирован 1 клиент
