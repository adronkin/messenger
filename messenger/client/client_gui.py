"""GUI client launcher"""

import sys
from logging import getLogger
from PyQt5.QtWidgets import QApplication
sys.path.append('../')
from clt_database import ClientDataBase
from clt_parse_args import get_command_args
from gui.main_window import ClientMainWindow
from gui.start_menu import AuthMenu
from transport import ClientTransport
import log.log_config

# Initialize the logger.
LOGGER = getLogger('client_logger')

# Load command line options.
parser = get_command_args()
server_ip, server_port, client_name = parser.address, parser.port, parser.name

# Create a client application.
client_app = QApplication(sys.argv)

# If the username was not specified on the command line then request it.
if not client_name:
    start_dialog = AuthMenu()
    client_app.exec_()
    # # If the user entered a name and clicked OK,
    # then save the entered name and delete the object, otherwise exit.
    if start_dialog.ok_pressed:
        client_name = start_dialog.auth_name_field.text()
        del start_dialog
    else:
        exit(0)

LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {server_ip},'
            f' порт сервера: {server_port}, имя пользователя: {client_name}.')

# DB initialization.
database = ClientDataBase(client_name)

try:
    transport = ClientTransport(server_ip, server_port, database, client_name)
except SyntaxError as error:
    print(error.text)
    exit(1)
transport.setDaemon(True)
transport.start()

# Create GUI.
main_window = ClientMainWindow(client_name, database, transport)
main_window.make_connection(transport)
client_app.exec_()

# If the graphical shell is closed, close the transport.
transport.transport_shutdown()
transport.join()
