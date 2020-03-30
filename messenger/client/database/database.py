"""Client Database Description Module."""

import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Index, DateTime, Text, \
    create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a base class for declarative work.
BASE = declarative_base()


class ClientDataBase:
    """
    A class describing database tables and client methods.
    """
    class Contacts(BASE):
        """
        The class describes a table with a list of user contacts.\n
        Stores data: id, username.
        """
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)
        __table_args__ = (Index('contacts_index', 'id'), )

        def __init__(self, username):
            self.username = username

    class MessageHistory(BASE):
        """
        The class describes a table with the user's correspondence history.\n
        Stores data: id, sender, recipient, date, message.
        """
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        sender = Column(String)
        recipient = Column(String)
        date = Column(DateTime)
        message = Column(Text)
        __table_args__ = (Index('message_history_index', 'id', 'sender', 'recipient'), )

        def __init__(self, sender, recipient, message):
            self.sender = sender
            self.recipient = recipient
            self.date = datetime.now()
            self.message = message

    class RegisteredUsers(BASE):
        """
        The class describes a table of users registered in the application.\n
        Stores data: id, username.
        """
        __tablename__ = 'registered_users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)
        __table_args__ = (Index('registered_users_index', 'id'), )

        def __init__(self, username):
            self.username = username

    def __init__(self, name):
        # Create a database (echo - logging through the standard logging module).
        # Because multiple clients are allowed at the same time, each must have its own database.
        # Since the client is multi-threaded, it is necessary to disable
        # connection checks from different threads, otherwise sqlite3.ProgrammingError
        self.engine = create_engine(
            f'sqlite:///{"/".join(map(str, os.path.dirname(__file__).split("/")[:-1]))}'
            f'/database/client_{name.lower()}_database.db3',
            echo=False,
            pool_recycle=3600,
            connect_args={'check_same_thread': False}
        )

        # Create tables.
        BASE.metadata.create_all(self.engine)

        # Create session.
        session_engine = sessionmaker(bind=self.engine)
        self.session = session_engine()

        # After connecting, clear the contact table,
        # as they are downloaded from the server.
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def clear_contacts(self):
        """
        Method for clearing the contact list.
        """
        self.session.query(self.Contacts).delete()

    def check_contact(self, username):
        """
        The method returns True if the user is in the contact list.\n
        :param str username: username.
        :return: bool.
        """
        q_user = self.session.query(self.Contacts).filter_by(username=username)
        if q_user.count():
            return True

    def add_contact(self, username):
        """
        The method adds the user to the contact list if he is not in the table.\n
        :param str username: username.
        """
        if self.check_contact(username):
            return
        new_contact = self.Contacts(username)
        self.session.add(new_contact)
        self.session.commit()

    def delete_contact(self, username):
        """
        The method removes the user from the contact list, if it is in the table.\n
        :param str username: username.
        """
        if not self.check_contact(username):
            print(f'Пользователь {username} отсутствует в списке контактов.')
            return
        self.session.query(self.Contacts).filter_by(username=username).delete()
        self.session.commit()

    def get_all_contacts(self):
        """
        The method returns a list of contacts.\n
        :return: list of contacts.
        """
        return [contact[0] for contact in self.session.query(self.Contacts.username).all()]

    def save_message(self, sender, recipient, msg_text):
        """
        The method saves the message to the database.\n
        :param str sender: message sender.
        :param str recipient: the recipient of the message.
        :param str msg_text: message text.
        """
        new_message = self.MessageHistory(sender, recipient, msg_text)
        self.session.add(new_message)
        self.session.commit()

    def get_message_history(self, sender=None, recipient=None, chat=None):
        """
        The method returns the history of correspondence by recipient and/or sender.\n
        :param str sender: message sender.
        :param str recipient: the recipient of the message.
        :param str chat: message text.
        :return: list of messages.
        """
        query = self.session.query(self.MessageHistory)
        if sender:
            query = query.filter_by(sender=sender)
        if recipient:
            query = query.filter_by(recipient=recipient)
        if chat:
            query_s = query.filter_by(sender=chat)
            query_r = query.filter_by(recipient=chat)
            query = query_s.union(query_r)
        return [(msg.date, msg.sender, msg.recipient, msg.message)
                for msg in query.all()]

    def check_registered_user(self, username):
        """
        The method returns True if the user is registered on the server.\n
        :param str username: username.
        :return: bool.
        """
        q_user = self.session.query(self.RegisteredUsers).filter_by(username=username)
        if q_user.count():
            return True

    def add_register_users(self, user_list):
        """
        Method for adding users from the list to the RegisteredUsers table.\n
        :param str user_list: list of users registered on the server.
        """
        # Clear the table as the list of users is loaded from the server at startup.
        self.session.query(self.RegisteredUsers).delete()
        for user in user_list:
            reg_user = self.RegisteredUsers(user)
            self.session.add(reg_user)
        self.session.commit()

    def get_register_users(self):
        """
        The method returns a list of registered users.\n
        :return: list of registered users.
        """
        return [user[0] for user in self.session.query(self.RegisteredUsers.username).all()]


if __name__ == '__main__':
    TEST_DB = ClientDataBase('test')
    print(TEST_DB.get_all_contacts())
    print(TEST_DB.get_register_users())
