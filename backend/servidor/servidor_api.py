# servidor/servidor_api.py

# --- Importações ---
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from database.db_manager import criar_nova_sala, listar_salas_disponiveis
# Do nosso gerenciador de banco de dados, importamos TODAS as funções que a API irá utilizar em um único bloco.
from database.db_manager import (
    buscar_todos_os_itens, 
    buscar_todos_os_monstros,
    registrar_novo_usuario,
    verificar_login,
    criar_nova_ficha,
    buscar_fichas_por_usuario,
    apagar_ficha,
    buscar_ficha_por_id,
    atualizar_ficha
    
)
import jwt
from datetime import datetime, timedelta, timezone
import json # Importa a biblioteca JSON para decodificar os campos da ficha.

# --- Configuração Inicial do Servidor ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345'
CORS(app)

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

# --- Definição dos Endpoints da API ---

# --- Endpoints Públicos (GET) ---
@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """Retorna a lista de todos os monstros da biblioteca."""
    monstros_db = buscar_todos_os_monstros()
    lista_de_monstros = [{'id': m[0], 'nome': m[1], 'vida': m[2], 'ataque_bonus': m[3], 'dano_dado': m[4], 'defesa': m[5], 'xp': m[6], 'ouro': m[7]} for m in monstros_db]
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Retorna a lista de todos os itens da biblioteca."""
    itens_db = buscar_todos_os_itens()
    lista_de_itens = [{'id': i[0], 'nome': i[1], 'tipo': i[2], 'descricao': i[3], 'preco': i[4], 'dano': i[5], 'bonus_ataque': i[6], 'efeito': i[7]} for i in itens_db]
    return jsonify(lista_de_itens)

# --- Endpoints de Autenticação (POST) ---
@app.route("/api/registrar", methods=['POST'])
def rota_registrar_usuario():
    """Recebe dados de novo usuário e o salva no DB."""
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
    """Recebe credenciais, verifica no DB e retorna um token JWT se forem válidas."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados:
        return jsonify({"sucesso": False, "mensagem": "Dados ausentes."}), 400
    user_id = verificar_login(dados['username'], dados['password'])
    if user_id:
        token_payload = {
            'sub': str(user_id), 'name': dados['username'],
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token})
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Endpoints Protegidos para FICHAS (CRUD Completo) ---

@app.route("/api/fichas", methods=['GET'])
@token_required 
def get_fichas_usuario(current_user_id):
    """(READ) Busca e retorna todas as fichas que pertencem ao usuário logado."""
    fichas = buscar_fichas_por_usuario(current_user_id)
    return jsonify(fichas)

@app.route("/api/fichas", methods=['POST'])
@token_required
def post_nova_ficha(current_user_id):
    """(CREATE) Cria uma nova ficha de personagem para o usuário logado."""
    dados = request.get_json()
    if not all(k in dados for k in ['nome_personagem', 'classe', 'raca', 'antecedente', 'atributos', 'pericias']):
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400
    sucesso = criar_nova_ficha(
        current_user_id, dados['nome_personagem'], dados['classe'],
        dados['raca'], dados['antecedente'], dados['atributos'], dados['pericias']
    )
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500

@app.route("/api/fichas/<int:id>", methods=['GET'])
@token_required
def get_ficha_unica(current_user_id, id):
    """(READ) Busca e retorna os detalhes de uma única ficha."""
    ficha = buscar_ficha_por_id(id, current_user_id)
    if ficha:
        # CORREÇÃO: Converte as strings JSON do banco de dados de volta para objetos Python.
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
    """(UPDATE) Atualiza os dados de uma ficha existente."""
    dados = request.get_json()
    sucesso = atualizar_ficha(id, current_user_id, dados)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha atualizada com sucesso!'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao atualizar ficha ou permissão negada.'}), 404

@app.route("/api/fichas/<int:id>", methods=['DELETE'])
@token_required
def delete_ficha(current_user_id, id):
    """(DELETE) Apaga uma ficha específica do usuário logado."""
    sucesso = apagar_ficha(id, current_user_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha apagada com sucesso!'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Ficha não encontrada ou permissão negada.'}), 404

# --- Bloco para Iniciar o Servidor ---
if __name__ == "__main__":
    app.run(debug=True, port=5001)
    # --- NOVOS ENDPOINTS PARA SALAS ---

@app.route("/api/salas", methods=['GET'])
@token_required # Protegido, pois só usuários logados podem ver as salas
def get_salas(current_user_id):
    """Busca e retorna a lista de todas as salas de campanha disponíveis."""
    salas = listar_salas_disponiveis()
    return jsonify(salas)

@app.route("/api/salas", methods=['POST'])
@token_required # Protegido, pois só um usuário logado (Mestre) pode criar uma sala
def post_nova_sala(current_user_id):
    """Cria uma nova sala de campanha."""
    dados = request.get_json()
    if not dados or 'nome' not in dados:
        return jsonify({'mensagem': 'Nome da sala é obrigatório.'}), 400
    
    # A senha é opcional
    senha = dados.get('senha', None)
    nome_sala = dados['nome']

    # O 'current_user_id' do token é o ID do Mestre que está criando a sala.
    sucesso = criar_nova_sala(nome_sala, senha, current_user_id)

    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Sala criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Nome de sala já existe ou erro ao criar.'}), 409