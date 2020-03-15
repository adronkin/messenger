"""Модуль описывает окно настроек GUI сервера"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QLabel, QLineEdit, QPushButton, \
    QFileDialog


class ConfigWindow(QDialog):
    """
    Класс описывающий окно настроек.
    """
    def __init__(self):
        super().__init__()
        # Вызываем конструктор.
        self.initUI()

    def initUI(self):
        # Настройки окна (задаем фиксированный размер окна и заголовок).
        self.setFixedSize(370, 200)
        self.setWindowTitle('Настройки сервера')

        # Текст к строке с путем к БД.
        self.db_path_text = QLabel('Путь к файлу БД: ', self)
        self.db_path_text.move(15, 15)
        self.db_path_text.setFixedSize(240, 15)

        # Путь к БД.
        self.db_path = QLineEdit(self)
        self.db_path.move(15, 35)
        self.db_path.setFixedSize(250, 20)
        self.db_path.setReadOnly(True)

        # Кнопка выбора пути к БД.
        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(270, 30)

        # Текст для поля имени файла БД.
        self.db_file_text = QLabel('Имя файла БД: ', self)
        self.db_file_text.move(15, 70)
        self.db_file_text.setFixedSize(150, 20)

        # Поле для ввода имени файла БД.
        self.db_file_name = QLineEdit(self)
        self.db_file_name.move(125, 70)
        self.db_file_name.setFixedSize(235, 20)

        # Текст для поля ввода IP-адреса.
        self.ip_address_text = QLabel('IP-адрес: ', self)
        self.ip_address_text.move(15, 95)
        self.ip_address_text.setFixedSize(150, 20)

        # Поле для ввода IP-адреса.
        self.ip_address_field = QLineEdit(self)
        self.ip_address_field.move(125, 95)
        self.ip_address_field.setFixedSize(235, 20)

        # Текст для поля ввода порта.
        self.port_text = QLabel('Порт: ', self)
        self.port_text.move(15, 120)
        self.port_text.setFixedSize(150, 20)

        # Поле для ввода порта.
        self.port_field = QLineEdit(self)
        self.port_field.move(125, 120)
        self.port_field.setFixedSize(235, 20)

        # Кнопка для сохранения настроек.
        self.save_button = QPushButton('Сохранить', self)
        self.save_button.move(80, 155)

        # Кнопка закрытия окна
        self.close_button = QPushButton(' Закрыть ', self)
        self.close_button.move(190, 155)
        self.close_button.clicked.connect(self.close)

        self.db_path_select.clicked.connect(self.open_path_select)

        self.show()

    def open_path_select(self):
        """
        Метод обработчик открытия окна выбора пути.
        :return:
        """
        window = QFileDialog()
        path = window.getExistingDirectory()
        self.db_path.insert(path)


if __name__ == '__main__':
    # Создаем объект приложения.
    app = QApplication(sys.argv)
    # Создаем диалоговое окно сообщения.
    message = QMessageBox
    # Тест меню настроек.
    config_window = ConfigWindow()
    # Запускаем приложение (цикл опроса событий).
    app.exec_()
