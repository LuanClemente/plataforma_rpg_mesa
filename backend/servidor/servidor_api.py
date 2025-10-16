# servidor/servidor_api.py

# --- IMPORTS PRINCIPAIS ---
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, join_room
from flask_cors import CORS  # Mantido, conforme sua solução funcional.
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import json

# --- IMPORTS DE MÓDULOS INTERNOS ---
# Importações do nosso projeto, agora em um bloco único e organizado.
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
    listar_salas_disponiveis,
    verificar_senha_da_sala,
    salvar_mensagem_chat,
    buscar_historico_chat,
    buscar_dados_essenciais_ficha
)
from core.rolador_de_dados import rolar_dados

# --- CONFIGURAÇÃO DO SERVIDOR ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345'

# --- CONFIGURAÇÃO DE CORS (SUA SOLUÇÃO FUNCIONAL) ---
# Gerencia o CORS para as rotas REST tradicionais (@app.route).
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# O SocketIO gerencia o CORS para as conexões WebSocket.
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# --- DECORATOR DE AUTENTICAÇÃO JWT ---
def token_required(f):
    """Verifica se o token JWT é válido antes de permitir acesso à rota."""
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

# --- ROTAS REST DA API (ORGANIZADAS POR FUNCIONALIDADE) ---

# --- Rotas Públicas ---
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

# --- Rotas de Autenticação ---
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
        token_payload = {'sub': str(user_id), 'name': dados['username'], 'iat': datetime.now(timezone.utc), 'exp': datetime.now(timezone.utc) + timedelta(hours=24)}
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token})
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Rotas de Fichas (Protegidas) ---
@app.route("/api/fichas", methods=['GET'])
@token_required
def get_fichas_usuario(current_user_id):
    fichas = buscar_fichas_por_usuario(current_user_id)
    return jsonify(fichas)

@app.route("/api/fichas", methods=['POST'])
@token_required
def post_nova_ficha(current_user_id):
    dados = request.get_json()
    campos_obrigatorios = ['nome_personagem', 'classe', 'raca', 'antecedente', 'atributos', 'pericias']
    if not all(k in dados for k in campos_obrigatorios):
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400
    sucesso = criar_nova_ficha(current_user_id, dados['nome_personagem'], dados['classe'], dados['raca'], dados['antecedente'], dados['atributos'], dados['pericias'])
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500

# --- ROTAS DE EDIÇÃO QUE ESTAVAM FALTANDO ---
@app.route("/api/fichas/<int:id>", methods=['GET'])
@token_required
def get_ficha_unica(current_user_id, id):
    """Busca e retorna os detalhes de uma única ficha para a página de edição."""
    ficha = buscar_ficha_por_id(id, current_user_id)
    if ficha:
        # Converte as strings JSON do banco de dados de volta para objetos Python.
        if ficha.get('atributos_json'):
            ficha['atributos'] = json.loads(ficha['atributos_json'])
        if ficha.get('pericias_json'):
            ficha['pericias'] = json.loads(ficha['pericias_json'])
        return jsonify(ficha)
    else:
        return jsonify({'mensagem': 'Ficha não encontrada ou permissão negada.'}), 404

@app.route("/api/fichas/<int:id>", methods=['PUT'])
@token_required
def update_ficha(current_user_id, id):
    """Atualiza os dados de uma ficha existente."""
    dados = request.get_json()
    sucesso = atualizar_ficha(id, current_user_id, dados)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha atualizada com sucesso!'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao atualizar ficha ou permissão negada.'}), 404
        
@app.route("/api/fichas/<int:id>", methods=['DELETE'])
@token_required
def delete_ficha(current_user_id, id):
    sucesso = apagar_ficha(id, current_user_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha apagada com sucesso!'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Ficha não encontrada ou permissão negada.'}), 404

# --- Rotas de Salas (Protegidas) ---
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
    sucesso = criar_nova_sala(dados['nome'], dados.get('senha'), current_user_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Sala criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Nome de sala já existe ou erro ao criar.'}), 409

@app.route("/api/salas/verificar-senha", methods=['POST'])
@token_required
def rota_verificar_senha_sala(current_user_id):
    dados = request.get_json()
    if not dados or 'sala_id' not in dados or 'senha' not in dados:
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos.'}), 400
    senha_valida = verificar_senha_da_sala(dados['sala_id'], dados['senha'])
    return jsonify({'sucesso': senha_valida, 'mensagem': 'Senha da sala incorreta.' if not senha_valida else ''})

# --- EVENTOS SOCKET.IO ---
@socketio.on('connect')
def handle_connect():
    print(f"Cliente conectado! SID: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Cliente desconectado! SID: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    token = data.get('token'); sala_id = data.get('sala_id'); ficha_id = data.get('ficha_id')
    if not all([token, sala_id, ficha_id]):
        send({'error': 'Dados para entrar na sala incompletos.'}); return
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        ficha_data = buscar_dados_essenciais_ficha(ficha_id, user_id)
        if not ficha_data:
            send({'error': 'Ficha não encontrada ou não pertence a você.'}); return
        nome_personagem = ficha_data['nome_personagem']
        join_room(sala_id)
        historico = buscar_historico_chat(sala_id)
        socketio.emit('chat_history', {'historico': historico}, room=request.sid)
        mensagem_entrada = f"--- {nome_personagem} entrou na taverna! ---"
        send(mensagem_entrada, to=sala_id)
        salvar_mensagem_chat(sala_id, 'Sistema', f"{nome_personagem} entrou na taverna!")
        print(f"{nome_personagem} (User ID: {user_id}) entrou na sala {sala_id}")
    except Exception as e:
        print(f"Falha na autenticação: {e}"); send({'error': 'Autenticação falhou.'})

@socketio.on('send_message')
def handle_send_message(data):
    token = data.get('token'); sala_id = data.get('sala_id'); message_text = data.get('message'); ficha_id = data.get('ficha_id')
    if not all([token, sala_id, message_text, ficha_id]):
        send({'error': 'Dados da mensagem incompletos.'}); return
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        ficha_data = buscar_dados_essenciais_ficha(ficha_id, user_id)
        if not ficha_data: return
        nome_personagem = ficha_data['nome_personagem']
        salvar_mensagem_chat(sala_id, nome_personagem, message_text)
        formatted_message = f"[{nome_personagem}]: {message_text}"
        send(formatted_message, to=sala_id)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}"); send({'error': 'Token inválido.'})

@socketio.on('roll_dice')
def handle_roll_dice(data):
    token = data.get('token'); sala_id = data.get('sala_id'); dice_command = data.get('command'); ficha_id = data.get('ficha_id')
    if not all([token, sala_id, dice_command, ficha_id]):
        send({'error': 'Dados da rolagem incompletos.'}); return
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        ficha_data = buscar_dados_essenciais_ficha(ficha_id, user_id)
        if not ficha_data: return
        nome_personagem = ficha_data['nome_personagem']
        total, rolagens = rolar_dados(dice_command)
        resultado_str = f"{total} ({', '.join(map(str, rolagens))})" if len(rolagens) > 1 else str(total)
        mensagem = f"🎲 [{nome_personagem}] rolou {dice_command} e tirou: {resultado_str}"
        salvar_mensagem_chat(sala_id, 'Sistema', f"[{nome_personagem}] rolou {dice_command} e tirou: {resultado_str}")
        send(mensagem, to=sala_id)
    except Exception as e:
        print(f"Erro ao rolar dados: {e}"); send({'error': 'Token inválido.'})

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)