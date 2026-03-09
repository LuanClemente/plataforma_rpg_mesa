from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import eventlet

# É importante aplicar o monkey_patch antes de importar outras coisas que usam rede
eventlet.monkey_patch()

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!' # TODO: Change this in production

# Inicializa o SocketIO. O CORS para websockets é tratado aqui.
socketio = SocketIO(app, cors_allowed_origins="http://localhost:5173", async_mode='eventlet')

# Inicializa o Flask-CORS para as rotas HTTP (API).
# É importante fazer isso *depois* do SocketIO para garantir que as requisições HTTP sejam tratadas corretamente.
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

# --- REGISTRAR ROTAS E EVENTOS ---
# Importa e registra as rotas da API (ex: /api/cantigas/dados)
from api_routes import api_bp
app.register_blueprint(api_bp)

# Importa os eventos WebSocket (deve ser após socketio ser definido)
import events  # noqa: F401, E402


@app.route('/')
def index():
    return "RPG Platform Backend is Running!"

if __name__ == '__main__':
    print("Iniciando o servidor Flask com SocketIO via Eventlet na porta 5003...")
    socketio.run(app, host='0.0.0.0', port=5003, debug=True)