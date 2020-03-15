"""Модуль описывает главное окно GUI сервера"""

import sys
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QMainWindow, QAction, qApp, \
    QTableView


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
        port = QStandardItem(str(port))
        port.setEditable(False)
        # Убираем миллисекунды.
        time = QStandardItem(str(time.replace(microsecond=0)))
        time.setEditable(False)
        active_user_list.appendRow([user, ip, port, time])
    return active_user_list


if __name__ == '__main__':
    # Создаем объект приложения.
    app = QApplication(sys.argv)
    # Создаем диалоговое окно сообщения.
    message = QMessageBox
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
