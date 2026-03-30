# servidor/servidor_api.py

print("--- LOADING servidor_api.py - VERSION 3 ---")

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
from ..logging_config import log_conexao, log_evento_socket, log_batalha, log_erro, log_debug
# --- IMPORTS DE MÓDulos INTERNOS ---
# (Verificando se todas as funções usadas estão importadas)
from ..database.db_manager import (
    buscar_todos_os_itens, 
    buscar_todos_os_monstros,
    buscar_monstro_por_id,
    buscar_tipos_monstros,
    buscar_item_por_id,
    buscar_categorias_itens,
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
    buscar_mestre_da_sala,      # <- Usada em handle_join_room e handle_dar_xp
    apagar_sala,
    transferir_mestre_sala,
    banir_usuario_sala,
    verificar_banido
)
from ..core.rolador_de_dados import rolar_dados
from ..database import esconderijo_db

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
CORS(app, 
     resources={r"/api/*": {"origins": ["http://localhost:5173", "http://localhost:5174"]}}, 
     allow_headers=["Content-Type", "x-access-token"],
     supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- DECORATOR DE AUTENTICAÇÃO JWT ---
def token_required(f):
    """Verifica se o token JWT é válido antes de permitir acesso à rota."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Adicionado para lidar com requisições preflight do CORS
        if request.method == 'OPTIONS':
            return '', 204
            
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
    """Retorna monstros com filtros opcionais: ?nome=&oficial=&tipo=&criador_id="""
    nome      = request.args.get('nome', None)
    oficial   = request.args.get('oficial', None)
    tipo      = request.args.get('tipo', None)
    criador_id = request.args.get('criador_id', None)
    if oficial is not None:
        oficial = 1 if oficial == '1' else 0
    monstros = buscar_todos_os_monstros(nome=nome, oficial=oficial, tipo=tipo, criador_id=criador_id)
    return jsonify(monstros)

@app.route("/api/monstros/tipos", methods=['GET'])
def get_tipos_monstros():
    """Retorna lista de tipos únicos para o filtro."""
    return jsonify(buscar_tipos_monstros())

@app.route("/api/monstros/<int:monstro_id>", methods=['GET'])
def get_monstro_detalhe(monstro_id):
    """Retorna um monstro completo por ID."""
    m = buscar_monstro_por_id(monstro_id)
    if not m:
        return jsonify({'erro': 'Monstro não encontrado'}), 404
    return jsonify(m)

@app.route("/api/itens", methods=['GET'])
def get_itens():
    """Retorna itens com filtros: ?nome=&categoria=&oficial="""
    nome      = request.args.get('nome', None)
    categoria = request.args.get('categoria', None)
    oficial   = request.args.get('oficial', None)
    criador_id = request.args.get('criador_id', None)
    if oficial is not None:
        oficial = 1 if oficial == '1' else 0
    itens = buscar_todos_os_itens(nome=nome, categoria=categoria, oficial=oficial, criador_id=criador_id)
    return jsonify(itens)

@app.route("/api/itens/categorias", methods=['GET'])
def get_categorias_itens():
    return jsonify(buscar_categorias_itens())

@app.route("/api/itens/<int:item_id>", methods=['GET'])
def get_item_detalhe(item_id):
    item = buscar_item_por_id(item_id)
    if not item:
        return jsonify({'erro': 'Item não encontrado'}), 404
    return jsonify(item)

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

def _check_campanha_owner(campanha_id, user_id):
    campanha = esconderijo_db.buscar_campanha(campanha_id)
    if not campanha:
        return None, (jsonify({'sucesso': False, 'mensagem': 'Campanha não encontrada.'}), 404)
    if campanha['criador_id'] != user_id:
        return None, (jsonify({'sucesso': False, 'mensagem': 'Acesso negado.'}), 403)
    return campanha, None

@app.route('/api/campanhas', methods=['GET'])
@token_required
def listar_campanhas(current_user_id):
    campanhas = esconderijo_db.listar_campanhas(current_user_id)
    return jsonify(campanhas)

@app.route('/api/campanhas/<int:campanha_id>', methods=['GET'])
@token_required
def buscar_campanha_route(current_user_data, campanha_id):
    user_id = int(current_user_data['sub'])
    campanha, err = _check_campanha_owner(campanha_id, user_id)
    if err: return err
    return jsonify(campanha)

@app.route('/api/campanhas', methods=['POST'])
@token_required
def criar_campanha_route(current_user_id):
    dados = request.get_json() or {}
    try:
        campanha = esconderijo_db.criar_campanha(current_user_id, dados)
        return jsonify({'sucesso': True, 'campanha': campanha}), 201
    except Exception as e:
        print(f'Erro ao criar campanha: {e}')
        return jsonify({'sucesso': False, 'mensagem': 'Erro interno no servidor.'}), 500

@app.route('/api/campanhas/<int:campanha_id>', methods=['PUT'])
@token_required
def atualizar_campanha_route(current_user_data, campanha_id):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(campanha_id, user_id)
    if err: return err
    dados = request.get_json() or {}
    campanha = esconderijo_db.atualizar_campanha(campanha_id, user_id, dados)
    if not campanha:
        return jsonify({'sucesso': False, 'mensagem': 'Campanha não encontrada ou não atualizada.'}), 404
    return jsonify({'sucesso': True, 'campanha': campanha})

@app.route('/api/campanhas/<int:campanha_id>', methods=['DELETE'])
@token_required
def deletar_campanha_route(current_user_data, campanha_id):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(campanha_id, user_id)
    if err: return err
    sucesso = esconderijo_db.deletar_campanha(campanha_id, user_id)
    if not sucesso:
        return jsonify({'sucesso': False, 'mensagem': 'Campanha não encontrada.'}), 404
    return jsonify({'sucesso': True, 'mensagem': 'Campanha deletada.'})

# Subrecursos genericos
def _rota_listar(campanha_id, fetch_fn, current_user_data):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(campanha_id, user_id)
    if err: return err
    return jsonify(fetch_fn(campanha_id))

# mapas
@app.route('/api/campanhas/<int:cid>/mapas', methods=['GET'])
@token_required
def listar_mapas_route(current_user_data, cid):
    return _rota_listar(cid, esconderijo_db.listar_mapas, current_user_data)

@app.route('/api/campanhas/<int:cid>/mapas', methods=['POST'])
@token_required
def criar_mapa_route(current_user_data, cid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    mapa = esconderijo_db.criar_mapa(cid, dados)
    return jsonify({'sucesso': True, 'mapa': mapa}), 201

@app.route('/api/campanhas/<int:cid>/mapas/<int:mid>', methods=['PUT'])
@token_required
def atualizar_mapa_route(current_user_data, cid, mid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    mapa = esconderijo_db.atualizar_mapa(mid, dados)
    if not mapa:
        return jsonify({'sucesso': False, 'mensagem': 'Mapa não encontrado.'}), 404
    return jsonify({'sucesso': True, 'mapa': mapa})

@app.route('/api/campanhas/<int:cid>/mapas/<int:mid>', methods=['DELETE'])
@token_required
def deletar_mapa_route(current_user_data, cid, mid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    if not esconderijo_db.deletar_mapa(mid, cid):
        return jsonify({'sucesso': False, 'mensagem': 'Mapa não encontrado.'}), 404
    return jsonify({'sucesso': True})

@app.route('/api/campanhas/<int:cid>/mapas/<int:mid>/toggle', methods=['PATCH'])
@token_required
def toggle_mapa_route(current_user_data, cid, mid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    data = request.get_json() or {}
    visivel = bool(data.get('visivel', 0))
    mapa = esconderijo_db.toggle_mapa(mid, visivel)
    return jsonify({'sucesso': True, 'mapa': mapa})

# eventos
@app.route('/api/campanhas/<int:cid>/eventos', methods=['GET'])
@token_required
def listar_eventos_route(current_user_data, cid):
    return _rota_listar(cid, esconderijo_db.listar_eventos, current_user_data)

@app.route('/api/campanhas/<int:cid>/eventos', methods=['POST'])
@token_required
def criar_evento_route(current_user_data, cid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    evento = esconderijo_db.criar_evento(cid, dados)
    return jsonify({'sucesso': True, 'evento': evento}), 201

@app.route('/api/campanhas/<int:cid>/eventos/<int:eid>', methods=['PUT'])
@token_required
def atualizar_evento_route(current_user_data, cid, eid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    evento = esconderijo_db.atualizar_evento(eid, dados)
    if not evento:
        return jsonify({'sucesso': False, 'mensagem': 'Evento não encontrado.'}), 404
    return jsonify({'sucesso': True, 'evento': evento})

@app.route('/api/campanhas/<int:cid>/eventos/<int:eid>', methods=['DELETE'])
@token_required
def deletar_evento_route(current_user_data, cid, eid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    if not esconderijo_db.deletar_evento(eid, cid):
        return jsonify({'sucesso': False, 'mensagem': 'Evento não encontrado.'}), 404
    return jsonify({'sucesso': True})

@app.route('/api/campanhas/<int:cid>/eventos/<int:eid>/toggle', methods=['PATCH'])
@token_required
def toggle_evento_route(current_user_data, cid, eid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    data = request.get_json() or {}
    visivel = bool(data.get('visivel', 0))
    evento = esconderijo_db.toggle_evento(eid, visivel)
    return jsonify({'sucesso': True, 'evento': evento})

# npcs
@app.route('/api/campanhas/<int:cid>/npcs', methods=['GET'])
@token_required
def listar_npcs_route(current_user_data, cid):
    return _rota_listar(cid, esconderijo_db.listar_npcs, current_user_data)

@app.route('/api/campanhas/<int:cid>/npcs', methods=['POST'])
@token_required
def criar_npc_route(current_user_data, cid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    npc = esconderijo_db.criar_npc(cid, dados)
    return jsonify({'sucesso': True, 'npc': npc}), 201

@app.route('/api/campanhas/<int:cid>/npcs/<int:nid>', methods=['PUT'])
@token_required
def atualizar_npc_route(current_user_data, cid, nid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    npc = esconderijo_db.atualizar_npc(nid, dados)
    if not npc:
        return jsonify({'sucesso': False, 'mensagem': 'NPC não encontrado.'}), 404
    return jsonify({'sucesso': True, 'npc': npc})

@app.route('/api/campanhas/<int:cid>/npcs/<int:nid>', methods=['DELETE'])
@token_required
def deletar_npc_route(current_user_data, cid, nid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    if not esconderijo_db.deletar_npc(nid, cid):
        return jsonify({'sucesso': False, 'mensagem': 'NPC não encontrado.'}), 404
    return jsonify({'sucesso': True})

@app.route('/api/campanhas/<int:cid>/npcs/<int:nid>/toggle', methods=['PATCH'])
@token_required
def toggle_npc_route(current_user_data, cid, nid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    data = request.get_json() or {}
    visivel = bool(data.get('visivel', 0))
    npc = esconderijo_db.toggle_npc(nid, visivel)
    return jsonify({'sucesso': True, 'npc': npc})

# quests
@app.route('/api/campanhas/<int:cid>/quests', methods=['GET'])
@token_required
def listar_quests_route(current_user_data, cid):
    return _rota_listar(cid, esconderijo_db.listar_quests, current_user_data)

@app.route('/api/campanhas/<int:cid>/quests', methods=['POST'])
@token_required
def criar_quest_route(current_user_data, cid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    quest = esconderijo_db.criar_quest(cid, dados)
    return jsonify({'sucesso': True, 'quest': quest}), 201

@app.route('/api/campanhas/<int:cid>/quests/<int:qid>', methods=['PUT'])
@token_required
def atualizar_quest_route(current_user_data, cid, qid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    quest = esconderijo_db.atualizar_quest(qid, dados)
    if not quest:
        return jsonify({'sucesso': False, 'mensagem': 'Quest não encontrada.'}), 404
    return jsonify({'sucesso': True, 'quest': quest})

@app.route('/api/campanhas/<int:cid>/quests/<int:qid>', methods=['DELETE'])
@token_required
def deletar_quest_route(current_user_data, cid, qid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    if not esconderijo_db.deletar_quest(qid, cid):
        return jsonify({'sucesso': False, 'mensagem': 'Quest não encontrada.'}), 404
    return jsonify({'sucesso': True})

@app.route('/api/campanhas/<int:cid>/quests/<int:qid>/toggle', methods=['PATCH'])
@token_required
def toggle_quest_route(current_user_data, cid, qid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    data = request.get_json() or {}
    visivel = bool(data.get('visivel', 0))
    quest = esconderijo_db.toggle_quest(qid, visivel)
    return jsonify({'sucesso': True, 'quest': quest})

# anotacoes
@app.route('/api/campanhas/<int:cid>/anotacoes', methods=['GET'])
@token_required
def listar_anotacoes_route(current_user_data, cid):
    return _rota_listar(cid, esconderijo_db.listar_anotacoes, current_user_data)

@app.route('/api/campanhas/<int:cid>/anotacoes', methods=['POST'])
@token_required
def criar_anotacao_route(current_user_data, cid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    anotacao = esconderijo_db.criar_anotacao(cid, dados)
    return jsonify({'sucesso': True, 'anotacao': anotacao}), 201

@app.route('/api/campanhas/<int:cid>/anotacoes/<int:aid>', methods=['PUT'])
@token_required
def atualizar_anotacao_route(current_user_data, cid, aid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    dados = request.get_json() or {}
    anotacao = esconderijo_db.atualizar_anotacao(aid, dados)
    if not anotacao:
        return jsonify({'sucesso': False, 'mensagem': 'Anotação não encontrada.'}), 404
    return jsonify({'sucesso': True, 'anotacao': anotacao})

@app.route('/api/campanhas/<int:cid>/anotacoes/<int:aid>', methods=['DELETE'])
@token_required
def deletar_anotacao_route(current_user_data, cid, aid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    if not esconderijo_db.deletar_anotacao(aid, cid):
        return jsonify({'sucesso': False, 'mensagem': 'Anotação não encontrada.'}), 404
    return jsonify({'sucesso': True})

@app.route('/api/campanhas/<int:cid>/anotacoes/<int:aid>/toggle', methods=['PATCH'])
@token_required
def toggle_anotacao_route(current_user_data, cid, aid):
    user_id = int(current_user_data['sub'])
    _, err = _check_campanha_owner(cid, user_id)
    if err: return err
    data = request.get_json() or {}
    visivel = bool(data.get('visivel', 0))
    anotacao = esconderijo_db.toggle_anotacao(aid, visivel)
    return jsonify({'sucesso': True, 'anotacao': anotacao})

# sala/campanha
@app.route('/api/salas/<int:sala_id>/campanha', methods=['GET'])
@token_required
def buscar_campanha_sala_route(current_user_data, sala_id):
    campanha = esconderijo_db.buscar_campanha_da_sala(sala_id)
    if not campanha:
        return jsonify({'sucesso': False, 'mensagem': 'Nenhuma campanha vinculada à sala.'}), 404
    return jsonify(campanha)

@app.route('/api/salas/<int:sala_id>/campanha', methods=['POST'])
@token_required
def vincular_campanha_sala_route(current_user_data, sala_id):
    user_id = int(current_user_data['sub'])
    dados = request.get_json() or {}
    campanha_id = dados.get('campanha_id')
    if not campanha_id:
        return jsonify({'sucesso': False, 'mensagem': 'campanha_id é obrigatório.'}), 400
    campanha, err = _check_campanha_owner(campanha_id, user_id)
    if err: return err
    esconderijo_db.vincular_sala_campanha(sala_id, campanha_id)
    return jsonify({'sucesso': True})

# --- CRUD de Monstros (POST, PUT, DELETE) ---
@app.route("/api/monstros", methods=['POST'])
@token_required
def post_novo_monstro(current_user_data):
    """(CREATE) Cria um novo monstro customizado (qualquer usuário logado)."""
    user_id = int(current_user_data['sub'])
    dados = request.get_json()
    if not dados or not dados.get('nome'):
        return jsonify({'sucesso': False, 'mensagem': 'Nome é obrigatório.'}), 400
    dados['criador_id'] = user_id
    dados['oficial'] = 0
    try:
        novo_monstro = criar_novo_monstro(dados)
        if novo_monstro: return jsonify({'sucesso': True, 'monstro': novo_monstro}), 201
        else: return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar monstro (nome já existe?).'}), 409
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


@app.route("/api/salas/<int:sala_id>", methods=['DELETE'])
@token_required
def delete_sala(current_user_id, sala_id):
    """Apaga uma sala. Apenas o Mestre criador pode excluir."""
    sucesso = apagar_sala(sala_id, current_user_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Sala excluída com sucesso.'})
    else:
        return jsonify({'sucesso': False, 'mensagem': 'Sala não encontrada ou permissão negada.'}), 404

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
    log_conexao("Cliente conectado", sid=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    """Chamado quando um cliente se desconecta."""
    print(f"Cliente desconectado! SID: {request.sid}")
    log_conexao("Cliente desconectado", sid=request.sid)
    
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
        if mestre_id_da_sala is None:
             socketio.emit('join_error', {'mensagem': 'Sala não encontrada.'}, room=request.sid)
             return
        
        # Verificar se o usuário está banido
        if verificar_banido(sala_id, user_id):
            socketio.emit('join_error', {
                'mensagem': 'banido',
                'texto': 'Você foi banido, sua aventura terminou por aqui, inicie uma nova aventura!'
            }, room=request.sid)
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
    # Bloquear jogador morto
    if sala_id and str(sala_id) in batalhas_ativas:
        b = batalhas_ativas[str(sala_id)]
        sid = request.sid
        for j in b['jogadores']:
            if j.get('sid') == sid and j['status'] == 'morto':
                socketio.emit('acao_bloqueada', {'motivo': 'Você está morto e não pode agir.'}, room=sid)
                return
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


@socketio.on('mestre_passar_coroa')
def handle_passar_coroa(data):
    """Mestre transfere seu cargo para outro jogador da sala."""
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    alvo_ficha_id = data.get('alvo_ficha_id')  # ficha_id do novo mestre

    if not all([token, sala_id, alvo_ficha_id]):
        socketio.emit('mestre_error', {'mensagem': 'Dados incompletos.'}, room=request.sid)
        return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        mestre_id_da_sala = buscar_mestre_da_sala(sala_id)

        if user_id != mestre_id_da_sala:
            socketio.emit('mestre_error', {'mensagem': 'Apenas o Mestre atual pode passar a coroa.'}, room=request.sid)
            return

        # Encontrar o SID e user_id do alvo pelo ficha_id
        alvo_info = None
        alvo_sid = None
        if sala_id in salas_ativas:
            for sid, info in salas_ativas[sala_id].items():
                if str(info.get('ficha_id')) == str(alvo_ficha_id):
                    alvo_info = info
                    alvo_sid = sid
                    break

        if not alvo_info or not alvo_sid:
            socketio.emit('mestre_error', {'mensagem': 'Jogador alvo não encontrado na sala.'}, room=request.sid)
            return

        novo_mestre_user_id = alvo_info['user_id']
        nome_novo_mestre = alvo_info['nome_personagem']
        nome_mestre_atual = salas_ativas[sala_id][request.sid]['nome_personagem']

        # Atualizar no banco
        sucesso = transferir_mestre_sala(sala_id, novo_mestre_user_id)
        if not sucesso:
            socketio.emit('mestre_error', {'mensagem': 'Erro ao transferir no banco.'}, room=request.sid)
            return

        # Atualizar dicionário salas_ativas
        salas_ativas[sala_id][request.sid]['role'] = 'player'
        salas_ativas[sala_id][alvo_sid]['role'] = 'mestre'
        salas_ativas[sala_id][alvo_sid]['ficha_id'] = None

        # Notificar individualmente cada um
        socketio.emit('status_mestre', {'isMestre': False}, room=request.sid)
        socketio.emit('status_mestre', {'isMestre': True}, room=alvo_sid)

        # Anunciar na sala
        msg = f"--- 👑 {nome_mestre_atual} passou a coroa de Mestre para {nome_novo_mestre}! ---"
        salvar_mensagem_chat(sala_id, 'Sistema', msg)
        send(msg, to=sala_id)

        # Atualizar lista de jogadores
        socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_id].values()), to=sala_id)

    except Exception as e:
        print(f"Erro em handle_passar_coroa: {e}")
        socketio.emit('mestre_error', {'mensagem': f'Erro: {e}'}, room=request.sid)


@socketio.on('mestre_dar_item')
def handle_dar_item(data):
    """Mestre dá um item (da Ferraria Arcana) para o inventário de um jogador."""
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    alvo_ficha_id = data.get('alvo_ficha_id')
    nome_item = data.get('nome_item')
    descricao_item = data.get('descricao_item', '')

    if not all([token, sala_id, alvo_ficha_id, nome_item]):
        socketio.emit('mestre_error', {'mensagem': 'Dados incompletos para dar item.'}, room=request.sid)
        return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        mestre_id_da_sala = buscar_mestre_da_sala(sala_id)

        if user_id != mestre_id_da_sala:
            socketio.emit('mestre_error', {'mensagem': 'Apenas o Mestre pode dar itens.'}, room=request.sid)
            return

        sucesso = adicionar_item_sala(alvo_ficha_id, sala_id, nome_item, descricao_item)
        if not sucesso:
            socketio.emit('mestre_error', {'mensagem': 'Erro ao adicionar item no inventário.'}, room=request.sid)
            return

        # Descobrir nome do personagem alvo
        nome_alvo = 'Jogador'
        if sala_id in salas_ativas:
            for sid, info in salas_ativas[sala_id].items():
                if str(info.get('ficha_id')) == str(alvo_ficha_id):
                    nome_alvo = info['nome_personagem']
                    # Notificar o jogador para atualizar inventário
                    socketio.emit('inventario_atualizado', {}, room=sid)
                    break

        msg = f"--- 🎁 {nome_alvo} recebeu o item: {nome_item}! ---"
        salvar_mensagem_chat(sala_id, 'Sistema', msg)
        send(msg, to=sala_id)

        socketio.emit('mestre_feedback', {'mensagem': f'Item "{nome_item}" dado com sucesso!'}, room=request.sid)

    except Exception as e:
        print(f"Erro em handle_dar_item: {e}")
        socketio.emit('mestre_error', {'mensagem': f'Erro: {e}'}, room=request.sid)



@socketio.on('mestre_kickar')
def handle_kickar(data):
    """Mestre expulsa um jogador da sala temporariamente."""
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    alvo_ficha_id = str(data.get('alvo_ficha_id'))

    if not all([token, sala_id, alvo_ficha_id]):
        return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id):
            return

        # Encontrar SID do alvo
        alvo_sid = None
        alvo_nome = 'Jogador'
        if sala_id in salas_ativas:
            for sid, info in salas_ativas[sala_id].items():
                if str(info.get('ficha_id')) == alvo_ficha_id:
                    alvo_sid = sid
                    alvo_nome = info['nome_personagem']
                    break

        if not alvo_sid:
            socketio.emit('mestre_error', {'mensagem': 'Jogador não encontrado.'}, room=request.sid)
            return

        # Notificar o jogador que foi expulso
        socketio.emit('kick_ban', {
            'tipo': 'kick',
            'mensagem': 'Você foi expulso da sala, comporte-se da próxima vez!'
        }, room=alvo_sid)

        # Remover do dicionário de salas
        if sala_id in salas_ativas and alvo_sid in salas_ativas[sala_id]:
            salas_ativas[sala_id].pop(alvo_sid)

        # Anunciar na sala
        msg = f"--- ⚡ {alvo_nome} foi expulso da sala pelo Mestre. ---"
        salvar_mensagem_chat(sala_id, 'Sistema', msg)
        send(msg, to=sala_id)
        socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_id].values()), to=sala_id)

    except Exception as e:
        print(f"Erro em handle_kickar: {e}")


@socketio.on('mestre_banir')
def handle_banir(data):
    """Mestre bane permanentemente um jogador da sala."""
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    alvo_ficha_id = str(data.get('alvo_ficha_id'))

    if not all([token, sala_id, alvo_ficha_id]):
        return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id):
            return

        # Encontrar SID e user_id do alvo
        alvo_sid = None
        alvo_nome = 'Jogador'
        alvo_user_id = None
        if sala_id in salas_ativas:
            for sid, info in salas_ativas[sala_id].items():
                if str(info.get('ficha_id')) == alvo_ficha_id:
                    alvo_sid = sid
                    alvo_nome = info['nome_personagem']
                    alvo_user_id = info['user_id']
                    break

        if not alvo_sid or not alvo_user_id:
            socketio.emit('mestre_error', {'mensagem': 'Jogador não encontrado.'}, room=request.sid)
            return

        # Registrar ban no banco
        banir_usuario_sala(sala_id, alvo_user_id)

        # Notificar o jogador banido
        socketio.emit('kick_ban', {
            'tipo': 'ban',
            'mensagem': 'Você foi banido, sua aventura terminou por aqui, inicie uma nova aventura!'
        }, room=alvo_sid)

        # Remover do dicionário
        if sala_id in salas_ativas and alvo_sid in salas_ativas[sala_id]:
            salas_ativas[sala_id].pop(alvo_sid)

        # Anunciar
        msg = f"--- 🔨 {alvo_nome} foi banido da sala pelo Mestre. ---"
        salvar_mensagem_chat(sala_id, 'Sistema', msg)
        send(msg, to=sala_id)
        socketio.emit('lista_jogadores_atualizada', list(salas_ativas[sala_id].values()), to=sala_id)

    except Exception as e:
        print(f"Erro em handle_banir: {e}")




# ============================================================
# SISTEMA DE BATALHA
# ============================================================
batalhas_ativas = {}  # { sala_id: { estado_da_batalha } }

@socketio.on('batalha_iniciar')
def handle_batalha_iniciar(data):
    """Mestre inicia uma batalha com monstros selecionados."""
    log_debug('batalha_iniciar', f'data recebido: {data}')
    token   = data.get('token')
    sala_id = str(data.get('sala_id')) if data.get('sala_id') is not None else 'NONE'
    monstros_ids = data.get('monstros_ids', [])  # lista de IDs do bestiário
    acoes_padrao = 1
    try:
        acoes_padrao = int(data.get('acoes_padrao', 1))
    except Exception as e:
        log_erro('batalha_iniciar', sala_id=sala_id, erro_msg=f'acoes_padrao invalid: {e}')
    acoes_individuais = data.get('acoes_individuais', {})  # { ficha_id: n_acoes }

    log_evento_socket('batalha_iniciar', sala_id, payload_resumo=f'monstros={monstros_ids}, acoes_padrao={acoes_padrao}, acoes_individuais={acoes_individuais}')

    if not token:
        log_erro('batalha_iniciar', sala_id=sala_id, erro_msg='Token ausente no payload')
        socketio.emit('batalha_erro', {'mensagem': 'Token ausente'}, room=request.sid)
        return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id):
            return

        # Montar lista de monstros com HP atual
        monstros = []
        for mid in monstros_ids:
            m = buscar_monstro_por_id(mid)
            if m:
                monstros.append({
                    'id': f"m_{mid}_{len(monstros)}",
                    'db_id': mid,
                    'nome': m['nome'],
                    'tipo': m.get('tipo',''),
                    'hp_max': m.get('vida_maxima', 10),
                    'hp_atual': m.get('vida_maxima', 10),
                    'ca': m.get('ca', m.get('defesa', 10)),
                    'status': 'vivo',  # vivo | derrotado | fugiu
                    'iniciativa': 0,
                })

        # Montar lista de jogadores
        jogadores = []
        if sala_id in salas_ativas:
            for sid, info in salas_ativas[sala_id].items():
                if info['role'] == 'player' and info.get('ficha_id'):
                    fid = str(info['ficha_id'])
                    jogadores.append({
                        'sid': sid,
                        'ficha_id': fid,
                        'nome': info['nome_personagem'],
                        'status': 'vivo',  # vivo | caido | morto
                        'hp_atual': 10,
                        'acoes_restantes': acoes_individuais.get(fid, acoes_padrao),
                        'acoes_max': acoes_individuais.get(fid, acoes_padrao),
                        'iniciativa': 0,
                    })
            # Mestre NÃO participa como combatente

        batalhas_ativas[sala_id] = {
            'fase': 'iniciativa',  # iniciativa | combate | encerrada
            'sub_fase': None,      # None | aguardando_d20_acerto | aguardando_dado_dano | aguardando_roll_dano
            'monstros': monstros,
            'jogadores': jogadores,
            'turno_ordem': [],
            'turno_atual': 0,
            'log': [],
            'acoes_padrao': acoes_padrao,
        }

        # Notificar toda a sala
        socketio.emit('batalha_iniciada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': batalhas_ativas[sala_id],
        }, to=sala_id)

        msg = "--- ⚔️ BATALHA INICIADA! Role iniciativa (1d20)! ---"
        send(msg, to=sala_id)
        salvar_mensagem_chat(sala_id, 'Sistema', msg)
        log_batalha('iniciativa', sala_id, f'Batalha iniciada por mestre {user_id}, {len(monstros)} monstros, {len(jogadores)} jogadores')

    except Exception as e:
        log_erro('batalha_iniciar', user_id=None, sala_id=sala_id, erro_msg=str(e))
        print(f"Erro batalha_iniciar: {e}")
        socketio.emit('batalha_erro', {'mensagem': str(e)}, room=request.sid)


def _batalha_publica(sala_id):
    """Retorna estado da batalha SEM HP dos monstros (para players)."""
    b = batalhas_ativas.get(sala_id)
    if not b: return None
    monstros_pub = []
    for m in b['monstros']:
        monstros_pub.append({
            'id': m['id'], 'nome': m['nome'], 'tipo': m['tipo'],
            'status': m['status'], 'ca': m['ca'],
            # HP escondido: só mostra se derrotado/fugiu
            'hp_oculto': m['status'] == 'vivo',
        })
    return {
        'fase': b['fase'],
        'sub_fase': b.get('sub_fase'),
        'dado_dano_atual': b.get('dado_dano_atual'),
        'alvo_dano_atual': b.get('alvo_dano_atual'),
        'd20_acerto_atual': b.get('d20_acerto_atual'),
        'monstros': monstros_pub,
        'jogadores': b['jogadores'],
        'turno_ordem': b['turno_ordem'],
        'turno_atual': b['turno_atual'],
        'log': b['log'],
    }


@socketio.on('batalha_set_iniciativa')
def handle_set_iniciativa(data):
    """Mestre registra iniciativa de um participante."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))
    pid     = data.get('pid')   # ficha_id ou id do monstro
    valor   = int(data.get('valor', 0))

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        for j in b['jogadores']:
            if j['ficha_id'] == str(pid):
                j['iniciativa'] = valor
        for m in b['monstros']:
            if m['id'] == pid:
                m['iniciativa'] = valor

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro set_iniciativa: {e}")


@socketio.on('batalha_comecar_combate')
def handle_comecar_combate(data):
    """Mestre confirma iniciativas e começa o combate."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]

        # Montar ordem por iniciativa (maior primeiro)
        participantes = []
        for j in b['jogadores']:
            participantes.append({'id': j['ficha_id'], 'nome': j['nome'], 'tipo': 'jogador', 'iniciativa': j['iniciativa']})
        for m in b['monstros']:
            if m['status'] == 'vivo':
                participantes.append({'id': m['id'], 'nome': m['nome'], 'tipo': 'monstro', 'iniciativa': m['iniciativa']})

        participantes.sort(key=lambda x: x['iniciativa'], reverse=True)
        b['turno_ordem'] = participantes
        b['turno_atual'] = 0
        b['fase'] = 'combate'

        # Resetar ações
        for j in b['jogadores']:
            j['acoes_restantes'] = j['acoes_max']

        log_entry = f"⚔️ Combate iniciado! Ordem: {' → '.join(p['nome'] for p in participantes)}"
        b['log'].append(log_entry)

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

        msg = f"--- {log_entry} ---"
        send(msg, to=sala_id)
        salvar_mensagem_chat(sala_id, 'Sistema', msg)

    except Exception as e:
        print(f"Erro comecar_combate: {e}")


@socketio.on('batalha_atacar')
def handle_atacar(data):
    """Registra um ataque (player ou monstro atacando alvo)."""
    token    = data.get('token')
    sala_id  = str(data.get('sala_id'))
    atacante_id = data.get('atacante_id')
    alvo_id  = data.get('alvo_id')
    dano     = int(data.get('dano', 0))
    rolagem  = data.get('rolagem', '')  # ex: "1d6+2 = 8"

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        is_mestre = (user_id == buscar_mestre_da_sala(sala_id))

        # Encontrar nomes
        nome_atacante = atacante_id
        nome_alvo = alvo_id

        for j in b['jogadores']:
            if j['ficha_id'] == str(atacante_id): nome_atacante = j['nome']
            if j['ficha_id'] == str(alvo_id):
                nome_alvo = j['nome']
                j['hp_atual'] = max(0, j['hp_atual'] - dano)
                if j['hp_atual'] == 0 and j['status'] == 'vivo':
                    j['status'] = 'caido'
                    b['log'].append(f"💀 {j['nome']} caiu em batalha!")

        for m in b['monstros']:
            if m['id'] == atacante_id: nome_atacante = m['nome']
            if m['id'] == alvo_id and is_mestre:
                nome_alvo = m['nome']
                m['hp_atual'] = max(0, m['hp_atual'] - dano)
                if m['hp_atual'] == 0 and m['status'] == 'vivo':
                    m['status'] = 'derrotado'
                    b['log'].append(f"💥 {m['nome']} foi derrotado!")
                    msg = f"--- 💥 {m['nome']} foi derrotado! ---"
                    send(msg, to=sala_id)
                    salvar_mensagem_chat(sala_id, 'Sistema', msg)

        log_entry = f"⚔️ {nome_atacante} atacou {nome_alvo}: {rolagem} ({dano} dano)"
        b['log'].append(log_entry)

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
            'efeito': {'tipo': 'ataque', 'atacante': atacante_id, 'alvo': alvo_id, 'dano': dano},
        }, to=sala_id)

    except Exception as e:
        print(f"Erro batalha_atacar: {e}")


@socketio.on('batalha_proximo_turno')
def handle_proximo_turno(data):
    """Avança para o próximo turno."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        ativos = [p for p in b['turno_ordem']
                  if not _esta_fora(p['id'], b)]

        if not ativos:
            return

        b['turno_atual'] = (b['turno_atual'] + 1) % len(ativos)

        # Resetar ações do participante atual
        atual = ativos[b['turno_atual']]
        for j in b['jogadores']:
            if j['ficha_id'] == atual['id']:
                j['acoes_restantes'] = j['acoes_max']

        b['sub_fase'] = None
        b['d20_acerto_atual'] = None
        b['dado_dano_atual'] = None
        b['alvo_dano_atual'] = None
        b['log'].append(f"🔄 Turno de {atual['nome']}")

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro proximo_turno: {e}")


def _esta_fora(pid, b):
    for j in b['jogadores']:
        if j['ficha_id'] == str(pid) and j['status'] in ('morto',):
            return True
    for m in b['monstros']:
        if m['id'] == pid and m['status'] != 'vivo':
            return True
    return False


@socketio.on('batalha_curar')
def handle_curar(data):
    """Mestre cura um jogador."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))
    alvo_id = str(data.get('alvo_id'))
    cura    = int(data.get('cura', 1))

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        for j in b['jogadores']:
            if j['ficha_id'] == alvo_id:
                if j['status'] == 'caido':
                    j['status'] = 'vivo'
                    j['hp_atual'] = max(1, cura)
                    b['log'].append(f"💚 {j['nome']} foi curado e levantou com {j['hp_atual']} HP!")
                else:
                    j['hp_atual'] += cura
                    b['log'].append(f"💚 {j['nome']} recebeu {cura} de cura (HP: {j['hp_atual']})")

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro batalha_curar: {e}")


@socketio.on('batalha_status_jogador')
def handle_status_jogador(data):
    """Mestre muda status de um jogador: caido | morto | vivo."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))
    alvo_id = str(data.get('alvo_id'))
    novo_status = data.get('status')  # caido | morto | vivo

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        for j in b['jogadores']:
            if j['ficha_id'] == alvo_id:
                j['status'] = novo_status
                if novo_status == 'morto':
                    b['log'].append(f"☠️ {j['nome']} morreu!")
                    # Notificar jogador específico que está morto
                    if j['sid']:
                        socketio.emit('jogador_morto', {}, room=j['sid'])
                elif novo_status == 'vivo':
                    j['hp_atual'] = max(1, j['hp_atual'])
                    b['log'].append(f"✨ {j['nome']} foi ressuscitado!")
                    if j['sid']:
                        socketio.emit('jogador_ressuscitado', {}, room=j['sid'])

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro status_jogador: {e}")


@socketio.on('batalha_status_monstro')
def handle_status_monstro(data):
    """Mestre declara monstro derrotado ou fugido."""
    token    = data.get('token')
    sala_id  = str(data.get('sala_id'))
    monstro_id = data.get('monstro_id')
    novo_status = data.get('status')  # derrotado | fugiu

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        for m in b['monstros']:
            if m['id'] == monstro_id:
                m['status'] = novo_status
                emoji = '💥' if novo_status == 'derrotado' else '💨'
                texto = 'foi derrotado' if novo_status == 'derrotado' else 'fugiu!'
                b['log'].append(f"{emoji} {m['nome']} {texto}!")
                msg = f"--- {emoji} {m['nome']} {texto}! ---"
                send(msg, to=sala_id)
                salvar_mensagem_chat(sala_id, 'Sistema', msg)

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro status_monstro: {e}")


@socketio.on('batalha_encerrar')
def handle_encerrar_batalha(data):
    """Mestre encerra a batalha."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))
    motivo  = data.get('motivo', 'encerrada')  # vitoria | derrota | encerrada

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id):
            return

        if sala_id in batalhas_ativas:
            del batalhas_ativas[sala_id]

        emojis = {'vitoria': '🏆', 'derrota': '💀', 'encerrada': '🏳️'}
        textos = {'vitoria': 'VITÓRIA!', 'derrota': 'DERROTA...', 'encerrada': 'Batalha encerrada.'}
        emoji = emojis.get(motivo, '🏳️')
        texto = textos.get(motivo, 'Batalha encerrada.')

        socketio.emit('batalha_encerrada', {
            'motivo': motivo, 'texto': texto, 'emoji': emoji,
        }, to=sala_id)

        msg = f"--- {emoji} {texto} ---"
        send(msg, to=sala_id)
        salvar_mensagem_chat(sala_id, 'Sistema', msg)

    except Exception as e:
        print(f"Erro encerrar_batalha: {e}")




@socketio.on('batalha_player_iniciativa')
def handle_player_iniciativa(data):
    """Player envia sua própria rolagem de iniciativa."""
    token   = data.get('token')
    sala_id = str(data.get('sala_id'))
    valor   = int(data.get('valor', 0))

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        if b['fase'] != 'iniciativa':
            return

        # Encontrar o jogador pelo user_id (via sid)
        sid = request.sid
        for j in b['jogadores']:
            if j['sid'] == sid:
                j['iniciativa'] = valor
                b['log'].append(f"🎲 {j['nome']} rolou {valor} de iniciativa!")
                break

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro player_iniciativa: {e}")


@socketio.on('batalha_d20_acerto')
def handle_d20_acerto(data):
    """Player rola D20 para tentar acertar no seu turno."""
    token    = data.get('token')
    sala_id  = str(data.get('sala_id'))
    valor    = int(data.get('valor', 0))

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        if b['fase'] != 'combate' or b.get('sub_fase') != 'aguardando_d20_acerto':
            socketio.emit('batalha_erro', {'mensagem': 'Não é hora de rolar acerto.'}, room=request.sid)
            return

        # Verificar se é o turno deste player
        ativos = [p for p in b['turno_ordem'] if not _esta_fora(p['id'], b)]
        if not ativos:
            return
        turno_atual = ativos[b['turno_atual'] % len(ativos)]

        sid = request.sid
        player_no_turno = next((j for j in b['jogadores'] if j['sid'] == sid and j['ficha_id'] == turno_atual['id']), None)
        if not player_no_turno:
            socketio.emit('batalha_erro', {'mensagem': 'Não é seu turno.'}, room=request.sid)
            return

        b['d20_acerto_atual'] = valor
        b['sub_fase'] = 'aguardando_dado_dano'
        b['log'].append(f"🎲 {player_no_turno['nome']} rolou {valor} para acerto!")

        # Notificar mestre para escolher o dado de dano
        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro d20_acerto: {e}")


@socketio.on('batalha_mestre_escolhe_dado')
def handle_mestre_escolhe_dado(data):
    """Mestre escolhe qual dado o player vai rolar para dano."""
    token    = data.get('token')
    sala_id  = str(data.get('sala_id'))
    dado     = data.get('dado', '1d6')   # ex: '1d6', '2d8', '1d6+1d10'
    alvo_id  = data.get('alvo_id')

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if user_id != buscar_mestre_da_sala(sala_id) or sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        if b.get('sub_fase') != 'aguardando_dado_dano':
            return

        b['dado_dano_atual'] = dado
        b['alvo_dano_atual'] = alvo_id
        b['sub_fase'] = 'aguardando_roll_dano'
        b['log'].append(f"🎲 Mestre escolheu {dado} como dado de dano!")

        # Notificar o alvo escolhido também
        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
        }, to=sala_id)

    except Exception as e:
        print(f"Erro mestre_escolhe_dado: {e}")


@socketio.on('batalha_roll_dano')
def handle_roll_dano(data):
    """Player rola o dado de dano escolhido pelo mestre."""
    token    = data.get('token')
    sala_id  = str(data.get('sala_id'))
    valor    = int(data.get('valor', 0))
    rolagem_str = data.get('rolagem_str', '')

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id   = int(user_data['sub'])
        if sala_id not in batalhas_ativas:
            return

        b = batalhas_ativas[sala_id]
        if b.get('sub_fase') != 'aguardando_roll_dano':
            socketio.emit('batalha_erro', {'mensagem': 'Não é hora de rolar dano.'}, room=request.sid)
            return

        # Verificar turno
        ativos = [p for p in b['turno_ordem'] if not _esta_fora(p['id'], b)]
        if not ativos: return
        turno_atual = ativos[b['turno_atual'] % len(ativos)]

        sid = request.sid
        player_no_turno = next((j for j in b['jogadores'] if j['sid'] == sid and j['ficha_id'] == turno_atual['id']), None)
        if not player_no_turno:
            socketio.emit('batalha_erro', {'mensagem': 'Não é seu turno.'}, room=request.sid)
            return

        nome_atacante = player_no_turno['nome']
        alvo_id = b.get('alvo_dano_atual')
        dado    = b.get('dado_dano_atual', '?d?')
        d20     = b.get('d20_acerto_atual', '?')

        # Aplicar dano no alvo
        nome_alvo = alvo_id
        for m in b['monstros']:
            if m['id'] == alvo_id:
                nome_alvo = m['nome']
                m['hp_atual'] = max(0, m['hp_atual'] - valor)
                if m['hp_atual'] == 0 and m['status'] == 'vivo':
                    m['status'] = 'derrotado'
                    b['log'].append(f"💥 {m['nome']} foi derrotado!")
                    msg = f"--- 💥 {m['nome']} foi derrotado! ---"
                    send(msg, to=sala_id)
                    salvar_mensagem_chat(sala_id, 'Sistema', msg)

        for j in b['jogadores']:
            if j['ficha_id'] == str(alvo_id):
                nome_alvo = j['nome']
                j['hp_atual'] = max(0, j['hp_atual'] - valor)
                if j['hp_atual'] == 0 and j['status'] == 'vivo':
                    j['status'] = 'caido'
                    b['log'].append(f"💀 {j['nome']} caiu em batalha!")

        b['log'].append(f"⚔️ {nome_atacante} (D20:{d20}) usou {dado} → {rolagem_str} = {valor} dano em {nome_alvo}!")

        # Resetar sub_fase
        b['sub_fase'] = None
        b['d20_acerto_atual'] = None
        b['dado_dano_atual'] = None
        b['alvo_dano_atual'] = None

        socketio.emit('batalha_atualizada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': b,
            'efeito': {'tipo': 'ataque', 'atacante': player_no_turno['ficha_id'], 'alvo': alvo_id, 'dano': valor},
        }, to=sala_id)

    except Exception as e:
        print(f"Erro roll_dano: {e}")


# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == '__main__':
    # HACK: Força o uso do servidor Werkzeug/threading desabilitando a detecção do eventlet.
    # O eventlet, quando instalado, é pego automaticamente mas está causando conflitos com o CORS.
    try:
        from socketio import server
        server.eventlet = None
        print("MODO DE COMPATIBILIDADE: Eventlet desabilitado. Iniciando via Threading/Werkzeug...")
    except (ImportError, AttributeError):
        print("AVISO: Não foi possível desabilitar o eventlet. Tentando iniciar mesmo assim...")

    socketio.run(app, host='0.0.0.0', port=5003, debug=True, allow_unsafe_werkzeug=True)