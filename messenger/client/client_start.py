"""
Client messaging application. It supports sending messages
to users on the network, messages are encrypted using the
RSA algorithm with a 2048 bit key length.

Supports command line arguments:

``python3 client.py {server IP address} {port} -n or --name {username} -p or --password {password}``

{Server IP address} - the address of the message server.
{port} - port through which connections are accepted
-n or --name is the name of the user who will log into the system.
-p or --password - user password.

All command line options are optional, but the username and password
must be used in tandem.

Examples of using:

``python3 client.py``

Launching the application with default settings.

``python3 client.py 127.0.0.1 8888``

Launching the application with instructions
to connect to the server at ip_address: port.

``python3 -n test -p 123``

Launching the application with user test and password 123.

``python3 client.py 127.0.0.1 8888 -n test -p 123``

Launching the application with the user test and password 123 and instructing
connecting to the server at 127.0.0.1:8888.
"""

import os
import sys
from logging import getLogger
from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox
sys.path.append('../')
from client.custom.errors import ServerError
from client.custom.parse_args import get_command_args
from client.custom.transport import ClientTransport
from client.database.database import ClientDataBase
from client.gui.main_window import ClientMainWindow
from client.gui.start_menu import AuthMenu

# Initialize the logger.
LOGGER = getLogger('client_logger')


def main():
    """
    Function to start the client.
    """
    # Load command line options.
    parser = get_command_args()
    server_ip = parser.address
    server_port = parser.port
    client_name = parser.name
    client_password = parser.password

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
            sys.exit(0)

    LOGGER.info(f'Запущено клиентское приложение. IP-адрес сервера: {server_ip},'
                f' порт сервера: {server_port}, имя пользователя: {client_name}.')

    # Download the keys from the file,
    # if there is no file, then generate a new pair.
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
        transport = ClientTransport(
            server_ip,
            server_port,
            database,
            client_name,
            client_password,
            keys
        )
        transport.setDaemon(True)
        transport.start()
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        sys.exit(1)

    del start_dialog

    # Create GUI.
    main_window = ClientMainWindow(client_name, database, transport, keys)
    main_window.make_connection(transport)
    client_app.exec_()

    # If the graphical shell is closed, close the transport.
    transport.transport_shutdown()
    transport.join()


if __name__ == '__main__':
    main()

# TODO TypeError, обновить список пользователей, если зарегистрирован 1 клиент
