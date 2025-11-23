from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!' # TODO: Change this in production

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Import routes and events (to be created)
# Import events to register handlers
import events

@app.route('/')
def index():
    return "RPG Platform Backend is Running!"

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
