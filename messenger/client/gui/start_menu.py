"""The module describes a menu for entering a username at program startup."""

import sys
from PyQt5.QtWidgets import QDialog, QApplication, QLabel, QLineEdit, \
    QPushButton, qApp


class AuthMenu(QDialog):
    """
    The class describes the start menu for entering a username.
    """
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setFixedSize(200, 140)
        self.setWindowTitle('Авторизация')

        # Text for username input field.
        self.auth_name_text = QLabel('Имя пользователя: ', self)
        self.auth_name_text.move(10, 5)
        self.auth_name_text.setFixedSize(180, 20)

        # Username input field.
        self.auth_name_field = QLineEdit(self)
        self.auth_name_field.move(10, 25)
        self.auth_name_field.setFixedSize(180, 20)

        # Text for password input field.
        self.password_text = QLabel('Пароль: ', self)
        self.password_text.move(10, 50)
        self.password_text.setFixedSize(180, 20)

        # Password input field.
        self.password_field = QLineEdit(self)
        self.password_field.move(10, 70)
        self.password_field.setFixedSize(180, 20)
        self.password_field.setEchoMode(QLineEdit.Password)

        # Login button.
        self.login_button = QPushButton('Войти', self)
        self.login_button.move(18, 100)
        self.login_button.clicked.connect(self.check_not_empty)

        # Exit button.
        self.exit_button = QPushButton('Выход', self)
        self.exit_button.move(100, 100)
        self.exit_button.clicked.connect(qApp.exit)

        self.show()

    def check_not_empty(self):
        """
        Button handler login_button. If the field is not empty, then change
        the ok_pressed flag to True and close the window.
        """
        if self.auth_name_field.text() and self.password_field.text():
            self.ok_pressed = True
            qApp.exit()


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    START_MENU = AuthMenu()
    APP.exec_()
