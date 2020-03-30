"""The module describes the server GUI settings window."""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QLabel, \
    QLineEdit, QPushButton, QFileDialog


class ConfigWindow(QDialog):
    """
    The class describes the settings window.
    """
    def __init__(self):
        super().__init__()
        # Call the constructor.
        self.initUI()

    def initUI(self):
        """The method creates interface elements of the main window."""
        self.setFixedSize(370, 200)
        self.setWindowTitle('Настройки сервера')

        # Text to the line with the path to the database.
        self.db_path_text = QLabel('Путь к файлу БД: ', self)
        self.db_path_text.move(15, 15)
        self.db_path_text.setFixedSize(240, 15)

        # The path to the database.
        self.db_path = QLineEdit(self)
        self.db_path.move(15, 35)
        self.db_path.setFixedSize(250, 20)
        self.db_path.setReadOnly(True)

        # Button to select the path to the database.
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(270, 30)

        # The text for the database file name field.
        self.db_file_text = QLabel('Имя файла БД: ', self)
        self.db_file_text.move(15, 70)
        self.db_file_text.setFixedSize(150, 20)

        # Field for entering database file name.
        self.db_file_name = QLineEdit(self)
        self.db_file_name.move(125, 70)
        self.db_file_name.setFixedSize(235, 20)

        # Текст для поля ввода IP-адреса.
        self.ip_address_text = QLabel('IP-адрес: ', self)
        self.ip_address_text.move(15, 95)
        self.ip_address_text.setFixedSize(150, 20)

        # A field for entering an IP address.
        self.ip_address_field = QLineEdit(self)
        self.ip_address_field.move(125, 95)
        self.ip_address_field.setFixedSize(235, 20)

        # Text for port input field.
        self.port_text = QLabel('Порт: ', self)
        self.port_text.move(15, 120)
        self.port_text.setFixedSize(150, 20)

        # Field for entering the port.
        self.port_field = QLineEdit(self)
        self.port_field.move(125, 120)
        self.port_field.setFixedSize(235, 20)

        # Button for saving settings.
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(80, 155)

        # Button to close the window.
        self.close_button = QPushButton(' Закрыть ', self)
        self.close_button.move(190, 155)
        self.close_button.clicked.connect(self.close)

        self.db_path_select.clicked.connect(self.open_path_select)

        self.show()

    def open_path_select(self):
        """
        The handler method opens the path selection window.
        """
        window = QFileDialog()
        path = window.getExistingDirectory()
        self.db_path.insert(path)


if __name__ == '__main__':
    # Create an application object.
    APP = QApplication(sys.argv)
    # Create a message box.
    MESSAGE = QMessageBox
    # Test settings menu.
    CONFIG_WINDOW = ConfigWindow()
    # Application launch (event polling cycle).
    APP.exec_()
