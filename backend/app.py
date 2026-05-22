import os
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
# Em produção, ele vai pegar uma chave segura das variáveis de ambiente. Local, usa o padrão.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret_de_cria_123!')

# Puxa o CORS dinamicamente. Se não achar a variável, libera com '*' pra não quebrar nossos testes
url_front = os.environ.get('https://plataforma-rpg-mesa.onrender.com', '*')

# Se estiver rodando no Render, usa 'eventlet' (que aguenta o tranco). Local, vai de 'threading'
async_mode = 'threading'
# Inicializa o SocketIO com as configurações de produção
socketio = SocketIO(app, cors_allowed_origins=url_front, async_mode=async_mode)

# Inicializa o Flask-CORS para as rotas HTTP (API)
CORS(app, resources={r"/*": {"origins": url_front}})

# --- REGISTRAR ROTAS E EVENTOS ---
from api_routes import api_bp
app.register_blueprint(api_bp)

import events  # noqa: F401, E402

@app.route('/')
def index():
    return "RPG Platform Backend is Running!"

if __name__ == '__main__':
    print("Iniciando o servidor Flask local na porta 5003...")
    socketio.run(app, host='0.0.0.0', port=5003, debug=True, allow_unsafe_werkzeug=True)
