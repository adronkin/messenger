"""
Module for starting the server.

Using.

The module supports command line arguments:

'-p', '--port' - The port on which connections are accepted.
'-a', '--address' - The address from which connections are received.

Examples of using:

``python3 server.py -p 8080``

Starting the server on port 8080.

``python server.py -a 127.0.0.1``

Starting the server accepting only connections to localhost.
"""

import os
import sys
from configparser import ConfigParser
from PyQt5.QtWidgets import QApplication, QMessageBox
sys.path.append('../')
from server.gui.main_window import MainWindow
from server.gui.config_window import ConfigWindow
from server.custom.core import Server
from server.database.database import ServerDataBase
from server.custom.parse_args import args_parser


def main():
    """
    Include functions for creating a server settings dialog box (server_config)
    and saving settings (save_server_config).
    """
    # Download the server configuration file.
    config = ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f'{dir_path}/server.ini')

    # Parsing parameters from the command line or setting default values.
    listen_address, listen_port = args_parser(
        config['SETTINGS']['default_ip'],
        config['SETTINGS']['default_port']
    )

    # Database initialization.
    database = ServerDataBase(os.path.join(config['SETTINGS']['db_path'],
                                           config['SETTINGS']['db_file']))

    # Create a server instance.
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    # Create a graphical environment for the server.
    server_app = QApplication(sys.argv)
    main_window = MainWindow(server, database)

    def server_config():
        """
        The function creates a server settings window.
        """
        global CONFIG_WINDOW
        CONFIG_WINDOW = ConfigWindow()
        CONFIG_WINDOW.db_path.insert(config['SETTINGS']['db_path'])
        CONFIG_WINDOW.db_file_name.insert(config['SETTINGS']['db_file'])
        CONFIG_WINDOW.ip_address_field.insert(config['SETTINGS']['default_ip'])
        CONFIG_WINDOW.port_field.insert(str(config['SETTINGS']['default_port']))
        CONFIG_WINDOW.save_button.clicked.connect(save_server_config)

    def save_server_config():
        """
        Function save settings.
        """
        global CONFIG_WINDOW
        message = QMessageBox()
        config['SETTINGS']['db_path'] = CONFIG_WINDOW.db_path.text()
        config['SETTINGS']['db_file'] = CONFIG_WINDOW.db_file_name.text()
        try:
            port = int(CONFIG_WINDOW.port_field.text())
        except ValueError:
            message.warning(CONFIG_WINDOW, 'Ошибка', 'Порт должен быть числом.')
        else:
            # TODO добавить проверку корректности IP-адреса.
            config['SETTINGS']['default_ip'] = CONFIG_WINDOW.ip_address_field.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = CONFIG_WINDOW.port_field.text()
                # Write a new port to a file.
                with open(os.path.join(dir_path, 'server.ini'), 'w') as conf:
                    config.write(conf)
                    message.information(
                        CONFIG_WINDOW,
                        'Ok',
                        'Настройки сохранены.'
                    )
            else:
                message.warning(CONFIG_WINDOW,
                                'Ошибка',
                                'Порт должен быть от 1024 до 65536.'
                                )

    # Associate buttons with procedures.
    main_window.setting_button.triggered.connect(server_config)

    # Run GUI.
    server_app.exec_()

    # By closing the windows, we stop the message handler.
    server_app.running = False


if __name__ == '__main__':
    main()

# TODO проверить запуск на другой системе.
