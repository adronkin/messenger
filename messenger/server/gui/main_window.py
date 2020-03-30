"""The module describes the main window."""

import sys
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMessageBox, QLabel, QMainWindow, QAction, qApp, \
    QTableView
sys.path.append('../')
from server.gui.add_user import AddUserWindow
from server.gui.del_user import DeleteUserWindow


class MainWindow(QMainWindow):
    """
    Class - the main window of the server.
    """
    def __init__(self, server, database):
        super().__init__()

        self.server = server
        self.database = database

        self.setFixedSize(700, 600)
        self.setWindowTitle('Server menu')

        # Exit button.
        self.exit_button = QAction('Выход', self)
        self.exit_button.setShortcut('Ctrl+Q')
        self.exit_button.triggered.connect(qApp.quit)

        # Client list refresh button.
        self.refresh_button = QAction('Обновить', self)
        # Setting button.
        self.setting_button = QAction('Настройки', self)
        # Register user button.
        self.register_user_button = QAction('Регистрация пользователя', self)
        # Delete user button.
        self.del_user_button = QAction('Удалить пользователя', self)

        self.statusBar()
        self.statusBar().showMessage('Server Working')

        # Toolbar.
        self.toolbar = self.addToolBar('Toolbar')
        self.toolbar.addAction(self.exit_button)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.setting_button)
        self.toolbar.addAction(self.register_user_button)
        self.toolbar.addAction(self.del_user_button)

        # Connected user table text.
        self.active_text = QLabel('Подключенные клиенты: ', self)
        self.active_text.move(15, 30)
        self.active_text.setFixedSize(235, 20)

        # Connected user table.
        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(5, 55)
        self.active_clients_table.setFixedSize(690, 515)

        # Associate buttons with procedures.
        self.refresh_button.triggered.connect(self.gui_active_users)
        self.register_user_button.triggered.connect(self.reg_user_window)
        self.del_user_button.triggered.connect(self.del_user_window)

        # The timer updates the client list 1 time per second.
        if database:
            self.timer = QTimer()
            self.timer.timeout.connect(self.gui_active_users)
            self.timer.start(1000)

        self.show()

    def reg_user_window(self):
        """
        The method calls the user registration window.
        """
        global REG_WINDOW
        REG_WINDOW = AddUserWindow(self.server, self.database)

    def del_user_window(self):
        """
        The method calls the user deletion window.
        """
        global DEL_WINDOW
        DEL_WINDOW = DeleteUserWindow(self.server, self.database)

    def gui_active_users(self):
        """
        The method creates a table of active users for display in the program window.\n
        :return: class instance QStandardItemModel.
        """
        list_users = self.database.get_all_active_users()
        active_user_list = QStandardItemModel()
        active_user_list.setHorizontalHeaderLabels([
            'Имя клиента',
            'IP-адрес',
            'Порт',
            'Время подключения'
        ])
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
        self.active_clients_table.setModel(active_user_list)
        self.active_clients_table.resizeColumnsToContents()
        self.active_clients_table.resizeRowsToContents()


if __name__ == '__main__':
    # Create an application object.
    APP = QApplication(sys.argv)
    # Create a message box.
    MESSAGE = QMessageBox
    # Create a message dialog box.
    MAIN_WINDOW = MainWindow(None, None)
    MAIN_WINDOW.statusBar().showMessage('Test run')
    TEST_LIST = QStandardItemModel(MAIN_WINDOW)
    TEST_LIST.setHorizontalHeaderLabels([
        'Имя клиента',
        'IP-адрес',
        'Порт',
        'Время подключения'
    ])
    TEST_LIST.appendRow([
        QStandardItem('test_user_1'),
        QStandardItem('127.0.0.1'),
        QStandardItem('53245'),
        QStandardItem('2020-01-01 15:36')
    ])
    TEST_LIST.appendRow([
        QStandardItem('test_user_2'),
        QStandardItem('127.0.0.1'),
        QStandardItem('52123'),
        QStandardItem('2020-01-02 12:21')
    ])
    MAIN_WINDOW.active_clients_table.setModel(TEST_LIST)
    MAIN_WINDOW.active_clients_table.resizeColumnsToContents()
    # Application launch (event polling cycle).
    APP.exec_()
