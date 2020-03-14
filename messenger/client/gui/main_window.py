"""The module describes the main window of clients"""

import sys
from logging import getLogger
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox
sys.path.append('../')
from gui.add_contact import AddContact
from gui.delete_contact import DeleteContact
from gui.main_window_gui import Ui_MainClientWindow
from custom.errors import ServerError
import log.log_config

# Initialize the logger.
LOGGER = getLogger('client_logger')


class ClientMainWindow(QMainWindow):
    """
    The class describes the main window of clients.
    """
    def __init__(self, client_name, database, transport):
        super().__init__()
        # Main parameters.
        self.client_name = client_name
        self.database = database
        self.transport = transport

        # Load configuration.
        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        # Send message button.
        self.ui.send_button.clicked.connect(self.send_message)

        # Add contact.
        self.ui.add_contact_button.clicked.connect(self.add_contact_window)

        # Remove contact.
        self.ui.delete_button.clicked.connect(self.remove_contact_window)

        # Additional attributes.
        self.contact_model = None
        self.history_model = None
        self.current_chat = None
        self.messages = QMessageBox()
        # Disable a horizontal scrollbar and enable word wrap.
        self.ui.message_story_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.message_story_field.setWordWrap(True)

        # Send double-click on contact_list to the handler.
        self.ui.contact_list.doubleClicked.connect(self.select_active_user)

        self.client_list_update()
        self.set_disabled_input()
        self.show()

    def client_list_update(self):
        """
        The method updates the contact list.
        :return:
        """
        contact_list = self.database.get_all_contacts()
        self.contact_model = QStandardItemModel()
        for i in sorted(contact_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contact_model.appendRow(item)
        self.ui.contact_list.setModel(self.contact_model)

    def send_message(self):
        """
        Method sends messages to the user.
        :return:
        """
        # Get the text from the new_message_field and clear the field.
        message_text = self.ui.new_message_field.toPlainText()
        self.ui.new_message_field.clear()
        if not message_text:
            return
        try:
            self.transport.create_message(self.current_chat, message_text)
            pass
        except ServerError as error:
            self.messages.critical(self, 'Ошибка', error.text)
        except OSError as error:
            if error.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером.')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения.')
        except (ConnectionAbortedError, ConnectionResetError):
            self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером.')
            self.close()
        else:
            self.database.save_message(self.client_name, self.current_chat, message_text)
            LOGGER.debug(f'Отправлено сообщение для пользователя'
                         f' {self.current_chat}: {message_text}')
            self.history_list_update()

    def history_list_update(self):
        """
        The method fills the message history.
        :return:
        """
        # Get message history received by date.
        message_list = sorted(self.database.get_message_history(chat=self.current_chat),
                              key=lambda item: item[0])
        # Create a model if not created.
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.message_story_field.setModel(self.history_model)
        # Clear old records.
        self.history_model.clear()
        # Show no more than 20 recent entries.
        length = len(message_list)
        start_index = 0
        if length > 20:
            start_index = length - 20
        # Fill the model with records. Separate incoming and outgoing messages in color.
        # Records in the reverse order, so select them from the end and no more than 20.
        for i in range(start_index, length):
            item = message_list[i]
            # Incoming messages.
            if item[2] == self.client_name:
                message = QStandardItem(f'{item[0].replace(microsecond=0)} {item[1]}:\n {item[3]}')
                message.setEditable(False)
                message.setTextAlignment(Qt.AlignLeft)
                message.setBackground(QBrush(QColor(208, 208, 240)))
                self.history_model.appendRow(message)
            # Outgoing messages.
            else:
                message = QStandardItem(f'{item[0].replace(microsecond=0)} {item[1]}:\n {item[3]}')
                message.setEditable(False)
                message.setTextAlignment(Qt.AlignRight)
                message.setBackground(QBrush(QColor(255, 255, 255)))
                self.history_model.appendRow(message)
        self.ui.message_story_field.scrollToBottom()

    def add_contact_window(self):
        """
        Method for adding a contact.
        :return:
        """
        global select_dialog
        select_dialog = AddContact(self.transport, self.database)
        select_dialog.add_button.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        """
        Method gets username from drop_menu.
        :param item: class object.
        :return:
        """
        # Get contact name (str).
        new_contact = item.drop_menu.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, item):
        """
        Method, informs the server, updates the table,
        contact list and add a contact to the database.
        :param {str} item: username.
        :return:
        """
        try:
            self.transport.add_contact_to_server(item)
        except ServerError as error:
            self.messages.critical(self, 'Ошибка', error.text)
        except OSError as error:
            if error.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером.')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения.')
        else:
            self.database.add_contact(item)
            new_contact = QStandardItem(item)
            new_contact.setEditable(False)
            self.contact_model.appendRow(new_contact)
            LOGGER.info(f'Пользователь {new_contact} успешно добавлен в список контактов.')
            self.messages.information(self, 'Успех', f'Контакт добавлен.')

    def remove_contact_window(self):
        """
        Method for remove a contact.
        :return:
        """
        global remove_dialog
        remove_dialog = DeleteContact(self.database)
        remove_dialog.delete_button.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        """
        Remove handler method, informs the server, updates the table and contact list.
        :param {obj} item: class object.
        :return:
        """
        # Get contact name (str).
        contact = item.drop_menu.currentText()
        try:
            self.transport.remove_contact_to_server(contact)
        except ServerError as error:
            self.messages.critical(self, 'Ошибка', error.text)
        except OSError as error:
            if error.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером.')
                self.close()
            # TODO проверить, почему часто возникает timed out
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения.')
        else:
            self.database.delete_contact(contact)
            self.client_list_update()
            LOGGER.info(f'Пользователь {contact} успешно удален из списка контактов.')
            self.messages.information(self, 'Успех', f'Контакт удален.')
            item.close()
            # If the active user is deleted, then deactivate the input fields.
            if contact == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def select_active_user(self):
        """
        Method handles double-click on contact.
        :return:
        """
        # User is in selected item in QListView.
        self.current_chat = self.ui.contact_list.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        """
        Method establishes the active user.
        :return:
        """
        # Activate the buttons and input field.
        self.ui.new_message_field.setDisabled(False)
        self.ui.send_button.setDisabled(False)
        self.ui.clear_message_button.setDisabled(False)
        # Fill the window with message history.
        self.history_list_update()

    def set_disabled_input(self):
        """
        Deactivate the input field.
        :return:
        """
        self.ui.new_message_field.clear()
        if self.history_model:
            self.history_model.clear()

        # new_message_field and send_button are inactive until the recipient is selected.
        self.ui.new_message_field.setDisabled(True)
        self.ui.send_button.setDisabled(True)
        self.ui.clear_message_button.setDisabled(True)

    @pyqtSlot(str)
    def new_message(self, sender):
        """
        Receive new message slot.
        :param {str} sender: message sender username.
        :return:
        """
        if sender == self.current_chat:
            self.history_list_update()
        else:
            # Check if we have such a user in contacts.
            if self.database.check_contact(sender):
                # If true, ask whether to open a chat.
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender},'
                                          f' открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                # If False, ask if we want to add the user to contacts.
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}.\n'
                                          f' Данного пользователя нет в вашем контакт-листе.\n'
                                          f' Добавить в контакты и открыть чат с ним?',
                                          QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_loss(self):
        """
        Connection loss slot.
        :return:
        """
        self.messages.warning(self, 'Сбой связи', 'Потеряно соединение с сервером.')
        self.close()

    def make_connection(self, transport):
        """
        Connection Creation Method.
        :param {obj} transport: socket object.
        :return:
        """
        transport.new_message.connect(self.new_message)
        transport.connection_loss.connect(self.connection_loss)
