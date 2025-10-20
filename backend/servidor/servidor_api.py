# servidor/servidor_api.py

# --- IMPORTS PRINCIPAIS ---
import sys
import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send, join_room
from flask_cors import CORS  # Mantido, conforme sua solução funcional.
from functools import wraps
import jwt
from datetime import datetime, timedelta, timezone
import json

# --- AJUSTE DE PATH PARA IMPORTAÇÕES ROBUSTAS ---
# Adiciona a pasta raiz do projeto (plataforma_Rpg_mesa) ao sys.path
# Isso garante que `from backend.core...` funcione, não importa de onde o script seja executado.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# --- IMPORTS DE MÓDULOS INTERNOS ---
# Importações do nosso projeto, agora em um bloco único e organizado.
# Usamos caminhos relativos ao 'backend' (ex: 'database.') pois executamos o servidor de dentro da pasta 'backend'.
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
    buscar_dados_essenciais_ficha,
    buscar_anotacoes,
    salvar_anotacoes,
    buscar_inventario_sala,
    adicionar_item_sala,
    apagar_item_sala,
    adicionar_xp_e_upar,  
    buscar_mestre_da_sala  
)
from database.db_manager import buscar_jogadores_na_sala # Importa a nova função
from core.rolador_de_dados import rolar_dados

# --- CONFIGURAÇÃO DO SERVIDOR ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte-e-dificil-de-adivinhar-12345'

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

@app.route("/api/fichas/<int:id>", methods=['GET'])
@token_required
def get_ficha_unica(current_user_id, id):
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

# --- Rotas de Anotações (Protegidas) ---
@app.route("/api/salas/<int:sala_id>/anotacoes", methods=['GET'])
@token_required
def get_anotacoes(current_user_id, sala_id):
    notas = buscar_anotacoes(current_user_id, sala_id)
    return jsonify({'notas': notas})

@app.route("/api/salas/<int:sala_id>/anotacoes", methods=['PUT'])
@token_required
def put_anotacoes(current_user_id, sala_id):
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
# (Todas as funções de WebSocket foram movidas para o lugar correto, fora de outras funções)

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
        
        # Verifica se o usuário é o mestre da sala
        mestre_id = buscar_mestre_da_sala(sala_id)
        is_mestre = (user_id == mestre_id)
        # Envia um evento privado de volta ao cliente informando seu status
        socketio.emit('status_mestre', {'isMestre': is_mestre}, room=request.sid)

        ficha_data = buscar_dados_essenciais_ficha(ficha_id, user_id)
        if not ficha_data:
            send({'error': 'Ficha não encontrada ou não pertence a você.'}); return
            
        nome_personagem = ficha_data['nome_personagem']
        join_room(sala_id)
        
        historico = buscar_historico_chat(sala_id)
        socketio.emit('chat_history', {'historico': historico}, room=request.sid)

        # Envia a lista de jogadores atualizada para todos na sala
        jogadores_na_sala = buscar_jogadores_na_sala(sala_id)
        socketio.emit('lista_jogadores_atualizada', {'jogadores': jogadores_na_sala}, to=sala_id)
        
        # Formata a mensagem de entrada baseado no status
        remetente_entrada = f"Mestre ({nome_personagem})" if is_mestre else nome_personagem
        mensagem_entrada = f"--- {remetente_entrada} entrou na taverna! ---"
        
        send(mensagem_entrada, to=sala_id)
        salvar_mensagem_chat(sala_id, 'Sistema', f"{remetente_entrada} entrou na taverna!")
        print(f"{remetente_entrada} (User ID: {user_id}) entrou na sala {sala_id}")
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
        # Verifica se é o mestre para adicionar uma tag [Mestre]
        mestre_id = buscar_mestre_da_sala(sala_id)
        remetente = f"[Mestre] {nome_personagem}" if user_id == mestre_id else nome_personagem
        
        salvar_mensagem_chat(sala_id, remetente, message_text)
        formatted_message = f"[{remetente}]: {message_text}"
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
        # Verifica se é o mestre para adicionar uma tag [Mestre]
        mestre_id = buscar_mestre_da_sala(sala_id)
        remetente = f"[Mestre] {nome_personagem}" if user_id == mestre_id else nome_personagem
        
        total, rolagens = rolar_dados(dice_command)
        resultado_str = f"{total} ({', '.join(map(str, rolagens))})" if len(rolagens) > 1 else str(total)
        
        mensagem = f"🎲 [{remetente}] rolou {dice_command} e tirou: {resultado_str}"
        salvar_mensagem_chat(sala_id, 'Sistema', f"[{remetente}] rolou {dice_command} e tirou: {resultado_str}")
        send(mensagem, to=sala_id)
    except Exception as e:
        print(f"Erro ao rolar dados: {e}"); send({'error': 'Token inválido.'})

# --- NOVO EVENTO DE MESTRE PARA DAR XP ---
@socketio.on('mestre_dar_xp')
def handle_dar_xp(data):
    """Ouve o comando do Mestre para distribuir XP."""
    token = data.get('token'); sala_id = data.get('sala_id'); ficha_id_alvo = data.get('alvo_id'); quantidade = data.get('quantidade')
    if not all([token, sala_id, ficha_id_alvo, quantidade]):
        send({'error': 'Dados de XP incompletos.'}); return

    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])

        # 1. VERIFICAÇÃO DE MESTRE
        mestre_id = buscar_mestre_da_sala(sala_id)
        if user_id != mestre_id:
            send({'error': 'Apenas o Mestre pode distribuir XP.'}); return

        # 2. LÓGICA DE DISTRIBUIÇÃO
        quantidade_xp = int(quantidade)
        alvos = []

        if ficha_id_alvo == 'all':
            # Se o alvo for 'all', busca todos os jogadores na sala
            jogadores_na_sala = buscar_jogadores_na_sala(sala_id)
            alvos = [j['id'] for j in jogadores_na_sala]
        else:
            # Se for um alvo específico, coloca em uma lista
            alvos.append(int(ficha_id_alvo))

        # 3. PROCESSA O XP PARA CADA ALVO
        for id_alvo in alvos:
            ficha_atualizada = adicionar_xp_e_upar(id_alvo, quantidade_xp)

            if ficha_atualizada:
                # 4. AVISA A TODOS NA SALA sobre o ganho de XP
                nome_personagem_alvo = ficha_atualizada['nome_personagem']
                mensagem_xp = f"--- {nome_personagem_alvo} recebe {quantidade_xp} pontos de experiência! ---"
                salvar_mensagem_chat(sala_id, 'Sistema', mensagem_xp)
                send(mensagem_xp, to=sala_id)

                # 5. ENVIA A FICHA ATUALIZADA PARA TODOS
                # O frontend de cada jogador decidirá se a ficha é a sua e se deve atualizar.
                socketio.emit('ficha_atualizada', ficha_atualizada, to=sala_id)

                # Mensagem de level up no chat
                if 'subiu_de_nivel' in ficha_atualizada and ficha_atualizada['subiu_de_nivel']:
                    mensagem_lvl_up = f"🎉🎉🎉 {nome_personagem_alvo} subiu para o nível {ficha_atualizada['nivel']}! 🎉🎉🎉"
                    salvar_mensagem_chat(sala_id, 'Sistema', mensagem_lvl_up)
                    send(mensagem_lvl_up, to=sala_id)

    except Exception as e:
        print(f"Erro ao processar XP: {e}")
        send({'error': 'Token inválido ou erro ao dar XP.'})

# --- INICIALIZAÇÃO DO SERVIDOR ---
if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001)