"""A module describes a menu for removing a user from the contact list"""
from sys import argv
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QComboBox, QPushButton


class DeleteContact(QDialog):
    """
    The class describes the menu for removing user from the contact list.
    """
    def __init__(self, database):
        self.database = database
        super().__init__()

        self.setFixedSize(228, 95)
        self.setWindowTitle('Удаление контакта')

        # Text for QComboBox.
        self.menu_text = QLabel('Выберите контакт для удаления: ', self)
        self.menu_text.move(10, 5)
        self.menu_text.setFixedSize(250, 20)

        # Drop menu.
        self.drop_menu = QComboBox(self)
        self.drop_menu.move(10, 30)
        self.drop_menu.setFixedSize(205, 20)

        # Delete button.
        self.delete_button = QPushButton('Удалить', self)
        self.delete_button.move(22, 60)
        self.delete_button.setFixedSize(90, 30)

        # Cancel button.
        self.cancel_button = QPushButton('Отмена', self)
        self.cancel_button.move(114, 60)
        self.cancel_button.setFixedSize(90, 30)
        self.cancel_button.clicked.connect(self.close)

        # Get the contact list from the database.
        if database:
            self.selector.addItems(sorted(self.database.get_all_contacts()))

        self.show()


if __name__ == '__main__':
    app = QApplication(argv)
    del_menu = DeleteContact(None)
    app.exec_()
