"""The module describes the add user window."""

import binascii
import sys
from hashlib import pbkdf2_hmac
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QLabel, \
    QLineEdit, QPushButton
sys.path.append('../')
from server.custom.variables import ENCODING


class AddUserWindow(QDialog):
    """
    The class is a dialog for registering a user on the server.
    """
    def __init__(self, server, database):
        super().__init__()

        self.server = server
        self.database = database

        self.setFixedSize(250, 185)
        self.setWindowTitle('Регистрация пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        # Text for username field.
        self.username_text = QLabel('Введите имя пользователя: ', self)
        self.username_text.move(15, 5)
        self.username_text.setFixedSize(200, 20)

        # Username field.
        self.username = QLineEdit(self)
        self.username.move(15, 25)
        self.username.setFixedSize(220, 20)

        # Text for password field.
        self.password_text = QLabel('Введите пароль: ', self)
        self.password_text.move(15, 50)
        self.password_text.setFixedSize(200, 20)

        # Password field.
        self.password = QLineEdit(self)
        self.password.move(15, 70)
        self.password.setFixedSize(220, 20)
        self.password.setEchoMode(QLineEdit.Password)

        # Text for password confirmation field.
        self.password_confirm_text = QLabel('Подтвердите пароль: ', self)
        self.password_confirm_text.move(15, 95)
        self.password_confirm_text.setFixedSize(200, 20)

        # Password confirmation field.
        self.password_confirm = QLineEdit(self)
        self.password_confirm.move(15, 115)
        self.password_confirm.setFixedSize(220, 20)
        self.password_confirm.setEchoMode(QLineEdit.Password)

        # Save button.
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(34, 140)
        self.save_button.setFixedSize(90, 30)
        self.save_button.clicked.connect(self.save_data)

        # Cancel button.
        self.cancel_button = QPushButton('Отмена', self)
        self.cancel_button.move(126, 140)
        self.cancel_button.setFixedSize(90, 30)
        self.cancel_button.clicked.connect(self.close)

        self.messages = QMessageBox()

        self.show()

    def save_data(self):
        """
        The method checks the correctness of the input
        and saves the new user in the database.
        """
        if not self.username.text():
            self.messages.critical(
                self,
                'Ошибка',
                'Не введено имя пользователя.'
            )
            return
        elif self.database.check_user(self.username.text()):
            self.messages.critical(
                self,
                'Ошибка',
                f'Пользователь с именем {self.username.text()} существует.'
            )
            return
        elif self.password.text() != self.password_confirm.text():
            self.messages.critical(
                self,
                'Ошибка',
                'Введенные пароли не совпадают.'
            )
            return
        else:
            # Generate a password hash, use a lowercase login as a salt.
            password_bytes = self.password.text().encode(ENCODING)
            salt = self.username.text().lower().encode(ENCODING)
            password_hash = pbkdf2_hmac('sha512', password_bytes, salt, 10000)
            self.database.register_user(
                self.username.text(),
                binascii.hexlify(password_hash)
            )
            self.messages.information(
                self,
                'Успех',
                'Пользователь зарегистрирован.'
            )
            # Send clients messages about the need to update directories.
            self.server.send_update_list()
            self.close()


if __name__ == '__main__':
    # Create an application object.
    APP = QApplication(sys.argv)
    # Create a message dialog box.
    MESSAGE = QMessageBox
    DEL_WINDOW = AddUserWindow(None, None)
    # Application launch (event polling cycle).
    APP.exec_()
