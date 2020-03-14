"""Модуль описания базы данных сервера."""

import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем базовый класс для декларативно работы.
BASE = declarative_base()


class ServerDataBase:
    """
    Класс описывающий таблицы БД и методы сервера.
    """
    class Users(BASE):
        """
        Класс описывает таблицу всех пользователей.
        """
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)
        last_login = Column(DateTime)
        __table_args__ = (Index('users_index', 'id'),)

        def __init__(self, username):
            self.username = username
            self.last_login = datetime.now()

    class ActiveUser(BASE):
        """
        Класс описывает таблицу активных пользователей.
        """
        __tablename__ = 'active_user'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'), unique=True)
        ip_address = Column(String)
        port = Column(Integer)
        login_time = Column(DateTime)
        __table_args__ = (Index('active_user_index', 'id', 'user_id'), )

        def __init__(self, user_id, ip_address, port, login_time):
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    class UserStory(BASE):
        """
        Класс описывает таблицу истории подключений пользователей.
        """
        __tablename__ = 'user_story'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        ip_address = Column(String)
        port = Column(Integer)
        login_time = Column(DateTime)
        logout_time = Column(DateTime)
        __table_args__ = (Index('user_story_index', 'id', 'user_id'), )

        def __init__(self, user_id, ip_address, port, login_time, logout_time):
            self.user_id = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.logout_time = logout_time

    class ContactList(BASE):
        """
        Класс описывает таблицу контактов пользователей.
        """
        __tablename__ = 'contact_list'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        friend_id = Column(Integer, ForeignKey('users.id'))
        __table_args__ = (Index('contact_list_index', 'id', 'user_id'), )

        def __init__(self, user_id, friend_id):
            self.user_id = user_id
            self.friend_id = friend_id

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

    def __init__(self, path):
        # Создаем БД (echo - логирование через стандартный модуль logging).
        # connect_args={'check_same_thread': False} - созданное в потоке может
        # использоваться не только в данном потоке.
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=3600,
                                    connect_args={'check_same_thread': False})

        # Создаем таблицы
        BASE.metadata.create_all(self.engine)

        # Создаем сессию
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # После установки соединения очищаем таблицу активных пользователей
        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        """
        Метод запускается при входе пользователя. Записывает в базу информацию о входе.
        :param {str} username: имя пользователя.
        :param {str} ip_address: IP-адрес пользователя.
        :param {int} port: порт пользователя.
        :return:
        """
        # Поиск в таплице Users пользователя с именем username
        q_user = self.session.query(self.Users).filter_by(username=username)
        # Если пользователь есть в таблице
        if q_user.count():
            # Возвращаем результат запроса и обновляем дату последнего входа
            user = q_user.first()
            user.last_login = datetime.now()
        # Иначе, добавляем нового пользователя
        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()

        # Обновляем данные в таблице ActiveUser и UserStory
        active_user = self.ActiveUser(user.id, ip_address, port, datetime.now())
        self.session.add(active_user)
        user_history = self.UserStory(user.id, ip_address, port, datetime.now(), None)
        self.session.add(user_history)
        self.session.commit()

    def user_logout(self, username):
        """
        Метод запускается при выходе пользователя. Удаляет пользователя из таблицы
        ActiveUser и вносит время выхода в таблицу UserStory.
        :param {str} username:
        :return:
        """
        user = self.session.query(self.Users).filter_by(username=username)
        user = user.first()
        # Удаляем пользователя из таблицы ActiveUser.
        self.session.query(self.ActiveUser).filter_by(user_id=user.id).delete()
        # Вносим в таблицу UserStory вреля logout_time.
        history_logout = self.session.query(self.UserStory).filter_by(user_id=user.id).all()[-1]
        history_logout.logout_time = datetime.now()
        self.session.commit()

    def get_all_users(self):
        """
        Метод возвращает список всех пользователей и время последнего входа.
        :return {list}: список всех пользователей.
        """
        query = self.session.query(
            self.Users.username,
            self.Users.last_login,
        )
        return query.all()

    def get_all_active_users(self):
        """
        Метод возвращает список всех активных пользователях.
        :return {list}: список всех активных пользователей.
        """
        query = self.session.query(
            self.Users.username,
            self.ActiveUser.ip_address,
            self.ActiveUser.port,
            self.ActiveUser.login_time,
        ).join(self.Users)
        return query.all()

    def get_connect_history(self, username=None):
        """
        Метод возвращает историю посещений одного или всех пользователей.
        :param {str} username: имя пользователя.
        :return {list}: список посещений пользователей.
        """
        query = self.session.query(
            self.Users.username,
            self.UserStory.ip_address,
            self.UserStory.port,
            self.UserStory.login_time,
            self.UserStory.logout_time,
        ).join(self.Users)
        if username:
            query = query.filter(self.Users.username == username)
        return query.all()

    def get_contact_list(self, username):
        """
        Метод возвращает возвращает список контактов одного или всех пользователей.
        :param {str} username: имя пользователя.
        :return {list}: список контактов пользователей.
        """
        user = self.session.query(self.Users).filter_by(username=username).one()
        query = self.session.query(
            self.ContactList,
            self.Users.username,
        ).filter_by(user_id=user.id).join(self.Users, self.ContactList.friend_id == self.Users.id)
        return [contact[1] for contact in query.all()]

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

    def get_message_history(self, sender=None, recipient=None):
        """
        Метод возвращает историю переписки по получателю и/или отправителю.
        :param {str} sender: отправитель сообщения.
        :param {str} recipient: получатель сообщения.
        :return:
        """
        query = self.session.query(self.MessageHistory)
        if sender:
            query = query.filter_by(sender=sender)
        if recipient:
            query = query.filter_by(recipient=recipient)
        return [(msg.date, msg.sender, msg.recipient, msg.message)
                for msg in query.all()]

    def add_contact(self, username, friend_name):
        """
        Метод добавляет пользователя в список контактов.
        :param {str} username: имя пользователя.
        :param {str} friend_name: пользователь для добавления в список контактов.
        :return:
        """
        q_username = self.session.query(self.Users).filter_by(username=username).first()
        q_friend_name = self.session.query(self.Users).filter_by(username=friend_name).first()

        # Проверяем, что контакт существует и запись не дублируется.
        if not q_friend_name or self.session.query(self.ContactList).\
                filter_by(user_id=q_username.id, friend_id=q_friend_name.id).count():
            return

        new_contact = self.ContactList(q_username.id, q_friend_name.id)
        self.session.add(new_contact)
        self.session.commit()

    def del_contact(self, username, friend_name):
        """
        Метод удаляет пользователя из списока контактов.
        :param {str} username: имя пользователя.
        :param {str} friend_name: пользователь для удаления из списока контактов.
        :return:
        """
        q_username = self.session.query(self.Users).filter_by(username=username).first()
        q_friend_name = self.session.query(self.Users).filter_by(username=friend_name).first()

        # Проверяем, что контакт существует.
        if not q_friend_name:
            return

        self.session.query(self.ContactList).\
            filter_by(user_id=q_username.id, friend_id=q_friend_name.id).delete()
        self.session.commit()

    def check_contact(self, username, friend_name):
        """
        Метод возвращает True, если пользователь username есть в списке контактов.
        :param {str} username: имя пользователя.
        :param {str} friend_name: пользователь для удаления из списока контактов.
        :return {bool}:
        """
        q_username = self.session.query(self.Users).filter_by(username=username).first()
        q_friend_name = self.session.query(self.Users).filter_by(username=friend_name).first()
        if q_username and q_friend_name:
            q_contact = self.session.query(
                self.ContactList).filter_by(user_id=q_username.id, friend_id=q_friend_name.id)
            if q_contact.count():
                return True


if __name__ == '__main__':
    TEST_DB = ServerDataBase(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          'server_database.db3'))
    # TEST_DB.user_login('test_user_1', '192.168.0.1', 7777)
    # for user in TEST_DB.get_all_active_users():
    #     print(f'Пользователь: {user[0]} ({user[1]}:{user[2]}).'
    #           f' Последний вход: {user[3]}.')
    # TEST_DB.user_logout('test_user_1')
    # TEST_DB.user_login('test_user_2', '127.0.0.1', 8888)
    # TEST_DB.user_logout('test_user_2')
    # for user in TEST_DB.get_all_users():
    #     print(f'Пользователь: {user.username}. Последний вход: {user.last_login}.')
    # for user in TEST_DB.get_connect_history('test_user_1'):
    #     print(f'Пользователь: {user.username} ({user.ip_address}:{user.port}).'
    #           f' Login: {user.login_time}. Logout: {user.logout_time}.')
    # print(f'Список контактов пользователя: {TEST_DB.get_contact_list("test_user_2")}')
    # TEST_DB.save_message('Ivan', 'Anton', 'Привет, Антон!')
    # TEST_DB.save_message('Anton', 'Ivan', 'Привет, Иван.')
    # TEST_DB.save_message('Ivan', 'Anton', 'Чем занят?')
    # for msg in TEST_DB.get_message_history(sender='Anton'):
    #     print(msg)
    # TEST_DB.add_contact('Petr', 'Peter')
    # TEST_DB.del_contact('Petr', 'Peter')
    print(TEST_DB.check_contact('test_user_1', 'Petr'))
