from flask import session, redirect, url_for, render_template, request, session, jsonify, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from flask_session import sessions
from . import main
from .. import login
from .forms import LoginForm, RegistrationForm
from ..model import UserModel
from app.model import UserModel
from app import db


@main.route('/')
def base():
    return "Hello World!"


@main.route('/room/<roomNumber>')
def joinRoom(roomNumber):
    pass


@main.route('/index')
@login_required
def index():
    print(current_user)
    print(current_user.username)
    print(current_user.id)
    return render_template('mainChat.html')


@main.route('/login', methods=['GET', 'POST'])
def loginFunc():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = UserModel.query.filter_by(username=form.username.data).first()
        print(f'Current User is {user}')
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for('main.loginFunc'))
        login_user(user, remember=form.remember_me.data)

        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
##---------------------SESSION MANAGEMENT---------------------##


@main.route('/session', methods=['GET', 'POST'])
def session_access():
    if request.method == 'GET':
        val = jsonify({
            'session': session.get('value', ''),
            'user': current_user.id,
            'userName': UserModel.query.filter_by(id=current_user.id).first().username
            if current_user.is_authenticated else 'anonymous'
        })
        print(f'Session value is {val}')
        return val
    data = request.get_json()
    print(data)
    if 'session' in data:
        session['value'] = data['session']
    elif 'user' in data:
        if data['user']:
            login_user(UserModel(data['user']))
        else:
            logout_user()
    return '', 204


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = UserModel(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        print(f'Current user id is {user.id}')
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.loginFunc'))
    return render_template('register.html', title='Register', form=form)


@login_required
@main.route('/user/<name>')
def getUser(name):
    print(f'Query made for user ${name}')
    userDat = UserModel.query.filter_by(username=name).first()
    return render_template('UserPage.html', messages=userDat.messages) #, imgLoc="C:\Users\Ninad Sinha\Google Drive\study stuff\CSCI\CSCI 4131\CSCI-4131\chatApp\static\images"


'''@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('index.html', form=form)


@main.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', name=name, room=room)'''
