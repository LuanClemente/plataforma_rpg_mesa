# backend/api_routes.py

import jwt
from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from database.db_manager import (
    registrar_novo_usuario, verificar_login, atualizar_credenciais_usuario,
    buscar_dados_cantigas, buscar_historico_salas,
    buscar_fichas_por_usuario, buscar_ficha_por_id,
    criar_nova_ficha, atualizar_ficha, apagar_ficha,
    criar_nova_sala, listar_salas_disponiveis, verificar_senha_da_sala,
    buscar_todos_os_monstros, criar_novo_monstro, atualizar_monstro_existente, apagar_monstro_base,
    buscar_todos_os_itens, criar_novo_item, atualizar_item_existente, apagar_item_base,
    buscar_todas_as_habilidades, criar_nova_habilidade, atualizar_habilidade_existente, apagar_habilidade_base,
    buscar_inventario_sala, adicionar_item_sala, apagar_item_sala,
    buscar_anotacoes, salvar_anotacoes,
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ─── DECORADOR JWT ────────────────────────────────────────────────────────────
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({'mensagem': 'Token ausente.'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({'mensagem': 'Token expirado.'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'mensagem': 'Token inválido.'}), 401
        return f(data, *args, **kwargs)
    return decorated


# ─── AUTH ─────────────────────────────────────────────────────────────────────
@api_bp.route('/registrar', methods=['POST'])
def registrar():
    dados = request.get_json()
    username = (dados.get('username') or '').strip()
    password = (dados.get('password') or '').strip()
    if not username or not password:
        return jsonify({'sucesso': False, 'mensagem': 'Nome e senha são obrigatórios.'}), 400
    sucesso = registrar_novo_usuario(username, password)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Aventureiro registrado!'})
    return jsonify({'sucesso': False, 'mensagem': 'Nome de usuário já existe.'}), 409


@api_bp.route('/login', methods=['POST'])
def login():
    import datetime
    dados = request.get_json()
    username = (dados.get('username') or '').strip()
    password = (dados.get('password') or '').strip()
    usuario = verificar_login(username, password)
    if not usuario:
        return jsonify({'sucesso': False, 'mensagem': 'Credenciais inválidas.'}), 401
    payload = {
        'sub': usuario['id'],
        'name': username,
        'role': usuario['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    }
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return jsonify({'sucesso': True, 'token': token, 'role': usuario['role']})


# ─── CANTIGAS ─────────────────────────────────────────────────────────────────
@api_bp.route('/cantigas/dados', methods=['GET'])
@token_required
def get_cantigas_dados(token_data):
    dados = buscar_dados_cantigas(token_data['sub'])
    if not dados:
        return jsonify({'tempo_aventura_segundos': 0, 'total_fichas': 0, 'total_salas_visitadas': 0})
    return jsonify(dados)


@api_bp.route('/cantigas/historico', methods=['GET'])
@token_required
def get_cantigas_historico(token_data):
    return jsonify(buscar_historico_salas(token_data['sub']))


# ─── CREDENCIAIS ──────────────────────────────────────────────────────────────
@api_bp.route('/usuario/credenciais', methods=['PUT'])
@token_required
def update_credenciais(token_data):
    dados = request.get_json()
    novo_nome = (dados.get('novo_nome') or '').strip() or None
    nova_senha = (dados.get('nova_senha') or '').strip() or None
    sucesso = atualizar_credenciais_usuario(token_data['sub'], novo_nome, nova_senha)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Identidade atualizada!'})
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao atualizar. Nome pode já estar em uso.'}), 400


# ─── FICHAS ───────────────────────────────────────────────────────────────────
@api_bp.route('/fichas', methods=['GET'])
@token_required
def get_fichas(token_data):
    return jsonify(buscar_fichas_por_usuario(token_data['sub']))


@api_bp.route('/fichas/<int:ficha_id>', methods=['GET'])
@token_required
def get_ficha(token_data, ficha_id):
    import json
    ficha = buscar_ficha_por_id(ficha_id, token_data['sub'])
    if not ficha:
        return jsonify({'mensagem': 'Ficha não encontrada.'}), 404
    if isinstance(ficha.get('atributos_json'), str):
        ficha['atributos'] = json.loads(ficha.pop('atributos_json'))
    if isinstance(ficha.get('pericias_json'), str):
        ficha['pericias'] = json.loads(ficha.pop('pericias_json'))
    return jsonify(ficha)


@api_bp.route('/fichas', methods=['POST'])
@token_required
def criar_ficha(token_data):
    dados = request.get_json()
    sucesso = criar_nova_ficha(
        usuario_id=token_data['sub'],
        nome_personagem=dados.get('nome_personagem'),
        classe=dados.get('classe'),
        raca=dados.get('raca'),
        antecedente=dados.get('antecedente', ''),
        atributos=dados.get('atributos', {}),
        pericias=dados.get('pericias', []),
    )
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha criada!'}), 201
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar ficha.'}), 400


@api_bp.route('/fichas/<int:ficha_id>', methods=['PUT'])
@token_required
def salvar_ficha(token_data, ficha_id):
    sucesso = atualizar_ficha(ficha_id, token_data['sub'], request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha salva!'})
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao salvar ficha.'}), 400


@api_bp.route('/fichas/<int:ficha_id>', methods=['DELETE'])
@token_required
def deletar_ficha(token_data, ficha_id):
    sucesso = apagar_ficha(ficha_id, token_data['sub'])
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Ficha apagada.'})
    return jsonify({'sucesso': False, 'mensagem': 'Ficha não encontrada.'}), 404


# ─── SALAS ────────────────────────────────────────────────────────────────────
@api_bp.route('/salas', methods=['GET'])
@token_required
def get_salas(token_data):
    return jsonify(listar_salas_disponiveis())


@api_bp.route('/salas', methods=['POST'])
@token_required
def post_sala(token_data):
    dados = request.get_json()
    nome = (dados.get('nome') or '').strip()
    senha = (dados.get('senha') or '').strip() or None
    if not nome:
        return jsonify({'mensagem': 'Nome da sala é obrigatório.'}), 400
    sucesso = criar_nova_sala(nome, senha, token_data['sub'])
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': f'Taverna "{nome}" fundada!'}), 201
    return jsonify({'sucesso': False, 'mensagem': 'Já existe uma sala com esse nome.'}), 409


@api_bp.route('/salas/verificar-senha', methods=['POST'])
@token_required
def verificar_senha_sala(token_data):
    dados = request.get_json()
    ok = verificar_senha_da_sala(dados.get('sala_id'), dados.get('senha', ''))
    if ok:
        return jsonify({'sucesso': True})
    return jsonify({'sucesso': False, 'mensagem': 'Senha incorreta.'}), 403


# ─── BESTIÁRIO ────────────────────────────────────────────────────────────────
@api_bp.route('/monstros', methods=['GET'])
@token_required
def get_monstros(token_data):
    return jsonify(buscar_todos_os_monstros())


@api_bp.route('/monstros', methods=['POST'])
@token_required
def post_monstro(token_data):
    sucesso = criar_novo_monstro(request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Monstro criado!'}), 201
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar monstro.'}), 400


@api_bp.route('/monstros/<int:monstro_id>', methods=['PUT'])
@token_required
def put_monstro(token_data, monstro_id):
    sucesso = atualizar_monstro_existente(monstro_id, request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Monstro atualizado!'})
    return jsonify({'sucesso': False, 'mensagem': 'Monstro não encontrado.'}), 404


@api_bp.route('/monstros/<int:monstro_id>', methods=['DELETE'])
@token_required
def delete_monstro(token_data, monstro_id):
    sucesso = apagar_monstro_base(monstro_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Monstro removido.'})
    return jsonify({'sucesso': False, 'mensagem': 'Monstro não encontrado.'}), 404


# ─── FERRARIA ARCANA — ITENS ──────────────────────────────────────────────────
@api_bp.route('/itens', methods=['GET'])
@token_required
def get_itens(token_data):
    return jsonify(buscar_todos_os_itens())


@api_bp.route('/itens', methods=['POST'])
@token_required
def post_item(token_data):
    sucesso = criar_novo_item(request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item criado!'}), 201
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar item.'}), 400


@api_bp.route('/itens/<int:item_id>', methods=['PUT'])
@token_required
def put_item(token_data, item_id):
    sucesso = atualizar_item_existente(item_id, request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item atualizado!'})
    return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado.'}), 404


@api_bp.route('/itens/<int:item_id>', methods=['DELETE'])
@token_required
def delete_item(token_data, item_id):
    sucesso = apagar_item_base(item_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item removido.'})
    return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado.'}), 404


# ─── HABILIDADES ──────────────────────────────────────────────────────────────
@api_bp.route('/habilidades', methods=['GET'])
@token_required
def get_habilidades(token_data):
    return jsonify(buscar_todas_as_habilidades())


@api_bp.route('/habilidades', methods=['POST'])
@token_required
def post_habilidade(token_data):
    sucesso = criar_nova_habilidade(request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Habilidade criada!'}), 201
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao criar habilidade.'}), 400


@api_bp.route('/habilidades/<int:habilidade_id>', methods=['PUT'])
@token_required
def put_habilidade(token_data, habilidade_id):
    sucesso = atualizar_habilidade_existente(habilidade_id, request.get_json())
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Habilidade atualizada!'})
    return jsonify({'sucesso': False, 'mensagem': 'Habilidade não encontrada.'}), 404


@api_bp.route('/habilidades/<int:habilidade_id>', methods=['DELETE'])
@token_required
def delete_habilidade(token_data, habilidade_id):
    sucesso = apagar_habilidade_base(habilidade_id)
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Habilidade removida.'})
    return jsonify({'sucesso': False, 'mensagem': 'Habilidade não encontrada.'}), 404


# ─── INVENTÁRIO DA SALA ───────────────────────────────────────────────────────
@api_bp.route('/sala/<int:sala_id>/inventario', methods=['GET'])
@token_required
def get_inventario(token_data, sala_id):
    ficha_id = request.args.get('ficha_id', type=int)
    if not ficha_id:
        return jsonify({'mensagem': 'ficha_id é obrigatório.'}), 400
    return jsonify(buscar_inventario_sala(ficha_id, sala_id))


@api_bp.route('/sala/<int:sala_id>/inventario', methods=['POST'])
@token_required
def post_inventario(token_data, sala_id):
    dados = request.get_json()
    sucesso = adicionar_item_sala(dados.get('ficha_id'), sala_id, dados.get('nome_item'), dados.get('descricao', ''))
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item adicionado!'}), 201
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao adicionar item.'}), 400


@api_bp.route('/inventario/<int:item_id>', methods=['DELETE'])
@token_required
def delete_inventario(token_data, item_id):
    dados = request.get_json()
    sucesso = apagar_item_sala(item_id, dados.get('ficha_id'))
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Item removido.'})
    return jsonify({'sucesso': False, 'mensagem': 'Item não encontrado.'}), 404


# ─── ANOTAÇÕES ────────────────────────────────────────────────────────────────
@api_bp.route('/sala/<int:sala_id>/anotacoes', methods=['GET'])
@token_required
def get_anotacoes(token_data, sala_id):
    anotacoes = buscar_anotacoes(token_data['sub'], sala_id)
    return jsonify({'notas': anotacoes or ''})


@api_bp.route('/sala/<int:sala_id>/anotacoes', methods=['PUT'])
@token_required
def put_anotacoes(token_data, sala_id):
    dados = request.get_json()
    sucesso = salvar_anotacoes(token_data['sub'], sala_id, dados.get('notas', ''))
    if sucesso:
        return jsonify({'sucesso': True, 'mensagem': 'Anotações salvas!'})
    return jsonify({'sucesso': False, 'mensagem': 'Erro ao salvar anotações.'}), 400