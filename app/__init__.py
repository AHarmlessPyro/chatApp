from flask import Flask, session
from flask_socketio import SocketIO
from flask_session import Session
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

socketio = SocketIO()
login = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
session = Session()

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_TYPE = 'redis'


def create_app(debug=False):
    """Create an application."""
    # app = Flask(__name__)
    app = Flask(__name__, static_url_path="/static", static_folder="static")
    app.debug = debug
    app.config['SECRET_KEY'] = 'thisIsASecretKey#1209'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    #app.config['SESSION_TYPE'] = 'sqlalchemy'
    #app.config['SESSION_SQLALCHEMY_TABLE'] = 'sessions'
    #app.config['SESSION_SQLALCHEMY'] = db

    # register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # end blueprint

    # init socket io app
    socketio.init_app(app, manage_session=False)
    # end socket io app init

    # start flask-session
    session.init_app(app)
    # end flask session

    # start flask-login init
    login.init_app(app)
    login.login_view = 'main.loginFunc'
    # end flask login

    # start flask-sqlalchemy
    db.init_app(app)
    # end flask-sqlalchemy

    # start flask-migrate
    migrate.init_app(app, db)
    # end flask-migrate

    # import models from model.py
    from app import model
    # done with import

    # session.app.session_interface.db.create_all()

    # pass back app
    return app
