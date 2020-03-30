"""The module describes the main window of clients."""

import base64
import sys
from json import JSONDecodeError
from logging import getLogger
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QMessageBox
sys.path.append('../')
from client.custom.variables import ENCODING, MESSAGE_TEXT, SENDER, RECIPIENT
from client.custom.errors import ServerError
from client.gui.add_contact import AddContact
from client.gui.delete_contact import DeleteContact
from client.gui.main_window_gui import Gui_MainClientWindow

# Initialize the logger.
LOGGER = getLogger('client_logger')


class ClientMainWindow(QMainWindow):
    """
    Class - the main window of the user.
    It contains all the basic logic of the client module.
    """
    def __init__(self, client_name, database, transport, keys):
        super().__init__()
        # Main parameters.
        self.client_name = client_name
        self.database = database
        self.transport = transport

        # Message decryptor object with a preloaded key.
        self.decrypter = PKCS1_OAEP.new(keys)

        # Load configuration.
        self.gui = Gui_MainClientWindow()
        self.gui.setupUi(self)

        # Send message button.
        self.gui.send_button.clicked.connect(self.send_message)

        # Add contact.
        self.gui.add_contact_button.clicked.connect(self.add_contact_window)

        # Remove contact.
        self.gui.delete_button.clicked.connect(self.remove_contact_window)

        # Additional attributes.
        self.contact_model = None
        self.history_model = None
        self.current_chat = None
        self.current_chat_key = None
        self.cryptographer = None
        self.messages = QMessageBox()
        # Disable a horizontal scrollbar and enable word wrap.
        self.gui.message_story_field.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.gui.message_story_field.setWordWrap(True)

        # Send double-click on contact_list to the handler.
        self.gui.contact_list.doubleClicked.connect(self.select_active_user)

        self.client_list_update()
        self.set_disabled_input()
        self.show()

    def client_list_update(self):
        """
        The method updates the contact list.
        """
        contact_list = self.database.get_all_contacts()
        self.contact_model = QStandardItemModel()
        for i in sorted(contact_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contact_model.appendRow(item)
        self.gui.contact_list.setModel(self.contact_model)

    def send_message(self):
        """
        The method encrypts and sends messages to the user.
        """
        # Get the text from the new_message_field and clear the field.
        message_text = self.gui.new_message_field.toPlainText()
        self.gui.new_message_field.clear()
        if not message_text:
            return
        # Encrypt the message with the recipient key and package it in base64.
        message_text_encrypted = self.cryptographer.encrypt(message_text.encode(ENCODING))
        message_text_encrypted_base64 = base64.b64encode(message_text_encrypted)
        try:
            self.transport.create_message(
                self.current_chat,
                message_text_encrypted_base64.decode('ascii')
            )
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
        """
        # Get message history received by date.
        message_list = sorted(
            self.database.get_message_history(chat=self.current_chat),
            key=lambda item: item[0]
        )

        # Create a model if not created.
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.gui.message_story_field.setModel(self.history_model)
        # Clear old records.
        self.history_model.clear()
        # Show no more than 20 recent entries.
        length = len(message_list)
        start_index = 0

        if length > 20:
            start_index = length - 20
        # Fill the model with records. Separate incoming and outgoing messages
        # in color. Records in the reverse order, so select them from the end
        # and no more than 20.
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
        self.gui.message_story_field.scrollToBottom()

    def add_contact_window(self):
        """
        Method creating a window - dialog for adding a contact
        """
        global SELECT_DIALOG
        SELECT_DIALOG = AddContact(self.transport, self.database)
        SELECT_DIALOG.add_button.clicked.connect(lambda: self.add_contact_action(SELECT_DIALOG))
        SELECT_DIALOG.show()

    def add_contact_action(self, item):
        """
        Method gets username from drop_menu.\n
        :param obj item: class object.
        """
        # Get contact name (str).
        new_contact = item.drop_menu.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, item):
        """
        The method of adding a contact to the server and client database.
        After updating the database, the contents of the window are also updated.\n
        :param str item: username.
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
            LOGGER.info(f'Пользователь {new_contact} добавлен в список контактов.')
            self.messages.information(self, 'Успех', 'Контакт добавлен.')

    def remove_contact_window(self):
        """
        Method creating a window for deleting a contact.
        """
        global REMOVE_DIALOG
        REMOVE_DIALOG = DeleteContact(self.database)
        REMOVE_DIALOG.delete_button.clicked.connect(lambda: self.delete_contact(REMOVE_DIALOG))
        REMOVE_DIALOG.show()

    def delete_contact(self, item):
        """
        Method removing contact from server and client database. After updating
        the database, the contents of the window are also updated.
        :param obj item: class object.
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
        """
        # User is in selected item in QListView.
        self.current_chat = self.gui.contact_list.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        """
        The method of activating chat with the interlocutor.
        """
        # Request the public key of the user and create an encryption object.
        try:
            self.current_chat_key = self.transport.get_key_from_server(self.current_chat)
            LOGGER.debug(f'Загружен открытый ключ для {self.current_chat}')
            if self.current_chat_key:
                self.cryptographer = PKCS1_OAEP.new(RSA.import_key(self.current_chat_key))
        except (OSError, JSONDecodeError):
            self.current_chat_key = None
            self.cryptographer = None
            LOGGER.debug(f'Не удалось получить ключ для {self.current_chat}')

        # If there is no key, then the error is that it was not possible
        # to start a chat with the user.
        if not self.current_chat_key:
            self.messages.warning(self, 'Ошибка', 'Для пользователя нет ключа шифрования.')
            return

        # Activate the buttons and input field.
        self.gui.new_message_field.setDisabled(False)
        self.gui.send_button.setDisabled(False)
        self.gui.clear_message_button.setDisabled(False)
        # Fill the window with message history.
        self.history_list_update()

    def set_disabled_input(self):
        """
        Deactivate the input field.
        """
        self.gui.new_message_field.clear()
        if self.history_model:
            self.history_model.clear()

        # New_message_field and send_button are inactive until the recipient is selected.
        self.gui.new_message_field.setDisabled(True)
        self.gui.send_button.setDisabled(True)
        self.gui.clear_message_button.setDisabled(True)

        self.cryptographer = None
        self.current_chat = None
        self.current_chat_key = None

    @pyqtSlot(dict)
    def new_message(self, message):
        """
        The slot handler of incoming messages, decrypts incoming messages
        and stores them in the message history. Asks the user if a message was
        received not from the current interlocutor. If necessary,
        change the interlocutor.\n
        :param dict message: message dict.
        """
        # Get a string of bytes.
        encrypted_message = base64.b64decode(message[MESSAGE_TEXT])
        # Decode a string, if an error occurs, display a message and end the function.
        try:
            decrypted_message = self.decrypter.decrypt(encrypted_message)
        except (ValueError, TypeError):
            self.messages.warning(self, 'Ошибка', 'Не удалось декодировать сообщение.')
            return
        self.database.save_message(message[SENDER],
                                   message[RECIPIENT],
                                   decrypted_message.decode(ENCODING)
                                   )
        sender = message[SENDER]
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
                    # You need to save the message again, otherwise it will be lost,
                    # because at the time of the previous call there was no contact.
                    self.database.save_message(message[SENDER],
                                               message[RECIPIENT],
                                               decrypted_message.decode(ENCODING)
                                               )
                    self.set_active_user()

    @pyqtSlot()
    def connection_loss(self):
        """
        The slot handler is a loss of connection to the server.
        Gives a warning window and terminates the application.\n
        """
        self.messages.warning(self, 'Сбой связи', 'Потеряно соединение с сервером.')
        self.close()

    @pyqtSlot()
    def signal_205(self):
        """
        Message slot 205 - a request by the server to update directories of available users and
        contacts. It may turn out that the current person is deleted, you need to check this and
        close the chat with a warning. Otherwise, just update the contact list without giving a
        warning to the user.\n
        """
        if self.current_chat and not self.database.check_registered_user(self.current_chat):
            self.messages.warning(self, 'Ошибка', 'Собеседник был удалён с сервера.')
            self.set_disabled_input()
            self.current_chat = None
        self.client_list_update()

    def make_connection(self, transport):
        """
        Connection Creation Method.\n
        :param obj transport: socket object.
        """
        transport.new_message.connect(self.new_message)
        transport.connection_loss.connect(self.connection_loss)
        transport.message_205.connect(self.signal_205)
