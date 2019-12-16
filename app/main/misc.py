from flask import Flask, current_app
import uuid


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
