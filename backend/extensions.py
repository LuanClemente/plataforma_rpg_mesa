from flask_socketio import SocketIO

# Initialize SocketIO here to avoid circular imports
socketio = SocketIO(cors_allowed_origins="*")
