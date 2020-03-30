"""The module describes the GUI of the main window of clients."""

from PyQt5 import QtCore, QtWidgets


class Gui_MainClientWindow(object):
    """
    The class describes the GUI of the main window of clients.
    """
    def setupUi(self, MainClientWindow):
        """The method creates interface elements of the main window."""
        MainClientWindow.setObjectName('MainClientWindow')
        MainClientWindow.resize(700, 621)
        MainClientWindow.setMinimumSize(QtCore.QSize(700, 621))
        
        self.centralwidget = QtWidgets.QWidget(MainClientWindow)
        self.centralwidget.setObjectName('centralwidget')

        # Contact list header.
        self.contact_text = QtWidgets.QLabel(self.centralwidget)
        self.contact_text.setGeometry(QtCore.QRect(10, 5, 150, 20))
        self.contact_text.setObjectName('contact_text')

        # Contact list field.
        self.contact_list = QtWidgets.QListView(self.centralwidget)
        self.contact_list.setGeometry(QtCore.QRect(10, 30, 200, 530))
        self.contact_list.setObjectName('contact_list')

        # Add contact Button.
        self.add_contact_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_contact_button.setGeometry(QtCore.QRect(17, 562, 90, 30))
        self.add_contact_button.setObjectName('add_contact_button')

        # Delete Contact Button.
        self.delete_button = QtWidgets.QPushButton(self.centralwidget)
        self.delete_button.setGeometry(QtCore.QRect(108, 562, 90, 30))
        self.delete_button.setObjectName('delete_button')

        # Message story header.
        self.message_story_text = QtWidgets.QLabel(self.centralwidget)
        self.message_story_text.setGeometry(QtCore.QRect(220, 5, 150, 20))
        self.message_story_text.setObjectName('message_story_text')

        # Message story field.
        self.message_story_field = QtWidgets.QListView(self.centralwidget)
        self.message_story_field.setGeometry(QtCore.QRect(220, 30, 469, 400))
        self.message_story_field.setObjectName('message_story_field')

        # Message text.
        self.message_text = QtWidgets.QLabel(self.centralwidget)
        self.message_text.setGeometry(QtCore.QRect(220, 436, 100, 20))
        self.message_text.setObjectName('message_text')

        # New message text field.
        self.new_message_field = QtWidgets.QTextEdit(self.centralwidget)
        self.new_message_field.setGeometry(QtCore.QRect(220, 460, 469, 100))
        self.new_message_field.setObjectName('new_message_field')

        # new_message field send button.
        self.send_button = QtWidgets.QPushButton(self.centralwidget)
        self.send_button.setGeometry(QtCore.QRect(460, 562, 110, 30))
        self.send_button.setObjectName('send_button')

        # new_message field clear button.
        self.clear_message_button = QtWidgets.QPushButton(self.centralwidget)
        self.clear_message_button.setGeometry(QtCore.QRect(338, 562, 110, 30))
        self.clear_message_button.setObjectName('clear_message_button')
        
        MainClientWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainClientWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 756, 21))
        self.menubar.setObjectName('menubar')
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName('menu')
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName('menu_2')
        MainClientWindow.setMenuBar(self.menubar)
        self.statusBar = QtWidgets.QStatusBar(MainClientWindow)
        self.statusBar.setObjectName('statusBar')
        MainClientWindow.setStatusBar(self.statusBar)
        self.menu_exit = QtWidgets.QAction(MainClientWindow)
        self.menu_exit.setObjectName('menu_exit')
        self.menu_add_contact = QtWidgets.QAction(MainClientWindow)
        self.menu_add_contact.setObjectName('menu_add_contact')
        self.menu_del_contact = QtWidgets.QAction(MainClientWindow)
        self.menu_del_contact.setObjectName('menu_del_contact')
        self.menu.addAction(self.menu_exit)
        self.menu_2.addAction(self.menu_add_contact)
        self.menu_2.addAction(self.menu_del_contact)
        self.menu_2.addSeparator()
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())

        self.retranslateUi(MainClientWindow)
        self.clear_message_button.clicked.connect(self.new_message_field.clear)
        QtCore.QMetaObject.connectSlotsByName(MainClientWindow)

    def retranslateUi(self, MainClientWindow):
        """The method assigns Russian-language names to interface elements."""
        _translate = QtCore.QCoreApplication.translate
        MainClientWindow.setWindowTitle(_translate('MainClientWindow', 'Messenger'))
        self.contact_text.setText(_translate('MainClientWindow', 'Список контактов: '))
        self.add_contact_button.setText(_translate('MainClientWindow', 'Добавить'))
        self.delete_button.setText(_translate('MainClientWindow', 'Удалить'))
        self.message_story_text.setText(_translate('MainClientWindow', 'История сообщений: '))
        self.message_text.setText(_translate('MainClientWindow', 'Сообщение: '))
        self.send_button.setText(_translate('MainClientWindow', 'Отправить'))
        self.clear_message_button.setText(_translate('MainClientWindow', 'Очистить'))
        self.menu.setTitle(_translate('MainClientWindow', 'Файл'))
        self.menu_2.setTitle(_translate('MainClientWindow', 'Контакты'))
        self.menu_exit.setText(_translate('MainClientWindow', 'Выход'))
        self.menu_add_contact.setText(_translate('MainClientWindow', 'Добавить контакт'))
        self.menu_del_contact.setText(_translate('MainClientWindow', 'Удалить контакт'))

