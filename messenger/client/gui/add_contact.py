"""A module describes a menu for adding a user to the contact list."""

import sys
from logging import getLogger
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QComboBox, QPushButton
sys.path.append('../')
import client.log.log_config
from client.custom.errors import ServerError

# Initialize the logger.
LOGGER = getLogger('client_logger')


class AddContact(QDialog):
    """
    Dialog for adding a user to the contact list. It offers the user a list
    of possible contacts and adds the selected one to the contacts.
    """
    def __init__(self, transport, database):
        self.transport = transport
        self.database = database
        super().__init__()

        self.setFixedSize(294, 95)
        self.setWindowTitle('Добавить контакт')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        # Text for QComboBox.
        self.menu_text = QLabel('Выберите контакт: ', self)
        self.menu_text.move(15, 5)
        self.menu_text.setFixedSize(250, 20)

        # Drop menu.
        self.drop_menu = QComboBox(self)
        self.drop_menu.move(10, 30)
        self.drop_menu.setFixedSize(185, 20)

        # Refresh button.
        self.refresh_button = QPushButton('Обновить', self)
        self.refresh_button.move(195, 25)
        self.refresh_button.setFixedSize(90, 30)
        self.refresh_button.clicked.connect(self.update_possible_contacts)

        # Add button.
        self.add_button = QPushButton('Добавить', self)
        self.add_button.move(55, 60)
        self.add_button.setFixedSize(90, 30)

        # Cancel button.
        self.cancel_button = QPushButton('Отмена', self)
        self.cancel_button.move(147, 60)
        self.cancel_button.setFixedSize(90, 30)
        self.cancel_button.clicked.connect(self.close)

        # Fill in the list of possible contacts.
        if database:
            self.get_possible_contacts()

        self.show()

    def get_possible_contacts(self):
        """
        The method of filling out the list of possible contacts.
        Creates a list of all registered users except those already added
        to contacts and himself.
        """
        # Clears the combobox, removing all items.
        self.drop_menu.clear()
        # Get all users and clients contacts.
        contact_list = set(self.database.get_all_contacts())
        users_list = set(self.database.get_register_users())
        # Delete the user himself.
        users_list.remove(self.transport.username)
        self.drop_menu.addItems(users_list - contact_list)

    def update_possible_contacts(self):
        """
        Method for updating the list of possible contacts. Requests a list of
        known users from the server and updates the contents of the window.
        """
        try:
            user_list = self.transport.get_registered_user_from_server()
            self.database.add_register_users(user_list)
        except ServerError:
            pass
        else:
            self.get_possible_contacts()
            LOGGER.debug('Обновление списка пользователей с сервера выполнено')


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    ADD_MENU = AddContact(None, None)
    APP.exec_()
