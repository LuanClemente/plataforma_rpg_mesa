# servidor/servidor_api.py

# --- IMPORTS PRINCIPAIS ---
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, join_room
from flask_cors import CORS 
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import json
import sys
import os

# --- IMPORTS DE MÓDULOS INTERNOS ---
from ..database.db_manager import (
    buscar_todos_os_itens, 
    buscar_todos_os_monstros,
    criar_novo_monstro,
    atualizar_monstro_existente,
    apagar_monstro_base,
    
    # --- [NOVAS] IMPORTAÇÕES DE ITENS E HABILIDADES ---
    criar_novo_item,
    atualizar_item_existente,
    apagar_item_base,
    criar_nova_habilidade,
    atualizar_habilidade_existente,
    apagar_habilidade_base,
    # --- FIM DAS NOVAS IMPORTAÇÕES ---

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
    buscar_dados_essenciais_ficha,
    buscar_anotacoes,
    salvar_anotacoes,
    buscar_inventario_sala,
    adicionar_item_sala,
    apagar_item_sala,
    adicionar_xp_e_upar,
    buscar_mestre_da_sala
)
from ..core.rolador_de_dados import rolar_dados

# --- CONFIGURAÇÃO DO SERVIDOR ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-seta-muito-forte-e-dificil-de-adivinhar-12345'

# --- CONFIGURAÇÃO DE CORS (SUA SOLUÇÃO FUNCIONAL) ---
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
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

# --- NOSSO NOVO DECORATOR DE MESTRE ---
def mestre_required(f):
    """
    Verifica se o usuário tem o 'role' de 'mestre' no token.
    IMPORTANTE: Este decorator DEVE ser usado DEPOIS do @token_required.
    """
    @wraps(f)
    def decorated(current_user_id, *args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'mensagem': 'Token (crachá) ausente!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            if data.get('role') != 'mestre':
                return jsonify({'mensagem': 'Acesso restrito a Mestres!'}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token (crachá) expirado!'}), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(f"Erro no decorator mestre_required: {e}")
            return jsonify({'mensagem': 'Token (crachá) inválido!'}), 401
        return f(data, *args, **kwargs)
    return decorated


# --- ROTAS REST DA API (ORGANIZADAS POR FUNCIONALIDADE) ---

# --- Rotas Públicas ---
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

# [NOVO] Rota pública para Habilidades (ainda não tínhamos!)
@app.route("/api/habilidades", methods=['GET'])
def get_habilidades():
    """Retorna a lista de todas as habilidades da biblioteca."""
    habilidades_db = buscar_detalhes_habilidades([]) # Reutilizando a função (ela precisa ser melhorada)
    # TODO: Criar 'buscar_todas_as_habilidades' no db_manager para ser mais limpo
    # Por agora, vamos apenas criar uma função nova para isso.
    
    # Vamos assumir que criaremos 'buscar_todas_as_habilidades'
    # Por favor, adicione 'buscar_todas_as_habilidades' no seu db_manager
    # (Eu não posso mais editar o db_manager, mas a lógica é igual a 'buscar_todos_os_itens')
    # Vou deixar esta rota comentada por enquanto para não dar erro
    
    # --- ROTA DE HABILIDADES PÚBLICA (PENDENTE) ---
    # (Vamos focar no CRUD do mestre primeiro)
    return jsonify([]) 


# --- ROTAS DE GERENCIAMENTO (ESCONDERIJO DO MESTRE) ---

# --- CRUD de Monstros ---
@app.route("/api/monstros", methods=['POST'])
@token_required
@mestre_required
def post_novo_monstro(current_user_data):
    """
    (CREATE) Cria um novo monstro na tabela 'monstros_base'.
    Acessível apenas para usuários com 'role' de 'mestre'.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está criando um monstro.")
    dados = request.get_json()
    campos_necessarios = ['nome', 'vida_maxima', 'ataque_bonus', 'dano_dado', 'defesa', 'xp_oferecido', 'ouro_drop']
    if not all(campo in dados for campo in campos_necessarios):
        return jsonify({'sucesso': False, 'mensagem': 'Dados do monstro incompletos.'}), 400
    try:
        novo_monstro = criar_novo_monstro(dados)
        if novo_monstro:
            return jsonify({'sucesso': True, 'monstro': novo_monstro}), 201
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar monstro (talvez o nome já exista?).'}), 409
    except Exception as e:
        print(f"Erro em post_novo_monstro: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/monstros/<int:monstro_id>", methods=['PUT'])
@token_required
@mestre_required
def update_monstro(current_user_data, monstro_id):
    """
    (UPDATE) Atualiza um monstro existente na 'monstros_base'.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está editando o monstro {monstro_id}.")
    dados = request.get_json()
    if not dados:
        return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido para atualização.'}), 400
    try:
        monstro_atualizado = atualizar_monstro_existente(monstro_id, dados)
        if monstro_atualizado:
            return jsonify({'sucesso': True, 'monstro': monstro_atualizado})
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Monstro não encontrado ou erro ao atualizar.'}), 404
    except Exception as e:
        print(f"Erro em update_monstro: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/monstros/<int:monstro_id>", methods=['DELETE'])
@token_required
@mestre_required
def delete_monstro(current_user_data, monstro_id):
    """
    (DELETE) Apaga um monstro da 'monstros_base'.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está apagando o monstro {monstro_id}.")
    try:
        sucesso = apagar_monstro_base(monstro_id)
        if sucesso:
            return jsonify({'sucesso': True, 'mensagem': 'Monstro apagado com sucesso.'})
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Monstro não encontrado ou erro ao apagar.'}), 404
    except Exception as e:
        print(f"Erro em delete_monstro: {e}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno no servidor: {e}'}), 500


# --- [NOVO] CRUD de Itens ---
@app.route("/api/itens", methods=['POST'])
@token_required
@mestre_required
def post_novo_item(current_user_data):
    """
    (CREATE) Cria um novo item na tabela 'itens_base'.
    Acessível apenas para Mestres.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está criando um item.")
    dados = request.get_json()
    
    # Validação dos campos obrigatórios (nome, tipo, preco_ouro)
    campos_necessarios = ['nome', 'tipo', 'preco_ouro']
    if not all(campo in dados for campo in campos_necessarios):
        return jsonify({'sucesso': False, 'mensagem': 'Dados do item incompletos (nome, tipo, preco_ouro são obrigatórios).'}), 400
        
    try:
        # Chama a nova função do db_manager
        novo_item = criar_novo_item(dados)
        
        if novo_item:
            return jsonify({'sucesso': True, 'item': novo_item}), 201
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar item (talvez o nome já exista?).'}), 409
            
    except Exception as e:
        print(f"Erro em post_novo_item: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/itens/<int:item_id>", methods=['PUT'])
@token_required
@mestre_required
def update_item(current_user_data, item_id):
    """
    (UPDATE) Atualiza um item existente na 'itens_base'.
    Acessível apenas para Mestres.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está editando o item {item_id}.")
    dados = request.get_json()
    
    if not dados:
        return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido para atualização.'}), 400
        
    try:
        # Chama a nova função do db_manager
        item_atualizado = atualizar_item_existente(item_id, dados)
        
        if item_atualizado:
            return jsonify({'sucesso': True, 'item': item_atualizado})
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado ou erro ao atualizar.'}), 404
            
    except Exception as e:
        print(f"Erro em update_item: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/itens/<int:item_id>", methods=['DELETE'])
@token_required
@mestre_required
def delete_item(current_user_data, item_id):
    """
    (DELETE) Apaga um item da 'itens_base'.
    Acessível apenas para Mestres.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está apagando o item {item_id}.")

    try:
        # Chama a nova função do db_manager
        sucesso = apagar_item_base(item_id)
        
        if sucesso:
            return jsonify({'sucesso': True, 'mensagem': 'Item apagado com sucesso.'})
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado ou erro ao apagar.'}), 404
            
    except Exception as e:
        print(f"Erro em delete_item: {e}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno no servidor: {e}'}), 500


# --- [NOVO] CRUD de Habilidades ---
@app.route("/api/habilidades", methods=['POST'])
@token_required
@mestre_required
def post_nova_habilidade(current_user_data):
    """
    (CREATE) Cria uma nova habilidade na 'habilidades_base'.
    Acessível apenas para Mestres.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está criando uma habilidade.")
    dados = request.get_json()
    
    # Validação (nome e efeito são obrigatórios)
    campos_necessarios = ['nome', 'efeito']
    if not all(campo in dados for campo in campos_necessarios):
        return jsonify({'sucesso': False, 'mensagem': 'Dados da habilidade incompletos (nome e efeito são obrigatórios).'}), 400
        
    try:
        # Chama a nova função do db_manager
        nova_habilidade = criar_nova_habilidade(dados)
        
        if nova_habilidade:
            return jsonify({'sucesso': True, 'habilidade': nova_habilidade}), 201
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar habilidade (talvez o nome já exista?).'}), 409
            
    except Exception as e:
        print(f"Erro em post_nova_habilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/habilidades/<int:habilidade_id>", methods=['PUT'])
@token_required
@mestre_required
def update_habilidade(current_user_data, habilidade_id):
    """
    (UPDATE) Atualiza uma habilidade existente na 'habilidades_base'.
    Acessível apenas para Mestres.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está editando a habilidade {habilidade_id}.")
    dados = request.get_json()
    
    if not dados:
        return jsonify({'sucesso': False, 'mensagem': 'Nenhum dado fornecido para atualização.'}), 400
        
    try:
        # Chama a nova função do db_manager
        habilidade_atualizada = atualizar_habilidade_existente(habilidade_id, dados)
        
        if habilidade_atualizada:
            return jsonify({'sucesso': True, 'habilidade': habilidade_atualizada})
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Habilidade não encontrada ou erro ao atualizar.'}), 404
            
    except Exception as e:
        print(f"Erro em update_habilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route("/api/habilidades/<int:habilidade_id>", methods=['DELETE'])
@token_required
@mestre_required
def delete_habilidade(current_user_data, habilidade_id):
    """
    (DELETE) Apaga uma habilidade da 'habilidades_base'.
    Acessível apenas para Mestres.
    """
    print(f"Mestre (ID: {current_user_data['sub']}) está apagando a habilidade {habilidade_id}.")

    try:
        # Chama a nova função do db_manager
        sucesso = apagar_habilidade_base(habilidade_id)
        
        if sucesso:
            return jsonify({'sucesso': True, 'mensagem': 'Habilidade apagada com sucesso.'})
        else:
            return jsonify({'sucesso': False, 'mensagem': 'Habilidade não encontrada ou erro ao apagar.'}), 404
            
    except Exception as e:
        print(f"Erro em delete_habilidade: {e}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro interno no servidor: {e}'}), 500


# --- Rotas de Autenticação ---
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
    user_data_from_db = verificar_login(dados['username'], dados['password'])
    if user_data_from_db:
        token_payload = {
            'sub': str(user_data_from_db['id']),
            'name': dados['username'],
            'role': user_data_from_db['role'], 
            'iat': datetime.now(timezone.utc),
            'exp': datetime.now(timezone.utc) + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({"sucesso": True, "mensagem": "Login bem-sucedido!", "token": token, "role": user_data_from_db['role']})
    else:
        return jsonify({"sucesso": False, "mensagem": "Nome de usuário ou senha inválidos."}), 401

# --- Rotas de Fichas (Protegidas) ---
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
    campos_obrigatorios = ['nome_personagem', 'classe', 'raca', 'antecedente', 'atributos', 'pericias']
    if not all(k in dados for k in campos_obrigatorios):
        return jsonify({'mensagem': 'Dados da ficha incompletos'}), 400
    sucesso = criar_nova_ficha(
        current_user_id, 
        dados['nome_personagem'], 
        dados['classe'], 
        dados['raca'], 
        dados['antecedente'], 
        dados['atributos'], 
        dados['pericias']
    )
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada com sucesso!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar a ficha'}), 500

@app.route("/api/fichas/<int:id>", methods=['GET'])
@token_required
def get_ficha_unica(current_user_id, id):
    """(READ) Busca e retorna os detalhes de uma única ficha para a página de edição."""
    ficha = buscar_ficha_por_id(id, current_user_id)
    if ficha:
        if ficha.get('atributos_json'): ficha['atributos'] = json.loads(ficha['atributos_json'])
        if ficha.get('pericias_json'): ficha['pericias'] = json.loads(ficha['pericias_json'])
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

# --- Rotas de Salas (Protegidas) ---
@app.route("/api/salas", methods=['GET'])
@token_required
def get_salas(current_user_id):
    """Busca e retorna a lista de todas as salas de campanha disponíveis."""
    salas = listar_salas_disponiveis()
    return jsonify(salas)

@app.route("/api/salas", methods=['POST'])
@token_required
def post_nova_sala(current_user_id):
    """Cria uma nova sala de campanha."""
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
    """Verifica se a senha fornecida para uma sala é válida."""
    dados = request.get_json()
    if not dados or 'sala_id' not in dados or 'senha' not in dados:
        return jsonify({'sucesso': False, 'mensagem': 'Dados incompletos.'}), 400
    senha_valida = verificar_senha_da_sala(dados['sala_id'], dados['senha'])
    return jsonify({'sucesso': senha_valida, 'mensagem': 'Senha da sala incorreta.' if not senha_valida else ''})

# --- Rotas de Anotações (Protegidas) ---
@app.route("/api/salas/<int:sala_id>/anotacoes", methods=['GET'])
@token_required
def get_anotacoes(current_user_id, sala_id):
    """Busca as anotações pessoais do jogador para esta sala."""
    notas = buscar_anotacoes(current_user_id, sala_id)
    return jsonify({'notas': notas})

@app.route("/api/salas/<int:sala_id>/anotacoes", methods=['PUT'])
@token_required
def put_anotacoes(current_user_id, sala_id):
    """Salva ou atualiza as anotações pessoais do jogador."""
    dados = request.get_json()
    if 'notas' not in dados:
        return jsonify({'mensagem': 'Dados de anotações ausentes'}), 400
    sucesso = salvar_anotacoes(current_user_id, sala_id, dados['notas'])
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Anotações salvas!'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao salvar anotações.'}), 500

# --- Rotas de Inventário de Sala (Protegidas) ---
@app.route("/api/salas/<int:sala_id>/inventario", methods=['GET'])
@token_required
def get_inventario_sala(current_user_id, sala_id):
    """Busca o inventário de um personagem (baseado na ficha) para esta sala."""
    ficha_id = request.args.get('ficha_id')
    if not ficha_id:
        return jsonify({'mensagem': 'ID da Ficha ausente na requisição'}), 400
    ficha_valida = buscar_dados_essenciais_ficha(ficha_id, current_user_id)
    if not ficha_valida:
        return jsonify({'mensagem': 'Permissão negada: esta ficha não é sua.'}), 403
    itens = buscar_inventario_sala(ficha_id, sala_id)
    return jsonify(itens)

@app.route("/api/salas/<int:sala_id>/inventario", methods=['POST'])
@token_required
def post_item_sala(current_user_id, sala_id):
    """Adiciona um item ao inventário de um personagem na sala."""
    dados = request.get_json()
    if not dados or 'ficha_id' not in dados or 'nome_item' not in dados:
        return jsonify({'mensagem': 'Dados do item incompletos'}), 400
    ficha_valida = buscar_dados_essenciais_ficha(dados['ficha_id'], current_user_id)
    if not ficha_valida:
        return jsonify({'mensagem': 'Permissão negada.'}), 403
    sucesso = adicionar_item_sala(dados['ficha_id'], sala_id, dados['nome_item'], dados.get('descricao', ''))
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item adicionado ao inventário!'}), 201
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao adicionar item.'}), 500

@app.route("/api/inventario-sala/<int:item_id>", methods=['DELETE'])
@token_required
def delete_item_sala(current_user_id, item_id):
    """Apaga um item do inventário da sala."""
    dados = request.get_json()
    ficha_id = dados.get('ficha_id')
    if not ficha_id:
        return jsonify({'mensagem': 'ID da Ficha ausente.'}), 400
    ficha_valida = buscar_dados_essenciais_ficha(ficha_id, current_user_id)
    if not ficha_valida:
        return jsonify({'mensagem': 'Permissão negada.'}), 403
    sucesso = apagar_item_sala(item_id, ficha_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item descartado.'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao descartar item.'}), 404

# --- EVENTOS SOCKET.IO ---

salas_ativas = {}

@socketio.on('connect')
def handle_connect():
    """Chamado automaticamente quando um cliente estabelece uma conexão WebSocket."""
    print(f"Cliente conectado! SID: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    """Chamado quando um cliente se desconecta."""
    print(f"Cliente desconectado! SID: {request.sid}")
    sala_para_remover = None
    jogador_removido = None
    for sala_id, jogadores in salas_ativas.items():
        if request.sid in jogadores:
            sala_para_remover = str(sala_id)
            jogador_removido = jogadores.pop(request.sid)
            break
    if sala_para_remover and jogador_removido:
        nome_personagem = jogador_removido['nome_personagem']
        socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_para_remover].values()), to=sala_para_remover)
        mensagem_saida = f"--- {nome_personagem} saiu da taverna. ---"
        send(mensagem_saida, to=sala_para_remover)
        salvar_mensagem_chat(sala_para_remover, 'Sistema', mensagem_saida)

@socketio.on('join_room')
def handle_join_room(data):
    """Evento para um usuário entrar em uma sala de campanha."""
    token = data.get('token'); sala_id = str(data.get('sala_id')); ficha_id = data.get('ficha_id')
    if not token or not sala_id:
        send({'error': 'Token ou ID da sala ausente.'}); return
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        mestre_id = buscar_mestre_da_sala(sala_id)
        is_mestre = (user_id == mestre_id)
        if sala_id not in salas_ativas:
            salas_ativas[sala_id] = {}
        if is_mestre:
            mestre_existente = any(j['role'] == 'mestre' for j in salas_ativas[sala_id].values())
            if mestre_existente:
                socketio.emit('join_error', {'mensagem': 'Já existe um Mestre ativo nesta sala.'}, room=request.sid)
                return
            nome_personagem = user_data['name']
            ficha_id_real = None
        else:
            if not ficha_id:
                send({'error': 'Jogador deve selecionar uma ficha.'}); return
            ficha_data = buscar_dados_essenciais_ficha(ficha_id, user_id)
            if not ficha_data:
                send({'error': 'Ficha não encontrada ou não pertence a você.'}); return
            nome_personagem = ficha_data['nome_personagem']
            ficha_id_real = ficha_id
        join_room(sala_id)
        salas_ativas[sala_id][request.sid] = {
            'user_id': user_id,
            'ficha_id': ficha_id_real,
            'nome_personagem': nome_personagem,
            'role': 'mestre' if is_mestre else 'player'
        }
        socketio.emit('status_mestre', {'isMestre': is_mestre}, room=request.sid)
        historico = buscar_historico_chat(sala_id)
        socketio.emit('chat_history', {'historico': historico}, room=request.sid)
        remetente_entrada = f"Mestre ({nome_personagem})" if is_mestre else nome_personagem
        mensagem_entrada = f"--- {remetente_entrada} entrou na taverna! ---"
        send(mensagem_entrada, to=sala_id)
        salvar_mensagem_chat(sala_id, 'Sistema', f"{remetente_entrada} entrou na taverna!")
        socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_id].values()), to=sala_id)
        print(f"{remetente_entrada} (User ID: {user_id}) entrou na sala {sala_id}")
    except Exception as e:
        print(f"Falha na autenticação do socket: {e}"); send({'error': 'Autenticação falhou.'})

@socketio.on('send_message')
def handle_send_message(data):
    """Ouve por mensagens de chat e as retransmite para a sala (e salva no DB)."""
    token = data.get('token'); sala_id = str(data.get('sala_id')); message_text = data.get('message')
    if not all([token, sala_id, message_text]):
        send({'error': 'Dados da mensagem incompletos.'}); return
    try:
        jogador = salas_ativas[sala_id][request.sid]
        nome_personagem = jogador['nome_personagem']
        remetente = f"[Mestre] {nome_personagem}" if jogador['role'] == 'mestre' else nome_personagem
        salvar_mensagem_chat(sala_id, remetente, message_text)
        formatted_message = f"[{remetente}]: {message_text}"
        send(formatted_message, to=sala_id)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}"); send({'error': 'Erro ao enviar mensagem.'})

@socketio.on('roll_dice')
def handle_roll_dice(data):
    """Ouve por rolagens de dados e as retransmite para a sala (e salva no DB)."""
    token = data.get('token'); sala_id = str(data.get('sala_id')); dice_command = data.get('command')
    if not all([token, sala_id, dice_command]):
        send({'error': 'Dados da rolagem incompletos.'}); return
    try:
        jogador = salas_ativas[sala_id][request.sid]
        nome_personagem = jogador['nome_personagem']
        remetente = f"[Mestre] {nome_personagem}" if jogador['role'] == 'mestre' else nome_personagem
        total, rolagens = rolar_dados(dice_command)
        resultado_str = f"{total} ({', '.join(map(str, rolagens))})" if len(rolagens) > 1 else str(total)
        mensagem = f"🎲 [{remetente}] rolou {dice_command} e tirou: {resultado_str}"
        log_message = f"[{remetente}] rolou {dice_command} e tirou: {resultado_str}"
        salvar_mensagem_chat(sala_id, 'Sistema', log_message)
        send(mensagem, to=sala_id)
    except Exception as e:
        print(f"Erro ao rolar dados: {e}"); send({'error': 'Erro ao rolar dados.'})

@socketio.on('mestre_dar_xp')
def handle_dar_xp(data):
    """Ouve o comando do Mestre para distribuir XP."""
    token = data.get('token'); sala_id = str(data.get('sala_id')); alvo_id = data.get('alvo_id'); quantidade = data.get('quantidade')
    if not all([token, sala_id, alvo_id, quantidade]):
        send({'error': 'Dados de XP incompletos.'}); return
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        mestre_id = buscar_mestre_da_sala(sala_id)
        if user_id != mestre_id:
            send({'error': 'Apenas o Mestre pode distribuir XP.'}, room=request.sid); return
        quantidade_xp = int(quantidade)
        fichas_para_atualizar_ids = []
        if alvo_id == 'all':
            jogadores_na_sala = salas_ativas.get(sala_id, {}).values()
            fichas_para_atualizar_ids = [j['ficha_id'] for j in jogadores_na_sala if j['role'] == 'player']
        else:
            fichas_para_atualizar_ids = [int(alvo_id)]
        for ficha_id in fichas_para_atualizar_ids:
            if not ficha_id: continue
            ficha_atualizada = adicionar_xp_e_upar(ficha_id, quantidade_xp)
            if ficha_atualizada:
                ficha_atualizada['atributos'] = json.loads(ficha_atualizada['atributos_json'])
                ficha_atualizada['pericias'] = json.loads(ficha_atualizada['pericias_json'])
                socketio.emit('ficha_atualizada', ficha_atualizada, to=sala_id)
                nome_alvo = ficha_atualizada['nome_personagem']
                mensagem_xp = f"--- {nome_alvo} recebe {quantidade_xp} pontos de experiência! ---"
                salvar_mensagem_chat(sala_id, 'Sistema', mensagem_xp)
                send(mensagem_xp, to=sala_id)
                if ficha_atualizada.get('subiu_de_nivel', False):
                    mensagem_lvl = f"🎉🎉🎉 PARABÉNS! {nome_alvo} subiu para o nível {ficha_atualizada['nivel']}! 🎉🎉🎉"
                    salvar_mensagem_chat(sala_id, 'Sistema', mensagem_lvl)
                    send(mensagem_lvl, to=sala_id)
                    print(f"Ficha {ficha_id} subiu de nível!")
            else:
                send({'error': f'Não foi possível dar XP para a ficha {ficha_id}.'}, room=request.sid)
    except Exception as e:
        print(f"Erro ao processar XP: {e}")
        send({'error': 'Token inválido ou erro ao dar XP.'})

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    print("Iniciando o servidor (modo __main__)...")
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)