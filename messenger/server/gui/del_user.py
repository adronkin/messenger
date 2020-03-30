"""The module describes the user deletion window."""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QLabel, \
    QComboBox, QPushButton


class DeleteUserWindow(QDialog):
    """
    Class - dialog for selecting a contact to delete.
    """
    def __init__(self, server, database):
        super().__init__()

        self.server = server
        self.database = database

        self.setFixedSize(220, 95)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        # Text for drop menu.
        self.del_user_text = QLabel('Выберите пользователя: ', self)
        self.del_user_text.move(15, 5)
        self.del_user_text.setFixedSize(200, 20)

        # Drop menu.
        self.del_drop_menu = QComboBox(self)
        self.del_drop_menu.move(10, 30)
        self.del_drop_menu.setFixedSize(200, 20)

        # Delete button.
        self.delete_button = QPushButton('Удалить', self)
        self.delete_button.move(22, 60)
        self.delete_button.setFixedSize(90, 30)
        self.delete_button.clicked.connect(self.remove_user)

        # Cancel button.
        self.cancel_button = QPushButton('Отмена', self)
        self.cancel_button.move(114, 60)
        self.cancel_button.setFixedSize(90, 30)
        self.cancel_button.clicked.connect(self.close)

        if database:
            self.drop_menu_fill()

        self.show()

    def drop_menu_fill(self):
        """
        The method fills the dropdown menu.
        """
        self.del_drop_menu.addItems([item[0] for item in self.database.get_all_users()])

    def remove_user(self):
        """
        Method handler deletion. Checks if the client is connected
        and closes the connection, also deleting it from the database.
        """
        self.database.del_user(self.del_drop_menu.currentText())
        if self.del_drop_menu.currentText() in self.server.names:
            sock = self.server.names[self.del_drop_menu.currentText()]
            del self.server.names[self.del_drop_menu.currentText()]
            self.server.remove_client(sock)
        # Send clients messages about the need to update directories.
        self.server.send_update_list()
        self.close()


if __name__ == '__main__':
    # Create an application object.
    APP = QApplication(sys.argv)
    # Create a message dialog box.
    MESSAGE = QMessageBox
    DEL_WINDOW = DeleteUserWindow(None, None)
    # Application launch (event polling cycle).
    APP.exec_()
