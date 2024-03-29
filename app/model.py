from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from app import db
from flask_login import UserMixin, LoginManager
from . import login
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import ARRAY


class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer,  primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    messages = db.relationship(
        'MessageModel', backref='author', lazy='dynamic')
    userImage = db.Column(db.LargeBinary)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, id=None):
        self.id = id

    def __init__(self, id=None, username="", email="", password_hash="", messages=[]):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.messages = messages


class MessageModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))
    # relevant_rooms = db.Column(db.Integer, db.ForeignKey(
    #   'private_rooms.id'), nullable=True)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))


'''
class PrivateRooms(db.Model):
    id = db.Column(db.String, primary_key=True)
    UserNamesAllowed = db.relationship(
        'UserModel', backref="registeredRooms", lazy="dynamic")
    MessagesInRoom = db.relationship(
        'MessageModel', backref="relatedRoom", lazy="dynamic")


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value
'''
