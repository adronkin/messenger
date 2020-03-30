"""Server Database Description Module."""

import os
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, \
    create_engine, Index, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create a base class for declarative work.
BASE = declarative_base()


class ServerDataBase:
    """
    A class describing database tables and server methods.
    """
    class Users(BASE):
        """
        The class describes the table of all users.\n
        Stores data: id, username, last_login, password, public_key.
        """
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True, nullable=False)
        last_login = Column(DateTime)
        password = Column(String)
        public_key = Column(Text, nullable=True)
        __table_args__ = (Index('users_index', 'id'), )

        def __init__(self, username, password):
            self.username = username
            self.last_login = datetime.now()
            self.password = password

    class ActiveUser(BASE):
        """
        The class describes the table of active users.\n
        Stores data: id, user_id, ip_address, port, login_time.
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
        The class describes a table of user connection history.\n
        Stores data: id, user_id, ip_address, port, login_time, logout_time.
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
        The class describes the user contact table.\n
        Stores data: id, user_id, friend_id.
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
        The class describes a table with the user's correspondence history.\n
        Stores data: id, sender, recipient, date, message.
        """
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        sender = Column(String)
        recipient = Column(String)
        date = Column(DateTime)
        message = Column(Text)
        __table_args__ = (
            Index('message_history_index', 'id', 'sender', 'recipient'),
        )

        def __init__(self, sender, recipient, message):
            self.sender = sender
            self.recipient = recipient
            self.date = datetime.now()
            self.message = message

    def __init__(self, path):
        # Create a database (echo - logging through the standard logging module).
        # connect_args={'check_same_thread': False} -
        # created in a stream can be used not only in this stream.
        self.engine = create_engine(
            f'sqlite:///{path}',
            echo=False,
            pool_recycle=3600,
            connect_args={'check_same_thread': False}
        )

        # Create tables.
        BASE.metadata.create_all(self.engine)

        # Create session.
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        # After the connection is established, clear the table of active users.
        self.session.query(self.ActiveUser).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port, key):
        """
        The method is launched when the user logs in.
        Writes entry information to the database.\n
        :param str username: username.
        :param str ip_address: User IP.
        :param int port: user port.
        :param str key: public key of the user.
        """
        # Search in the Users table for a user named username.
        q_user = self.session.query(self.Users).filter_by(username=username)

        # If the user is in the table.
        if q_user.count():
            # Return the result of the request and update the date of the last login.
            client = q_user.first()
            client.last_login = datetime.now()
            if client.public_key != key:
                client.public_key = key
        # Otherwise, add a new user.
        else:
            raise ValueError(f'Пользователь {username} не зарегистрирован.')

        # Updating data in the ActiveUser and UserStory tables.
        active_user = self.ActiveUser(
            client.id,
            ip_address,
            port,
            datetime.now()
        )
        self.session.add(active_user)
        user_history = self.UserStory(
            client.id,
            ip_address,
            port,
            datetime.now(),
            None
        )
        self.session.add(user_history)
        self.session.commit()

    def register_user(self, username, password):
        """
        Method for user registration. Writes to the Users table.\n
        :param str username: username.
        :param byte password: user password hash.
        """
        new_user = self.Users(username, password)
        self.session.add(new_user)
        self.session.commit()

    def del_user(self, username):
        """
        Method for deleting a user from the database.\n
        :param str username: username.
        """
        q_user = self.session.query(self.Users).filter_by(username=username)
        if q_user.count():
            client = q_user.first()
            self.session.query(self.ContactList).filter_by(user_id=client.id).delete()
            self.session.query(self.ContactList).filter_by(friend_id=client.id).delete()
            self.session.query(self.UserStory).filter_by(user_id=client.id).delete()
            self.session.query(self.ActiveUser).filter_by(user_id=client.id).delete()
            self.session.query(self.Users).filter_by(username=username).delete()
            self.session.commit()

    def get_pass_hash(self, username):
        """
        The method returns the hash of the user's password.\n
        :param str username: username.
        :return: user password hash.
        """
        client = self.session.query(self.Users).filter_by(username=username).first()
        return client.password

    def get_key(self, username):
        """
        The method returns the public key of the user.\n
        :param str username: username.
        :return: public key.
        """
        client = self.session.query(self.Users).filter_by(username=username).first()
        return client.public_key

    def user_logout(self, username):
        """
        The method is launched when the user exits. Removes the user from the
        ActiveUser table and enters the exit time into the UserStory table.\n
        :param str username: username.
        """
        client = self.session.query(self.Users).filter_by(username=username).first()
        self.session.query(self.ActiveUser).filter_by(user_id=client.id).delete()
        # Add logout_time to the UserStory table.
        history_logout = self.session.query(self.UserStory).filter_by(user_id=client.id).all()[-1]
        history_logout.logout_time = datetime.now()
        self.session.commit()

    def get_all_users(self):
        """
        The method returns a list of all users and the time of the last login.\n
        :return: list of all users.
        """
        query = self.session.query(
            self.Users.username,
            self.Users.last_login,
        )
        return query.all()

    def get_all_active_users(self):
        """
        The method returns a list of all active users.\n
        :return: list of all active users.
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
        The method returns the history of visits of one or all users.\n
        :param str username: username.
        :return: list of user visits.
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
        The method returns a contact list of one or all users.\n
        :param str username: username.
        :return: user contact list.
        """
        client = self.session.query(self.Users).filter_by(username=username).one()
        query = self.session.query(
            self.ContactList,
            self.Users.username,
        ).filter_by(user_id=client.id).join(
            self.Users,
            self.ContactList.friend_id == self.Users.id
        )
        return [contact[1] for contact in query.all()]

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

    def get_message_history(self, sender=None, recipient=None):
        """
        The method returns the history of correspondence by recipient
        and/or sender.\n
        :param str sender: message sender.
        :param str recipient: the recipient of the message.
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
        The method adds the user to the contact list.\n
        :param str username: username.
        :param str friend_name: user to add to your contact list.
        """
        q_username = self.session.query(self.Users).filter_by(username=username).first()
        q_friend_name = self.session.query(self.Users).filter_by(username=friend_name).first()

        # Check that the contact exists and the record is not duplicated.
        if not q_friend_name or self.session.query(self.ContactList).filter_by(
                user_id=q_username.id,
                friend_id=q_friend_name.id
        ).count():
            return

        new_contact = self.ContactList(q_username.id, q_friend_name.id)
        self.session.add(new_contact)
        self.session.commit()

    def del_contact(self, username, friend_name):
        """
        The method removes the user from the contact list.\n
        :param str username: username.
        :param str friend_name: user to remove from contact list.
        """
        q_username = self.session.query(self.Users).filter_by(username=username).first()
        q_friend_name = self.session.query(self.Users).filter_by(username=friend_name).first()

        # Check that the contact exists.
        if not q_friend_name:
            return

        self.session.query(self.ContactList).filter_by(
            user_id=q_username.id,
            friend_id=q_friend_name.id
        ).delete()
        self.session.commit()

    def check_contact(self, username, friend_name):
        """
        The method returns True if the username is in the contact list.\n
        :param str username: username
        :param str friend_name: user to check in the contact list.
        :return: bool.
        """
        q_username = self.session.query(self.Users).filter_by(username=username).first()
        q_friend_name = self.session.query(self.Users).filter_by(username=friend_name).first()
        if q_username and q_friend_name:
            q_contact = self.session.query(self.ContactList).filter_by(
                user_id=q_username.id,
                friend_id=q_friend_name.id
            )
            if q_contact.count():
                return True

    def check_user(self, username):
        """
        The method returns True if the username is in the Users table.\n
        :param str username: username.
        :return: bool.
        """
        q_username = self.session.query(self.Users).filter_by(username=username)
        if q_username.count():
            return True


if __name__ == '__main__':
    TEST_DB = ServerDataBase(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          'server_database.db3'))
    # TEST_DB.user_login('test', '192.168.0.1', 7777)
    # for user in TEST_DB.get_all_active_users():
    #     print(f'Пользователь: {user[0]} ({user[1]}:{user[2]}).'
    #           f' Последний вход: {user[3]}.')
    # TEST_DB.user_logout('test_user_1')
    # TEST_DB.user_login('test_user_2', '127.0.0.1', 8888)
    # TEST_DB.user_logout('test_user_2')
    # for user in TEST_DB.get_all_users():
    #     print(f'Пользователь: {user.username}. Последний вход: {user.last_login}.')
    for user in TEST_DB.get_connect_history('test'):
        print(f'Пользователь: {user[0]} ({user[1]}:{user[2]}).'
              f' Login: {user[3]}. Logout: {user[4]}.')
    # print(f'Список контактов пользователя: {TEST_DB.get_contact_list("test_user_2")}')
    # TEST_DB.save_message('Ivan', 'Anton', 'Привет, Антон!')
    # TEST_DB.save_message('Anton', 'Ivan', 'Привет, Иван.')
    # TEST_DB.save_message('Ivan', 'Anton', 'Чем занят?')
    # for msg in TEST_DB.get_message_history(sender='Anton'):
    #     print(msg)
    # TEST_DB.add_contact('Petr', 'Peter')
    # TEST_DB.del_contact('Petr', 'Peter')
    # TEST_DB.del_user('Vasya')
    # print(TEST_DB.check_contact('test_user_1', 'Petr'))
