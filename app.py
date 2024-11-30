import os
from flask import Flask, render_template, session, request  # Import `request`
from flask_socketio import SocketIO, send, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Store connected users
users = {}

def generate_username():
    """Generate a random username for an anonymous user."""
    return 'User-' + ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    """Assign a random username to the connecting user."""
    username = generate_username()
    users[request.sid] = username  # Using `request.sid` here
    emit('welcome', {'username': username}, to=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Remove user from the list when they disconnect."""
    if request.sid in users:
        username = users.pop(request.sid, None)
        emit('message', f'{username} has left the chat.', broadcast=True)

@socketio.on('message')
def handle_message(data):
    """Broadcast messages with usernames."""
    username = users.get(request.sid, 'Anonymous')
    send(f"{username}: {data}", broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

