from flask import session, redirect, url_for, render_template, request, session, jsonify, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required
from flask_session import sessions
from . import main
from .. import login
from .forms import LoginForm, RegistrationForm
from app.model import UserModel
from app import db


@main.route('/room/<roomNumber>')
def joinRoom(roomNumber):
    pass


@main.route('/index')
@login_required
def index():
    session['isPrivate'] = False
    return render_template('mainChat.html')


@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def loginFunc():
    session['isPrivate'] = False
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


@main.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect(url_for('main.loginFunc'))
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
    userDat = UserModel.query.filter_by(username=name).first()
    if userDat == None:
        return render_template('errorPage.html', type_of_error="404 Not Found", message=f'{name} was not found')
    return render_template('UserPage.html', messages=userDat.messages.all(), user=userDat)


@login_required
@main.route('/private')
def createRoom():
    return render_template('join_room.html')


@login_required
@main.route('/private/<room>')
def getRooms(room):
    session['isPrivate'] = True
    return render_template('privateChat.html', room=room)
