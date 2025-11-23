from flask import request
from flask_socketio import emit, join_room, leave_room
from app import socketio

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('status', {'msg': 'Connected to RPG Platform'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('join_room')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    print(f"{username} joined room {room}")
    emit('message', {'user': 'System', 'text': f'{username} has entered the room.'}, to=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    print(f"Message in {room}: {data['message']}")
    emit('message', data, to=room)
