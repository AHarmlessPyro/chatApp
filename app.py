from flask import Flask
from flask import request
from flask import render_template
from flask import g
from flask import current_app
from flask_socketio import SocketIO, join_room, leave_room, emit
import re
import os
import requests
import uuid
from extras import FixedArray

app = Flask(__name__, template_folder="template")
app.secret_key = "thisIsASecretKey"
socketio = SocketIO(app)
ROOMS = {}
CLIENTS = 0

@app.route('/')
def base():
    return "Hello World!"


@socketio.on('connect')
def connected():
    print("%s connected")
    add_clients()
    cl = get_clients()
    emit('connected', 'Connected client count ' + str(cl), broadcast=True)


@socketio.on('disconnect')
def disconnect():
    print("A client disconnected")
    remove_clients()
    cl = get_clients()
    emit('disconnected', ' A client disconnected with remaining count ' +
         str(cl), broadcast=True)


@app.route('/index')
def index():
    return render_template('mainChat.html')


@socketio.on('create')
def creation(data):
    emit('hello', {'boo': 'boo'})


@socketio.on('message')
def message(data):
    emit('broadcast', "Broadcasting " + message + "to everyone")


@socketio.on('createRoom')
def createRoom():
    addedRoom = add_rooms()
    print(addedRoom)
    emit('NewRoom', "Added a room " + str(addedRoom))


@socketio.on('messagePublic')
def sendMessagePublic(data):
    print(data)
    emit('newMessage', data, broadcast=True)


def get_rooms():
    rooms = getattr(current_app, '_rooms', None)
    if rooms is None:
        current_app._rooms = {}
    return current_app._rooms


def add_rooms():
    rooms = get_rooms()
    rooms[uuid.uuid4()] = []
    setattr(current_app, "_rooms", rooms)
    return rooms


def remove_rooms(uuidToRemove):
    rooms = get_rooms()
    del rooms[uuidToRemove]
    setattr(current_app, "_rooms", rooms)
    return rooms


def get_clients():
    clients = getattr(current_app, '_clients', None)
    print("clients connected are "+str(clients))
    if clients is None:
        current_app._clients = 0
    return current_app._clients


def add_clients():
    print("adding clients")
    clients = get_clients()
    clients = clients + 1
    setattr(current_app, "_clients", clients)
    return clients


def remove_clients():
    clients = get_clients()
    clients = clients - 1
    setattr(current_app, "_clients", clients)
    return clients


if __name__ == '__main__':
    socketio.run(app, debug=True)
    print("Hello")
    setattr(current_app, "_UUIDList", [])
