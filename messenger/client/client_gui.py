"""GUI client launcher"""

import os
import sys
from logging import getLogger
from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
sys.path.append('../')
from custom.errors import ServerError
from database.clt_database import ClientDataBase
from gui.clt_main_window import ClientMainWindow
from clt_parse_args import get_command_args
from gui.start_menu import AuthMenu
from transport import ClientTransport
import log.log_config

# Initialize the logger.
LOGGER = getLogger('client_logger')

# Load command line options.
parser = get_command_args()
server_ip, server_port, client_name, client_password = parser.address, parser.port, \
                                                       parser.name, parser.password

# Create a client application.
client_app = QApplication(sys.argv)

start_dialog = AuthMenu()

# If the username was not specified on the command line then request it.
if not client_name or not client_password:
    client_app.exec_()
    # # If the user entered a name and clicked OK,
    # then save the entered name and delete the object, otherwise exit.
    if start_dialog.ok_pressed:
        client_name = start_dialog.auth_name_field.text()
        client_password = start_dialog.password_field.text()
    else:
        exit(0)

LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {server_ip},'
            f' порт сервера: {server_port}, имя пользователя: {client_name}.')

# Download the keys from the file, if there is no file, then generate a new pair.
dir_path = os.path.dirname(os.path.realpath(__file__))
key_file = os.path.join(dir_path, f'{client_name}.key')
if not os.path.exists(key_file):
    keys = RSA.generate(2048, os.urandom)
    with open(key_file, 'wb') as key:
        key.write(keys.export_key())
else:
    with open(key_file, 'rb') as key:
        keys = RSA.import_key(key.read())

keys.publickey().export_key()

# DB initialization.
database = ClientDataBase(client_name)

try:
    transport = ClientTransport(server_ip, server_port, database,
                                client_name, client_password, keys)
    transport.setDaemon(True)
    transport.start()
except ServerError as error:
    message = QMessageBox()
    message.critical(start_dialog, 'Ошибка сервера', error.text)
    exit(1)

del start_dialog

# Create GUI.
main_window = ClientMainWindow(client_name, database, transport, keys)
main_window.make_connection(transport)
client_app.exec_()

# If the graphical shell is closed, close the transport.
transport.transport_shutdown()
transport.join()
