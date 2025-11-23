# servidor/servidor_api.py

# --- IMPORTS PRINCIPAIS ---
from flask import Flask, jsonify, request, g # Adicionado 'g' para uso futuro potencial
from flask_socketio import SocketIO, send, join_room, leave_room # Adicionado leave_room
from flask_cors import CORS 
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import json
import sys
import os
import bcrypt # Import bcrypt que faltava (usado em verificar_login, etc.)
import sqlite3 # Import sqlite3 para get_db_connection

# --- IMPORTS DE MÓDulos INTERNOS ---
# (Verificando se todas as funções usadas estão importadas)
from ..database.db_manager import (
    buscar_todos_os_itens, 
    buscar_todos_os_monstros,
    buscar_todas_as_habilidades, # <- Função para a rota GET pública
    criar_novo_monstro,
    atualizar_monstro_existente,
    apagar_monstro_base,
    criar_novo_item,
    atualizar_item_existente,
    apagar_item_base,
    criar_nova_habilidade,
    atualizar_habilidade_existente,
    apagar_habilidade_base,
    registrar_novo_usuario,
    verificar_login,            # <- Usada em rota_fazer_login
    criar_nova_ficha,
    buscar_fichas_por_usuario,
    apagar_ficha,
    buscar_ficha_por_id,
    atualizar_ficha,
    criar_nova_sala,
    listar_salas_disponiveis,
    verificar_senha_da_sala,    # <- Usada em rota_verificar_senha_sala
    salvar_mensagem_chat,
    buscar_historico_chat,
    buscar_dados_essenciais_ficha,
    buscar_anotacoes,
    salvar_anotacoes,            # <- Usada em put_anotacoes (com 'c')
    buscar_inventario_sala,
    adicionar_item_sala,
    apagar_item_sala,
    adicionar_xp_e_upar,        # <- Usada em handle_dar_xp
    buscar_mestre_da_sala       # <- Usada em handle_join_room e handle_dar_xp
)
from ..core.rolador_de_dados import rolar_dados

# --- FUNÇÃO AUXILIAR PARA CONEXÃO COM DB (SE NÃO TIVER NO DB_MANAGER) ---
# Adicionando uma função genérica para obter a conexão, caso precise
# (Se você já tiver uma similar no db_manager, pode remover esta)
DATABASE = os.path.join(os.path.dirname(__file__), '..', 'database', 'campanhas.db')

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Retorna linhas como objetos tipo dicionário
    return conn

# --- CONFIGURAÇÃO DO SERVIDOR ---
app = Flask(__name__)
# CORREÇÃO: Chave secreta corrigida ('secreta' em vez de 'seta')
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345' 

# --- CONFIGURAÇÃO DE CORS (SUA SOLUÇÃO FUNCIONAL) ---
CORS(app, origins=["http://localhost:5173", "http://localhost:5174"], supports_credentials=True)
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
            # Decodifica o token usando a chave secreta
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # Pega o ID do usuário ('sub' = subject) de dentro do token
            current_user_id = int(data['sub']) 
            # Armazena os dados decodificados em 'g' para possível uso em outros decorators
            g.current_user_data_from_token = data 
        except Exception as e:
            print(f"Erro ao decodificar token: {e}")
            return jsonify({'mensagem': 'Token (crachá) inválido ou expirado!'}), 401
        # Chama a rota original passando o ID do usuário
        return f(current_user_id, *args, **kwargs)
    return decorated

# --- NOSSO NOVO DECORATOR DE MESTRE ---
def mestre_required(f):
    """
    Verifica se o usuário tem o 'role' de 'mestre' no token JWT.
    IMPORTANTE: Deve ser usado DEPOIS de @token_required.
    Assume que @token_required já decodificou o token e colocou em g.current_user_data_from_token.
    """
    @wraps(f)
    def decorated(current_user_id, *args, **kwargs): # Recebe o user_id do @token_required
        # Pega os dados decodificados pelo @token_required
        user_data = getattr(g, 'current_user_data_from_token', None) 

        # Verificação de segurança: se o token_required falhou ou não rodou
        if user_data is None: 
             # Pega o token novamente e decodifica (como fallback)
            token = request.headers.get('x-access-token')
            if not token: return jsonify({'mensagem': 'Token ausente!'}), 401
            try:
                user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            except Exception as e:
                print(f"Erro ao decodificar token (fallback mestre_required): {e}")
                return jsonify({'mensagem': 'Token inválido!'}), 401

        # A verificação principal do role
        if user_data.get('role') != 'mestre':
            return jsonify({'mensagem': 'Acesso restrito a Mestres!'}), 403 # 403 Forbidden
            
        # Se for mestre, chama a função da rota original, passando o payload COMPLETO do token
        # (Substitui o current_user_id que seria passado pelo @token_required)
        return f(user_data, *args, **kwargs) 
    return decorated


# --- ROTAS REST DA API (ORGANIZADAS POR FUNCIONALIDADE) ---

# --- Rotas Públicas ---
@app.route("/api/monstros", methods=['GET'])
def get_monstros():
    """Retorna a lista de todos os monstros da biblioteca."""
    monstros_db = buscar_todos_os_monstros()
    # Converte tuplas para dicionários (importante para JSON)
    lista_de_monstros = [{'id': m[0], 'nome': m[1], 'vida_maxima': m[2], 'ataque_bonus': m[3], 'dano_dado': m[4], 'defesa': m[5], 'xp_oferecido': m[6], 'ouro_drop': m[7]} for m in monstros_db]
    return jsonify(lista_de_monstros)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Retorna a lista de todos os itens da biblioteca."""
    itens_db = buscar_todos_os_itens()
    lista_de_itens = [{'id': i[0], 'nome': i[1], 'tipo': i[2], 'descricao': i[3], 'preco_ouro': i[4], 'dano_dado': i[5], 'bonus_ataque': i[6], 'efeito': i[7]} for i in itens_db]
    return jsonify(lista_de_itens)

# --- CORREÇÃO: Definição ÚNICA e Correta da Rota GET /api/habilidades ---
@app.route("/api/habilidades", methods=['GET'])
def get_habilidades():
    """Retorna a lista de todas as habilidades da biblioteca."""
    # Chama a função correta do db_manager
    habilidades_db = buscar_todas_as_habilidades() 
    # A função já retorna uma lista de dicts, pode retornar diretamente
    return jsonify(habilidades_db)
# --- FIM DA CORREÇÃO ---


# --- ROTAS DE GERENCIAMENTO (ESCONDERIJO DO MESTRE) ---

# --- CRUD de Monstros (POST, PUT, DELETE) ---
@app.route("/api/monstros", methods=['POST'])
@token_required
@mestre_required
def post_novo_monstro(current_user_data):
    """(CREATE) Cria um novo monstro."""
    print(f"Mestre (ID: {current_user_data['sub']}) criando monstro.")
    dados = request.get_json()
    campos_necessarios = ['nome', 'vida_maxima', 'ataque_bonus', 'dano_dado', 'defesa', 'xp_oferecido', 'ouro_drop']
    if not all(campo in dados for campo in campos_necessarios):
        return jsonify({'sucesso': False, 'mensagem': 'Dados do monstro incompletos.'}), 400
    try:
        novo_monstro = criar_novo_monstro(dados)
        if novo_monstro: return jsonify({'sucesso': True, 'monstro': novo_monstro}), 201
        else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar monstro (nome duplicado?).'}), 409
    except Exception as e:
        print(f"Erro em post_novo_monstro: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/monstros/<int:monstro_id>", methods=['PUT'])
@token_required
@mestre_required
def update_monstro(current_user_data, monstro_id):
    """(UPDATE) Atualiza um monstro."""
    print(f"Mestre (ID: {current_user_data['sub']}) editando monstro {monstro_id}.")
    dados = request.get_json()
    if not dados: return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido.'}), 400
    try:
        monstro_atualizado = atualizar_monstro_existente(monstro_id, dados)
        if monstro_atualizado: return jsonify({'sucesso': True, 'monstro': monstro_atualizado})
        else: return jsonify({'sucesso': False, 'mensagem': 'Monstro não encontrado ou erro.'}), 404
    except Exception as e:
        print(f"Erro em update_monstro: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/monstros/<int:monstro_id>", methods=['DELETE'])
@token_required
@mestre_required
def delete_monstro(current_user_data, monstro_id):
    """(DELETE) Apaga um monstro."""
    print(f"Mestre (ID: {current_user_data['sub']}) apagando monstro {monstro_id}.")
    try:
        sucesso = apagar_monstro_base(monstro_id)
        if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Monstro apagado.'})
        else: return jsonify({'sucesso': False, 'mensagem': 'Monstro não encontrado.'}), 404
    except Exception as e:
        print(f"Erro em delete_monstro: {e}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno: {e}'}), 500

# --- CRUD de Itens (POST, PUT, DELETE) ---
@app.route("/api/itens", methods=['POST'])
@token_required
@mestre_required
def post_novo_item(current_user_data):
    """(CREATE) Cria um novo item."""
    print(f"Mestre (ID: {current_user_data['sub']}) criando item.")
    dados = request.get_json()
    campos_necessarios = ['nome', 'tipo', 'preco_ouro']
    if not all(campo in dados for campo in campos_necessarios):
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos (nome, tipo, preco_ouro obrigatórios).'}), 400
    try:
        novo_item = criar_novo_item(dados)
        if novo_item: return jsonify({'sucesso': True, 'item': novo_item}), 201
        else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar item (nome duplicado?).'}), 409
    except Exception as e:
        print(f"Erro em post_novo_item: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/itens/<int:item_id>", methods=['PUT'])
@token_required
@mestre_required
def update_item(current_user_data, item_id):
    """(UPDATE) Atualiza um item."""
    print(f"Mestre (ID: {current_user_data['sub']}) editando item {item_id}.")
    dados = request.get_json()
    if not dados: return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido.'}), 400
    try:
        item_atualizado = atualizar_item_existente(item_id, dados)
        if item_atualizado: return jsonify({'sucesso': True, 'item': item_atualizado})
        else: return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado ou erro.'}), 404
    except Exception as e:
        print(f"Erro em update_item: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/itens/<int:item_id>", methods=['DELETE'])
@token_required
@mestre_required
def delete_item(current_user_data, item_id):
    """(DELETE) Apaga um item."""
    print(f"Mestre (ID: {current_user_data['sub']}) apagando item {item_id}.")
    try:
        sucesso = apagar_item_base(item_id)
        if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Item apagado.'})
        else: return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado.'}), 404
    except Exception as e:
        print(f"Erro em delete_item: {e}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno: {e}'}), 500

# --- CRUD de Habilidades (POST, PUT, DELETE) ---
# A rota GET pública já está definida acima.
@app.route("/api/habilidades", methods=['POST'])
@token_required
@mestre_required
def post_nova_habilidade(current_user_data):
    """(CREATE) Cria uma nova habilidade."""
    print(f"Mestre (ID: {current_user_data['sub']}) criando habilidade.")
    dados = request.get_json()
    campos_necessarios = ['nome', 'efeito']
    if not all(campo in dados for campo in campos_necessarios):
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos (nome, efeito obrigatórios).'}), 400
    try:
        nova_habilidade = criar_nova_habilidade(dados)
        if nova_habilidade: return jsonify({'sucesso': True, 'habilidade': nova_habilidade}), 201
        else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar habilidade (nome duplicado?).'}), 409
    except Exception as e:
        print(f"Erro em post_nova_habilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/habilidades/<int:habilidade_id>", methods=['PUT'])
@token_required
@mestre_required
def update_habilidade(current_user_data, habilidade_id):
    """(UPDATE) Atualiza uma habilidade."""
    print(f"Mestre (ID: {current_user_data['sub']}) editando habilidade {habilidade_id}.")
    dados = request.get_json()
    if not dados: return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido.'}), 400
    try:
        habilidade_atualizada = atualizar_habilidade_existente(habilidade_id, dados)
        if habilidade_atualizada: return jsonify({'sucesso': True, 'habilidade': habilidade_atualizada})
        else: return jsonify({'sucesso': False, 'mensagem': 'Habilidade não encontrada ou erro.'}), 404
    except Exception as e:
        print(f"Erro em update_habilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/habilidades/<int:habilidade_id>", methods=['DELETE'])
@token_required
@mestre_required
def delete_habilidade(current_user_data, habilidade_id):
    """(DELETE) Apaga uma habilidade."""
    print(f"Mestre (ID: {current_user_data['sub']}) apagando habilidade {habilidade_id}.")
    try:
        sucesso = apagar_habilidade_base(habilidade_id)
        if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Habilidade apagada.'})
        else: return jsonify({'sucesso': False, 'mensagem': 'Habilidade não encontrada.'}), 404
    except Exception as e:
        print(f"Erro em delete_habilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno: {e}'}), 500


# --- Rotas de Autenticação ---
@app.route("/api/registrar", methods=['POST'])
def rota_registrar_usuario():
    """Registra um novo usuário."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados: 
        return jsonify({"sucesso": False, "mensagem": "Dados incompletos."}), 400
    # A função registrar_novo_usuario lida com o hashing
    sucesso = registrar_novo_usuario(dados['username'], dados['password'])
    if sucesso: 
        return jsonify({"sucesso": True, "mensagem": "Usuário registrado com sucesso!"}), 201
    else: 
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário já está em uso."}), 409

@app.route("/api/login", methods=['POST'])
def rota_fazer_login():
    """Realiza o login e retorna um token JWT com id, nome e role."""
    dados = request.get_json()
    if not dados or 'username' not in dados or 'password' not in dados: 
        return jsonify({"sucesso": False, "mensagem": "Dados ausentes."}), 400
    # verificar_login retorna {'id': ..., 'role': ...} ou None
    user_data_from_db = verificar_login(dados['username'], dados['password'])
    if user_data_from_db:
        # Cria o payload do token
        token_payload = { 
            'sub': str(user_data_from_db['id']), # ID do usuário
            'name': dados['username'],           # Nome de usuário
            'role': user_data_from_db['role'],   # Papel ('player' ou 'mestre')
            'iat': datetime.now(timezone.utc),   # Data de emissão
            'exp': datetime.now(timezone.utc) + timedelta(hours=24) # Data de expiração (24h)
        }
        # Gera o token JWT
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        # Retorna o token e o role para o frontend
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token, "role": user_data_from_db['role']})
    else: 
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Rotas de Fichas (Protegidas) ---
@app.route("/api/fichas", methods=['GET'])
@token_required
def get_fichas_usuario(current_user_id):
    """(READ) Busca as fichas do usuário logado."""
    fichas = buscar_fichas_por_usuario(current_user_id)
    return jsonify(fichas)

@app.route("/api/fichas", methods=['POST'])
@token_required
def post_nova_ficha(current_user_id):
    """(CREATE) Cria uma nova ficha para o usuário logado."""
    dados = request.get_json()
    campos_obrigatorios = ['nome_personagem', 'classe', 'raca', 'antecedente', 'atributos', 'pericias']
    if not all(k in dados for k in campos_obrigatorios):
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400
    sucesso = criar_nova_ficha(
        current_user_id, dados['nome_personagem'], dados['classe'], dados['raca'], 
        dados['antecedente'], dados['atributos'], dados['pericias']
    )
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500

@app.route("/api/fichas/<int:id>", methods=['GET'])
@token_required
def get_ficha_unica(current_user_id, id):
    """(READ) Busca detalhes de uma ficha específica do usuário."""
    ficha = buscar_ficha_por_id(id, current_user_id)
    if ficha:
        # Converte JSON strings do DB para objetos Python antes de enviar
        if ficha.get('atributos_json'): ficha['atributos'] = json.loads(ficha['atributos_json'])
        if ficha.get('pericias_json'): ficha['pericias'] = json.loads(ficha['pericias_json'])
        return jsonify(dict(ficha)) # Garante que é um dict padrão
    else: return jsonify({'mensagem': 'Ficha não encontrada ou permissão negada.'}), 404

@app.route("/api/fichas/<int:id>", methods=['PUT'])
@token_required
def update_ficha(current_user_id, id):
    """(UPDATE) Atualiza uma ficha do usuário."""
    dados = request.get_json()
    # Assume que 'atualizar_ficha' lida com a conversão para JSON se necessário
    sucesso = atualizar_ficha(id, current_user_id, dados) 
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Ficha atualizada com sucesso!'})
    else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao atualizar ficha ou permissão negada.'}), 404
        
@app.route("/api/fichas/<int:id>", methods=['DELETE'])
@token_required
def delete_ficha(current_user_id, id):
    """(DELETE) Apaga uma ficha do usuário."""
    sucesso = apagar_ficha(id, current_user_id)
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Ficha apagada com sucesso!'})
    else: return jsonify({'sucesso': False, 'mensagem': 'Ficha não encontrada ou permissão negada.'}), 404

# --- Rotas de Salas (Protegidas) ---
@app.route("/api/salas", methods=['GET'])
@token_required
def get_salas(current_user_id):
    """Lista todas as salas disponíveis."""
    salas = listar_salas_disponiveis() # Já retorna dicts
    return jsonify(salas)

@app.route("/api/salas", methods=['POST'])
@token_required
def post_nova_sala(current_user_id):
    """Cria uma nova sala, com o usuário atual como Mestre."""
    dados = request.get_json()
    if not dados or 'nome' not in dados:
        return jsonify({'mensagem': 'Nome da sala é obrigatório.'}), 400
    # criar_nova_sala lida com o hashing da senha se ela existir
    sucesso = criar_nova_sala(dados['nome'], dados.get('senha'), current_user_id) 
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Sala criada com sucesso!'}), 201
    else: return jsonify({'sucesso': False, 'mensagem': 'Nome de sala já existe ou erro ao criar.'}), 409

@app.route("/api/salas/verificar-senha", methods=['POST'])
@token_required
def rota_verificar_senha_sala(current_user_id):
    """Verifica se a senha de uma sala está correta."""
    dados = request.get_json()
    if not dados or 'sala_id' not in dados or 'senha' not in dados:
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos.'}), 400
    senha_valida = verificar_senha_da_sala(dados['sala_id'], dados['senha'])
    return jsonify({'sucesso': senha_valida, 'mensagem': 'Senha da sala incorreta.' if not senha_valida else ''})

# --- Rotas de Anotações (Protegidas) ---
@app.route("/api/salas/<int:sala_id>/anotacoes", methods=['GET'])
@token_required
def get_anotacoes(current_user_id, sala_id):
    """Busca as anotações do usuário para a sala."""
    notas = buscar_anotacoes(current_user_id, sala_id)
    return jsonify({'notas': notas if notas is not None else ""}) # Garante retorno de string

@app.route("/api/salas/<int:sala_id>/anotacoes", methods=['PUT'])
@token_required
def put_anotacoes(current_user_id, sala_id):
    """Salva/Atualiza as anotações do usuário para a sala."""
    dados = request.get_json()
    if 'notas' not in dados:
        return jsonify({'mensagem': 'Dados de anotações ausentes'}), 400
    # Usa salvar_anotacoes (com 'c')
    sucesso = salvar_anotacoes(current_user_id, sala_id, dados['notas']) 
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Anotações salvas!'})
    else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao salvar anotações.'}), 500

# --- Rotas de Inventário de Sala (Protegidas) ---
@app.route("/api/salas/<int:sala_id>/inventario", methods=['GET'])
@token_required
def get_inventario_sala(current_user_id, sala_id):
    """Busca o inventário de uma ficha específica na sala."""
    ficha_id = request.args.get('ficha_id') # Pega da query string ?ficha_id=X
    if not ficha_id: return jsonify({'mensagem': 'ID da Ficha ausente na requisição'}), 400
    # Verifica se o usuário logado é dono da ficha
    ficha_valida = buscar_dados_essenciais_ficha(ficha_id, current_user_id)
    if not ficha_valida: return jsonify({'mensagem': 'Permissão negada: esta ficha não é sua.'}), 403
    itens = buscar_inventario_sala(ficha_id, sala_id) # Busca itens
    return jsonify([dict(item) for item in itens]) # Garante lista de dicts

@app.route("/api/salas/<int:sala_id>/inventario", methods=['POST'])
@token_required
def post_item_sala(current_user_id, sala_id):
    """Adiciona um item ao inventário de uma ficha na sala."""
    dados = request.get_json()
    if not dados or 'ficha_id' not in dados or 'nome_item' not in dados:
        return jsonify({'mensagem': 'Dados do item incompletos'}), 400
    ficha_valida = buscar_dados_essenciais_ficha(dados['ficha_id'], current_user_id)
    if not ficha_valida: return jsonify({'mensagem': 'Permissão negada.'}), 403
    sucesso = adicionar_item_sala(dados['ficha_id'], sala_id, dados['nome_item'], dados.get('descricao', ''))
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Item adicionado ao inventário!'}), 201
    else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao adicionar item.'}), 500

@app.route("/api/inventario-sala/<int:item_id>", methods=['DELETE'])
@token_required
def delete_item_sala(current_user_id, item_id):
    """Apaga um item do inventário (requer ficha_id no corpo)."""
    # Espera { "ficha_id": X } no corpo da requisição DELETE
    dados = request.get_json() 
    ficha_id = dados.get('ficha_id') if dados else None # Pega ficha_id do corpo
    if not ficha_id: return jsonify({'mensagem': 'ID da Ficha ausente no corpo da requisição.'}), 400
    ficha_valida = buscar_dados_essenciais_ficha(ficha_id, current_user_id)
    if not ficha_valida: return jsonify({'mensagem': 'Permissão negada.'}), 403
    sucesso = apagar_item_sala(item_id, ficha_id)
    if sucesso: return jsonify({'sucesso': True, 'mensagem': 'Item descartado.'})
    else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao descartar item ou item não encontrado.'}), 404

# --- EVENTOS SOCKET.IO ---

# Dicionário global para rastrear usuários conectados e suas informações por sala
# Estrutura: { 'sala_id': { 'sid': {'user_id': X, 'ficha_id': Y, 'nome_personagem': Z, 'role': R} } }
salas_ativas = {}

@socketio.on('connect')
def handle_connect():
    """Chamado quando um cliente estabelece uma conexão WebSocket."""
    print(f"Cliente conectado! SID: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Chamado quando um cliente se desconecta."""
    print(f"Cliente desconectado! SID: {request.sid}")
    
    sala_para_remover_de = None
    jogador_removido_info = None
    
    # Encontra e remove o jogador do dicionário 'salas_ativas'
    for sala_id, jogadores in salas_ativas.items():
        if request.sid in jogadores:
            sala_para_remover_de = str(sala_id) # Garante que ID da sala é string
            jogador_removido_info = jogadores.pop(request.sid) # Remove usando o SID como chave
            # Se a sala ficar vazia após remover o jogador, remove a sala do dicionário
            if not jogadores: 
                del salas_ativas[sala_id]
            break # Sai do loop assim que encontrar e remover
            
    # Se um jogador foi removido de uma sala
    if sala_para_remover_de and jogador_removido_info:
        nome_personagem = jogador_removido_info['nome_personagem']
        
        # Envia a lista atualizada de jogadores para TODOS que ainda estão na sala
        # Verifica se a sala ainda existe (pode ter sido removida se ficou vazia)
        if sala_para_remover_de in salas_ativas:
             socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_para_remover_de].values()), to=sala_para_remover_de)
        
        # Envia a mensagem de saída para a sala (se ainda houver alguém)
        mensagem_saida = f"--- {nome_personagem} saiu da taverna. ---"
        send(mensagem_saida, to=sala_para_remover_de) # send() lida com sala vazia
        # Salva a mensagem de saída no histórico do chat
        salvar_mensagem_chat(sala_para_remover_de, 'Sistema', mensagem_saida)
        print(f"{nome_personagem} removido da sala {sala_para_remover_de}")

@socketio.on('join_room')
def handle_join_room(data):
    """Evento disparado pelo frontend quando um usuário tenta entrar numa sala."""
    token = data.get('token')
    sala_id = str(data.get('sala_id')) # Garante que ID da sala é string
    ficha_id = data.get('ficha_id') # Pode ser None se for Mestre
    
    # Validações iniciais
    if not token or not sala_id:
        socketio.emit('join_error', {'mensagem': 'Token ou ID da sala ausente.'}, room=request.sid)
        return
        
    try:
        # 1. Valida o Token JWT e extrai dados do usuário
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        user_name = user_data['name'] # Nome de usuário (usado se for mestre)
        
        # 2. Verifica se o usuário é o Mestre desta sala
        mestre_id_da_sala = buscar_mestre_da_sala(sala_id)
        if mestre_id_da_sala is None: # Checa se a sala existe no DB
             socketio.emit('join_error', {'mensagem': 'Sala não encontrada.'}, room=request.sid)
             return
        is_mestre = (user_id == mestre_id_da_sala)
        
        # 3. Inicializa o rastreamento da sala se for o primeiro a entrar
        if sala_id not in salas_ativas:
            salas_ativas[sala_id] = {}
            
        # 4. Lógica de Mestre vs Jogador
        role = ''
        nome_personagem = ''
        ficha_id_real = None # ID da ficha a ser armazenado (None para Mestre)

        if is_mestre:
            role = 'mestre'
            nome_personagem = user_name # Mestre usa o nome de usuário
            # Verifica se já existe um mestre ativo nesta sala
            mestre_existente_sid = next((sid for sid, info in salas_ativas[sala_id].items() if info['role'] == 'mestre'), None)
            if mestre_existente_sid and mestre_existente_sid != request.sid: # Se existe E não sou eu mesmo reconectando
                socketio.emit('join_error', {'mensagem': 'Já existe um Mestre ativo nesta sala.'}, room=request.sid)
                return
        else: # Se for Jogador
            role = 'player'
            if not ficha_id: # Jogador PRECISA ter uma ficha
                socketio.emit('join_error', {'mensagem': 'Jogador deve selecionar uma ficha.'}, room=request.sid)
                return
            # Valida se a ficha pertence ao usuário
            ficha_data = buscar_dados_essenciais_ficha(ficha_id, user_id)
            if not ficha_data:
                socketio.emit('join_error', {'mensagem': 'Ficha inválida ou não pertence a você.'}, room=request.sid)
                return
            nome_personagem = ficha_data['nome_personagem'] # Jogador usa nome do personagem
            ficha_id_real = ficha_id

        # 5. Adiciona o usuário à sala do SocketIO
        join_room(sala_id)
        
        # 6. Adiciona/Atualiza informações do jogador no nosso dicionário 'salas_ativas'
        salas_ativas[sala_id][request.sid] = {
            'user_id': user_id,
            'ficha_id': ficha_id_real,
            'nome_personagem': nome_personagem,
            'role': role
        }
        
        # 7. Envia informações específicas para o cliente que acabou de entrar
        # Informa se ele é mestre (para UI condicional)
        socketio.emit('status_mestre', {'isMestre': is_mestre}, room=request.sid) 
        # Envia o histórico de chat da sala
        historico = buscar_historico_chat(sala_id)
        socketio.emit('chat_history', {'historico': historico}, room=request.sid)
        
        # 8. Envia informações para TODOS na sala
        remetente_formatado = f"Mestre ({nome_personagem})" if is_mestre else nome_personagem
        mensagem_entrada = f"--- {remetente_formatado} entrou na taverna! ---"
        # Envia mensagem de entrada para todos na sala
        send(mensagem_entrada, to=sala_id) 
        # Salva mensagem de entrada no histórico
        salvar_mensagem_chat(sala_id, 'Sistema', mensagem_entrada) 
        # Envia lista atualizada de jogadores para todos na sala
        socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_id].values()), to=sala_id)
        
        print(f"{remetente_formatado} (User ID: {user_id}, SID: {request.sid}) entrou na sala {sala_id}")
        
    except jwt.ExpiredSignatureError:
        socketio.emit('join_error', {'mensagem': 'Token expirado. Faça login novamente.'}, room=request.sid)
    except Exception as e:
        print(f"Erro em handle_join_room: {e}")
        socketio.emit('join_error', {'mensagem': f'Erro ao entrar na sala: {e}'}, room=request.sid)

@socketio.on('send_message')
def handle_send_message(data):
    """Recebe mensagem de chat, salva no DB e retransmite para a sala."""
    sala_id = str(data.get('sala_id'))
    message_text = data.get('message')
    
    # Valida dados e se o remetente está na sala rastreada
    if not sala_id or not message_text or sala_id not in salas_ativas or request.sid not in salas_ativas[sala_id]:
        print(f"Erro send_message: Dados inválidos ou remetente não encontrado. SID: {request.sid}, Sala: {sala_id}")
        # Poderia enviar um erro de volta para o remetente, mas vamos evitar flood
        return 
        
    try:
        # Pega informações do remetente do nosso dicionário 'salas_ativas'
        jogador_info = salas_ativas[sala_id][request.sid]
        nome_personagem = jogador_info['nome_personagem']
        remetente_formatado = f"[Mestre] {nome_personagem}" if jogador_info['role'] == 'mestre' else nome_personagem
        
        # Salva a mensagem original no banco de dados
        salvar_mensagem_chat(sala_id, remetente_formatado, message_text)
        
        # Formata a mensagem para exibição no chat
        formatted_message = f"[{remetente_formatado}]: {message_text}"
        
        # Envia a mensagem formatada para TODOS na sala
        send(formatted_message, to=sala_id)
    except Exception as e:
        print(f"Erro em handle_send_message: {e}")
        # Enviar erro de volta pode ser útil para depuração no cliente
        socketio.emit('chat_error', {'mensagem': 'Erro ao enviar mensagem.'}, room=request.sid)


@socketio.on('roll_dice')
def handle_roll_dice(data):
    """Recebe comando de rolagem, processa, salva no DB e retransmite."""
    sala_id = str(data.get('sala_id'))
    dice_command = data.get('command')

    if not sala_id or not dice_command or sala_id not in salas_ativas or request.sid not in salas_ativas[sala_id]:
        print(f"Erro roll_dice: Dados inválidos ou remetente não encontrado. SID: {request.sid}, Sala: {sala_id}")
        return

    try:
        jogador_info = salas_ativas[sala_id][request.sid]
        nome_personagem = jogador_info['nome_personagem']
        remetente_formatado = f"[Mestre] {nome_personagem}" if jogador_info['role'] == 'mestre' else nome_personagem
        
        # Rola os dados usando o módulo 'core'
        total, rolagens = rolar_dados(dice_command)
        
        # Formata o resultado (mostra rolagens individuais se houver mais de um dado)
        resultado_str = f"{total} ({', '.join(map(str, rolagens))})" if rolagens and len(rolagens) > 1 else str(total)
        
        # Monta a mensagem para o chat e para o log
        mensagem_chat = f"🎲 [{remetente_formatado}] rolou {dice_command} e tirou: {resultado_str}"
        mensagem_log = f"[{remetente_formatado}] rolou {dice_command}: {resultado_str}" # Log mais simples
        
        # Salva o log no histórico do chat
        salvar_mensagem_chat(sala_id, 'Sistema', mensagem_log)
        # Envia a mensagem formatada para TODOS na sala
        send(mensagem_chat, to=sala_id)
    except Exception as e:
        print(f"Erro em handle_roll_dice: {e}")
        socketio.emit('chat_error', {'mensagem': 'Erro ao rolar dados.'}, room=request.sid)

@socketio.on('mestre_dar_xp')
def handle_dar_xp(data):
    """Recebe comando do Mestre para dar XP, processa e notifica a sala."""
    sala_id = str(data.get('sala_id'))
    alvo_id_str = data.get('alvo_id') # Pode ser 'all' ou um ID de ficha
    quantidade_str = data.get('quantidade')
    token = data.get('token') # Token para verificar se é o Mestre mesmo

    # Validações
    if not all([token, sala_id, alvo_id_str, quantidade_str]):
        socketio.emit('mestre_error', {'mensagem': 'Dados de XP incompletos.'}, room=request.sid)
        return

    try:
        # 1. Valida o Token e verifica se o remetente é o Mestre da sala
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        mestre_id_da_sala = buscar_mestre_da_sala(sala_id)
        if user_id != mestre_id_da_sala:
            socketio.emit('mestre_error', {'mensagem': 'Apenas o Mestre pode dar XP.'}, room=request.sid)
            return

        quantidade_xp = int(quantidade_str)
        if quantidade_xp <= 0: return # Ignora XP zero ou negativo

        fichas_para_atualizar_ids = []
        
        # 2. Determina as fichas alvo
        if alvo_id_str == 'all':
            # Pega IDs das fichas de todos os JOGADORES ('player') ativos na sala
            if sala_id in salas_ativas:
                fichas_para_atualizar_ids = [
                    info['ficha_id'] for sid, info in salas_ativas[sala_id].items() 
                    if info['role'] == 'player' and info['ficha_id'] is not None
                ]
        else:
            try:
                # Se não for 'all', tenta converter para ID numérico
                fichas_para_atualizar_ids = [int(alvo_id_str)]
            except ValueError:
                socketio.emit('mestre_error', {'mensagem': 'ID de alvo inválido.'}, room=request.sid)
                return

        if not fichas_para_atualizar_ids:
            socketio.emit('mestre_feedback', {'mensagem': 'Nenhum jogador alvo encontrado na sala.'}, room=request.sid)
            return

        # 3. Itera e aplica XP para cada ficha alvo
        for ficha_id in fichas_para_atualizar_ids:
            # Chama a função do db_manager que lida com XP e Level Up
            ficha_atualizada = adicionar_xp_e_upar(ficha_id, quantidade_xp)
            
            if ficha_atualizada:
                # Prepara os dados da ficha para enviar via SocketIO (converte JSON)
                try:
                    ficha_atualizada['atributos'] = json.loads(ficha_atualizada['atributos_json'])
                    ficha_atualizada['pericias'] = json.loads(ficha_atualizada['pericias_json'])
                except (json.JSONDecodeError, KeyError) as e:
                     print(f"Erro ao converter JSON da ficha {ficha_id} após XP: {e}")
                     # Continua mesmo assim, mas pode dar erro no frontend ao acessar atributos/pericias
                
                # 4. Notifica TODOS na sala sobre a atualização da ficha (para barra de XP)
                socketio.emit('ficha_atualizada', ficha_atualizada, to=sala_id)
                
                # 5. Envia mensagens de feedback para o chat da sala
                nome_alvo = ficha_atualizada['nome_personagem']
                mensagem_xp = f"--- {nome_alvo} recebe {quantidade_xp} XP! ---"
                salvar_mensagem_chat(sala_id, 'Sistema', mensagem_xp)
                send(mensagem_xp, to=sala_id)

                # Se a função retornou que subiu de nível...
                if ficha_atualizada.get('subiu_de_nivel', False): 
                    mensagem_lvl = f"🎉🎉🎉 PARABÉNS! {nome_alvo} subiu para o nível {ficha_atualizada['nivel']}! 🎉🎉🎉"
                    salvar_mensagem_chat(sala_id, 'Sistema', mensagem_lvl)
                    send(mensagem_lvl, to=sala_id)
                    print(f"Ficha {ficha_id} ({nome_alvo}) subiu para o nível {ficha_atualizada['nivel']}")
            else:
                # Informa o Mestre se falhou em dar XP para uma ficha específica
                print(f"Falha ao dar XP para ficha ID: {ficha_id}")
                socketio.emit('mestre_error', {'mensagem': f'Falha ao dar XP para ficha ID {ficha_id}.'}, room=request.sid)

    except jwt.ExpiredSignatureError:
         socketio.emit('mestre_error', {'mensagem': 'Token expirado.'}, room=request.sid)
    except Exception as e:
        print(f"Erro em handle_dar_xp: {e}")
        socketio.emit('mestre_error', {'mensagem': f'Erro ao processar XP: {e}'}, room=request.sid)

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    print("Iniciando o servidor Flask com SocketIO via Eventlet na porta 5001...")
    import eventlet
    # CORREÇÃO: Usar porta 5001 consistentemente
    eventlet.wsgi.server(eventlet.listen(('', 5001)), app)