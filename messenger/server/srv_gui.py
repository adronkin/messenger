"""Модуль для реализации GUI сервера"""
from sys import argv

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox, QDialog, QLabel, QLineEdit, QPushButton, \
    QFileDialog, QMainWindow, QAction, qApp, QTableView


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

        def open_path_select():
            """
            Метод обработчик открытия окна выбора пути.
            :return:
            """
            window = QFileDialog()
            path = window.getExistingDirectory()
            self.db_path.insert(path)

        self.db_path_select.clicked.connect(open_path_select)

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
        # TODO написать действия для save_button

        # Кнопка закрытия окна
        self.close_button = QPushButton(' Закрыть ', self)
        self.close_button.move(190, 155)
        self.close_button.clicked.connect(self.close)

        self.show()


class MainWindow(QMainWindow):
    """
    Класс описывающий главное окно.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedSize(700, 600)
        self.setWindowTitle('Server menu')

        # Кнопка выход.
        self.exitAction = QAction('Выход', self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.triggered.connect(qApp.quit)

        # Кнопка обновить список клиентов.
        self.refresh_button = QAction('Обновить', self)

        # Кнопка настроек сервера.
        self.setting_button = QAction('Настройки', self)

        self.statusBar()

        # Тулбар.
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(self.exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.setting_button)

        # Текст к таблице подключенных клиентов.
        self.active_text = QLabel('Подключенные клиенты: ', self)
        self.active_text.move(15, 30)
        self.active_text.setFixedSize(235, 20)

        # Таблица со списком подключенных клиентов.
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(5, 55)
        self.active_clients_table.setFixedSize(690, 515)

        self.show()


def gui_active_users(database):
    """
    Создание таблицы активных пользователей для отображения в окне программы.
    :param database: база данных.
    :return: экземпляр класса QStandardItemModel.
    """
    list_users = database.get_all_active_users()
    active_user_list = QStandardItemModel()
    active_user_list.setHorizontalHeaderLabels(['Имя клиента', 'IP-адрес',
                                                'Порт', 'Время подключения'])
    for row in list_users:
        user, ip, port, time = row
        user = QStandardItem(user)
        user.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(port)
        port.setEditable(False)
        # Убираем миллисекунды.
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        active_user_list.appendRow([user, ip, port, time])
    return active_user_list


if __name__ == '__main__':
    # Создаем объект приложения.
    app = QApplication(argv)
    # Создаем диалоговое окно сообщения.
    message = QMessageBox
    # Тест меню настроек.
    # config_window = ConfigWindow()
    # Тест основного окна.
    main_window = MainWindow()
    main_window.statusBar().showMessage('Test run')
    test_list = QStandardItemModel(main_window)
    test_list.setHorizontalHeaderLabels(['Имя клиента', 'IP-адрес', 'Порт', 'Время подключения'])
    test_list.appendRow([QStandardItem('test_user_1'), QStandardItem('127.0.0.1'),
                         QStandardItem('53245'), QStandardItem('2020-01-01 15:36')])
    test_list.appendRow([QStandardItem('test_user_2'), QStandardItem('127.0.0.1'),
                         QStandardItem('52123'), QStandardItem('2020-01-02 12:21')])
    main_window.active_clients_table.setModel(test_list)
    main_window.active_clients_table.resizeColumnsToContents()

    # Запускаем приложение (цикл опроса событий).
    app.exec_()
