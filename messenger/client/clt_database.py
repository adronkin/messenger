"""Модуль описания базы данных клиента."""

import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, Index, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Создаем базовый класс для декларативно работы.
BASE = declarative_base()


class ClientDataBase:
    """
    Класс описывающий таблицы БД и методы клиента.
    """
    class Contacts(BASE):
        """
        Класс описывает таблицу со списком контактов пользователя.
        """
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)
        __table_args__ = (Index('contacts_index', 'id'), )

        def __init__(self, username):
            self.username = username

    class MessageHistory(BASE):
        """
        Класс описывает таблицу с историей переписки пользователя.
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
        Класс описывает таблицу зарегистрированных в приложении пользователей.
        """
        __tablename__ = 'registered_users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)
        __table_args__ = (Index('registered_users_index', 'id'), )

        def __init__(self, username):
            self.username = username

    def __init__(self, name):
        # Создаем БД (echo - логирование через стандартный модуль logging).
        # Т.к. разрешено несколько клиентов одновременно, каждый должен иметь свою БД.
        # Поскольку клиент мультипоточный необходимо отключить проверки на подключения
        # с разных потоков, иначе sqlite3.ProgrammingError
        self.engine = create_engine(
            f'sqlite:///{"/".join(map(str, os.path.dirname(__file__).split("/")[:-1]))}'
            f'/client/database/client_{name.lower()}_database.db3',
            echo=False, pool_recycle=3600, connect_args={'check_same_thread': False})

        # Создаем таблицы
        BASE.metadata.create_all(self.engine)

        # Создаем сессию
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # После подключения очищаем таблицу контактов, т.к. они загружаются с сервера.
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def check_contact(self, username):
        """
        Метод возвращает True, если пользователь username есть в списке контактов.
        :param {str} username: имя пользователя.
        :return {bool}:
        """
        # Поиск в таблице Contacts пользователя с именем username
        q_user = self.session.query(self.Contacts).filter_by(username=username)
        if q_user.count():
            return True

    def add_contact(self, username):
        """
        Метод добавляет пользователя username в список контактов, если его нет в таблице.
        :param {str} username: имя пользователя.
        :return:
        """
        if self.check_contact(username):
            return
        new_contact = self.Contacts(username)
        self.session.add(new_contact)
        self.session.commit()

    def delete_contact(self, username):
        """
        Метод удаляет пользователя username из списока контактов, если он есть в таблице.
        :param {str} username: имя пользователя.
        :return:
        """
        if not self.check_contact(username):
            print(f'Пользователь {username} отсутствует в списке контактов.')
            return
        self.session.query(self.Contacts).filter_by(username=username).delete()
        self.session.commit()

    def get_all_contacts(self):
        """
        Метод возвращает список контактов.
        :return {list}:
        """
        return [contact[0] for contact in self.session.query(self.Contacts.username).all()]

    def save_message(self, sender, recipient, msg_text):
        """
        Метод сохраняет сообщение в базу.
        :param {str} sender: отправитель сообщения.
        :param {str} recipient: получатель сообщения.
        :param {str} msg_text: текст сообщения.
        :return:
        """
        new_message = self.MessageHistory(sender, recipient, msg_text)
        self.session.add(new_message)
        self.session.commit()

    def get_message_history(self, sender=None, recipient=None, chat=None):
        """
        Метод возвращает историю переписки по получателю и/или отправителю.
        :param {str} sender: отправитель сообщения.
        :param {str} recipient: получатель сообщения.
        :param {str} chat: получатель сообщения.
        :return:
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
        Метод возвращает True, если пользователь username зарегистрирован на сервере.
        :param {str} username: имя пользователя.
        :return {bool}:
        """
        q_user = self.session.query(self.RegisteredUsers).filter_by(username=username)
        if q_user.count():
            return True

    def add_register_users(self, user_list):
        """
        Метод для добавления пользователей из списка в таблицу RegisteredUsers.
        :param {str} user_list: список зарегистрированных на сервере пользователей.
        :return:
        """
        # Очищаем таблицу, т.к. список пользователей получаем только с сервера при запуске.
        self.session.query(self.RegisteredUsers).delete()
        for user in user_list:
            reg_user = self.RegisteredUsers(user)
            self.session.add(reg_user)
        self.session.commit()

    def get_register_users(self):
        """
        Метод возвращает список зарегистрированных пользователей.
        :return {list}:
        """
        return [user[0] for user in self.session.query(self.RegisteredUsers.username).all()]


if __name__ == '__main__':
    TEST_DB = ClientDataBase('test_user_1')
    TEST_DB.add_contact('Ivan')
    TEST_DB.add_contact('Anton')
    TEST_DB.add_contact('Anton')
    TEST_DB.add_contact('Ignat')
    TEST_DB.delete_contact('Ignat')
    TEST_DB.delete_contact('Ignat')
    print(TEST_DB.get_all_contacts())
    # TEST_DB.save_message('Ivan', 'Anton', 'Привет, Антон!')
    # TEST_DB.save_message('Anton', 'Ivan', 'Привет, Иван.')
    # TEST_DB.save_message('Ivan', 'Anton', 'Чем занят?')
    for msg in TEST_DB.get_message_history(chat='Petr'):
        print(msg)
    print(TEST_DB.get_register_users())
