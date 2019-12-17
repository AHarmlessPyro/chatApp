from flask import session, jsonify
from flask_socketio import emit, join_room, leave_room, emit, rooms
from flask_login import current_user, login_user, \
    logout_user
from flask_session import Session
from urllib import parse
from .. import socketio

import requests
import re
import ssl

from .misc import add_clients, get_clients, add_clients, remove_clients, add_rooms
from ..model import UserModel, MessageModel  # ,PrivateRooms
from .extras import authenticated_only

from app import db

CurrentRooms = []


@socketio.on('connect')
@authenticated_only
def connected():
    print(session['isPrivate'])
    print("%s connected")
    add_clients()
    cl = get_clients()
    print("Currently connected clients are " + str(rooms()))
    emit('Log', 'Connected client count ' + str(cl), broadcast=True)
    emit('setClientID', {'ID': str(cl)})
    messages = MessageModel.query.order_by(
        MessageModel.id.desc()).limit(10).all()
    messages = reversed(messages)
    # socketio.sleep(1)
    if not session['isPrivate']:
        for message in messages:
            val = {
                'message': message.body,
                'sender': message.author.username,
                'id': message.user_id
            }
            print(f'Sending message {val}')
            sendMessageSpecific(val)
    print(f'Current client is {current_user}')
    # emit('newMessage', {'message': f'Connected client count {str(cl)}', 'sender': 'System'}, broadcast=True)


@socketio.on('user-reconnected')
@authenticated_only
def reconnect():
    print("Fired reconnect event")
    add_clients()
    cl = get_clients()
    emit('Log', 'Connected client count ' + str(cl), broadcast=True)
    emit('setClientID', {'ID': str(cl)})
    print(f'Current client is {current_user}')
    # emit('newMessage', {'message': f'Connected client count {str(cl)}', 'sender': 'System'}, broadcast=True)


@socketio.on('gif')
def getGif(data):
    searchQuery = data['Query']
    offset = data['previousEndAt']
    count = data['countNext']
    data = requests.get(
        f'https://api.giphy.com/v1/gifs/search?api_key=7XqA72FYKKppzqE77yt1YBSI3xZ9Fpy7&q={searchQuery}&limit={count}&offset={offset}&rating=G&lang=en')
    item = (data.json())
    returnVal = []
    for element in item['data']:
        returnVal.append(element['images'])
    emit('returnGif', returnVal)


@socketio.on('disconnect')
def disconnect():
    print("A client disconnected")
    remove_clients()
    cl = get_clients()
    emit('disconnected', ' A client disconnected with remaining count ' +
         str(cl), broadcast=True)


@socketio.on('message')
def message(data):
    emit('broadcast', "Broadcasting " + message + "to everyone")


@socketio.on('messagePublic')
def sendMessagePublic(data):
    if data['sender'] == 'System':
        emit('newMessage', data, broadcast=True)
        return
    print(data)

    # number based URI : (?:[a-z]*://)?[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*(?:\:[0-9]*)?(?:/[\S]*)*
    # text based URI : (?:[a-z]*://)?(?:[\S]*\.)+[com|ru|org|net|info|biz]*(?:\:[0-9]*)?(?:/[\S]*)*

    textURI = r'(?:[a-z]*://)?(?:[\S]*\.)+[com|ru|org|net|info|biz]*(?:\:[0-9]*)?(?:/[\S]*)*'
    numberURI = r'(?:[a-z]*://)?[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*(?:\:[0-9]*)?(?:/[\S]*)*'

    if not (data['id'] == -1):
        message = MessageModel(body=data['message'], user_id=data['id'])
        db.session.add(message)
        db.session.commit()

        print(UserModel.query.filter_by(id=data['id']).first().messages)

    if not (re.match(textURI, data['message']) or re.match(numberURI, data['message'])):
        emit('newMessage', data, broadcast=True)
        return

    def attemptURL(URL, haveAttempted=False) -> bool:
        try:
            print(f'Attempting the URL {URL}')
            requestedItem = requests.head(URL)
            print(requestedItem)
            if re.findall('image', requestedItem.headers['Content-Type']):
                print("Found image")
                data['actualURL'] = URL
                emit('newImage', data, broadcast=True)
                return True
            elif re.findall('text', requestedItem.headers['Content-Type']):
                print("Found URL")
                data['actualURL'] = URL
                emit('newURL', data, broadcast=True)
                return True
            return False
        except Exception:
            return False
    if not attemptURL(data['message']):
        if not attemptURL(f'https://{data["message"]}'):
            if not attemptURL(f'http://{data["message"]}'):
                emit('newMessage', data, broadcast=True)
            else:
                print('Returned true on http')
        else:
            print('Returned true on https')
    else:
        print('Returned true on no additions')


@socketio.on('getPrevious')
def getPreviousMessages(data):
    messages = MessageModel.query.order_by(
        MessageModel.id.desc()).offset(data['count']).limit(10).all()
    #messages = reversed(messages)
    for message in messages:
        val = {
            'message': message.body,
            'sender': message.author.username,
            'id': message.user_id,
            'placement': 'before'
        }
        print(f'Sending message {val}')
        sendMessageSpecific(val)

##---------------------SESSION MANAGEMENT---------------------##


@socketio.on('get-session')
def get_session():
    emit('refresh-session', {
        'session': session.get('value', ''),
        'user': current_user.id
        if current_user.is_authenticated else 'anonymous'
    })


@socketio.on('set-session')
def set_session(data):
    if 'session' in data:
        session['value'] = data['session']
    elif 'user' in data:
        if data['user'] is not None:
            login_user(UserModel(data['user']))
        else:
            logout_user()

##---------------------MISC RELATED FUNCTIONS---------------------##


def sendMessageSpecific(data):

    textURI = r'(?:[a-z]*://)?(?:[\S]*\.)+[com|ru|org|net|info|biz]*(?:\:[0-9]*)?(?:/[\S]*)*'
    numberURI = r'(?:[a-z]*://)?[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*(?:\:[0-9]*)?(?:/[\S]*)*'

    if not (re.match(textURI, data['message']) or re.match(numberURI, data['message'])):
        emit('newMessage', data, broadcast=True)
        return

    def attemptURL(URL, haveAttempted=False) -> bool:
        try:
            requestedItem = requests.head(URL)
            if re.findall('image', requestedItem.headers['Content-Type']):
                data['actualURL'] = URL
                emit('newImage', data)
                return True
            elif re.findall('text', requestedItem.headers['Content-Type']):
                data['actualURL'] = URL
                emit('newURL', data)
                return True
            return False
        except Exception:
            return False
    if not attemptURL(data['message']):
        if not attemptURL(f'https://{data["message"]}'):
            if not attemptURL(f'http://{data["message"]}'):
                emit('newMessage', data)

##---------------------JOIN ROOM---------------------##


@authenticated_only
@socketio.on('create_room')
def create_room_New(data):
    print(data)
    room = data['room']
    for checkRoom in CurrentRooms:
        if checkRoom['room'] == room:
            emit("not_available")
            return
    usernames = [data['username'],
                 UserModel.query.filter_by(id=current_user.id).first().username]

    print(f'attempting to join room {room} accessible to {usernames}')

    CurrentRooms.append({'room': room, 'usernames': usernames, 'messages': []})
    emit('join_room')
    return


@authenticated_only
@socketio.on('join_room')
def join_room_New(data):
    room = data['room']
    print(f'attempting to join room {room}')
    for checkRoom in CurrentRooms:
        if checkRoom['room'] == room:
            emit("join_room")
            return
    emit('not_available')
    return
