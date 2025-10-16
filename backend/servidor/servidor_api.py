# servidor/servidor_api.py

# --- Importações ---
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db_manager import verificar_senha_da_sala
# Importa as ferramentas do Flask-SocketIO para comunicação em tempo real.
from flask_socketio import SocketIO, send, join_room, leave_room
# Do nosso gerenciador de banco de dados, importamos TODAS as funções que a API irá utilizar.
from database.db_manager import (
    buscar_todos_os_itens, 
    buscar_todos_os_monstros,
    registrar_novo_usuario,
    verificar_login,
    criar_nova_ficha,
    buscar_fichas_por_usuario,
    apagar_ficha,
    buscar_ficha_por_id,
    atualizar_ficha,
    criar_nova_sala,
    listar_salas_disponiveis
)
import jwt
from datetime import datetime, timedelta, timezone
import json

# --- Configuração Inicial do Servidor ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345'
CORS(app, origins=["http://localhost:5173"])

# --- CONFIGURAÇÃO CORRETA E FINAL DO CORS ---
# Dizemos explicitamente ao SocketIO para usar o motor 'eventlet' (que precisa estar instalado via pip).
# Isso garante que ele assuma o controle de TODAS as requisições (HTTP e WebSocket) corretamente.
# A configuração 'cors_allowed_origins' é gerenciada aqui para toda a aplicação.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# --- Decorator de Autenticação (O "Segurança") ---
def token_required(f):
    """Decorator que verifica o token JWT antes de executar uma rota protegida."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'mensagem': 'Token (crachá) ausente!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = int(data['sub'])
        except Exception as e:
            print(f"Erro ao decodificar token: {e}")
            return jsonify({'mensagem': 'Token (crachá) inválido ou expirado!'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# --- Endpoints da API REST (Nenhuma alteração na lógica interna das rotas) ---
@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    monstros_db = buscar_todos_os_monstros()
    lista_de_monstros = [{'id': m[0], 'nome': m[1], 'vida': m[2], 'ataque_bonus': m[3], 'dano_dado': m[4], 'defesa': m[5], 'xp': m[6], 'ouro': m[7]} for m in monstros_db]
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    itens_db = buscar_todos_os_itens()
    lista_de_itens = [{'id': i[0], 'nome': i[1], 'tipo': i[2], 'descricao': i[3], 'preco': i[4], 'dano': i[5], 'bonus_ataque': i[6], 'efeito': i[7]} for i in itens_db]
    return jsonify(lista_de_itens)

@app.route("/api/registrar", methods=['POST'])
def rota_registrar_usuario():
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados incompletos."}), 400
    sucesso = registrar_novo_usuario(dados['username'], dados['password'])
    if sucesso:
        return jsonify({"sucesso": True, "mensagem": "Usuário registrado com sucesso!"}), 201
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário já está em uso."}), 409

@app.route("/api/login", methods=['POST'])
def rota_fazer_login():
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados ausentes."}), 400
    user_id = verificar_login(dados['username'], dados['password'])
    if user_id:
        token_payload = {
            'sub': str(user_id), 'name': dados['username'],
            'iat': datetime.now(timezone.utc), 'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token})
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

@app.route("/api/fichas", methods=['GET'])
@token_required 
def get_fichas_usuario(current_user_id):
    fichas = buscar_fichas_por_usuario(current_user_id)
    return jsonify(fichas)

@app.route("/api/fichas", methods=['POST'])
@token_required
def post_nova_ficha(current_user_id):
    dados = request.get_json()
    if not all(k in dados for k in ['nome_personagem', 'classe', 'raca', 'antecedente', 'atributos', 'pericias']):
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400
    sucesso = criar_nova_ficha(current_user_id, dados['nome_personagem'], dados['classe'], dados['raca'], dados['antecedente'], dados['atributos'], dados['pericias'])
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500

@app.route("/api/fichas/<int:id>", methods=['DELETE'])
@token_required
def delete_ficha(current_user_id, id):
    sucesso = apagar_ficha(id, current_user_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha apagada com sucesso!'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Ficha não encontrada ou permissão negada.'}), 404
        
@app.route("/api/salas", methods=['GET'])
@token_required
def get_salas(current_user_id):
    salas = listar_salas_disponiveis()
    return jsonify(salas)

@app.route("/api/salas", methods=['POST'])
@token_required
def post_nova_sala(current_user_id):
    dados = request.get_json()
    if not dados or 'nome' not in dados:
        return jsonify({'mensagem': 'Nome da sala é obrigatório.'}), 400
    senha = dados.get('senha', None)
    nome_sala = dados['nome']
    sucesso = criar_nova_sala(nome_sala, senha, current_user_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Sala criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Nome de sala já existe ou erro ao criar.'}), 409

# --- NOVO ENDPOINT PARA VERIFICAÇÃO DE SENHA DA SALA ---
@app.route("/api/salas/verificar-senha", methods=['POST'])
@token_required # Protegido, pois só usuários logados podem tentar entrar.
def rota_verificar_senha_sala(current_user_id):
    """Verifica se a senha fornecida para uma sala é válida."""
    dados = request.get_json()
    if not dados or 'sala_id' not in dados or 'senha' not in dados:
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos.'}), 400

    sala_id = dados['sala_id']
    senha = dados['senha']

    # Chama a função do db_manager para fazer a verificação segura.
    senha_valida = verificar_senha_da_sala(sala_id, senha)

    if senha_valida:
        # Se a senha for válida, responde com sucesso.
        return jsonify({'sucesso': True})
    else:
        # Se for inválida, responde com erro de não autorizado.
        return jsonify({'sucesso': False, 'mensagem': 'Senha da sala incorreta.'}), 401
# --- Gerenciadores de Eventos WebSocket ---
@socketio.on('connect')
def handle_connect():
    print(f"Cliente conectado com WebSocket! ID da sessão: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Cliente desconectado do WebSocket! ID da sessão: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    token = data.get('token')
    sala_id = data.get('sala_id')

    if not token or not sala_id:
        send({'error': 'Token ou ID da sala ausente.'})
        return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = user_data['name']
        join_room(sala_id)
        send(f"--- {username} entrou na taverna! ---", to=sala_id)
        print(f"Usuário '{username}' (ID: {user_data['sub']}) entrou na sala {sala_id}")
    except Exception as e:
        print(f"Falha na autenticação para entrar na sala: {e}")
        send({'error': 'Autenticação falhou.'})

# --- Bloco para Iniciar o Servidor ---
if __name__ == "__main__":
    # Usamos 'socketio.run()' para iniciar o servidor com o motor correto (eventlet).
    socketio.run(app, debug=True, port=5001)