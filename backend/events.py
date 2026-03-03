# backend/events.py
# Eventos WebSocket — compatível com SalaPage.jsx

import jwt
import re
import random
from flask import request, current_app
from flask_socketio import emit, join_room, leave_room
from app import socketio
from database.db_manager import (
    buscar_ficha_por_id, buscar_mestre_da_sala,
    salvar_mensagem_chat, buscar_historico_chat,
    registrar_acesso_sala,
)


def _decode_token(token):
    """Decodifica o JWT e retorna o payload, ou None se inválido."""
    try:
        return jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    except Exception:
        return None


def _rolar_dados(comando):
    """
    Interpreta comandos no formato NdX+M (ex: 2d6+3, 1d20, d8).
    Retorna (resultado_total, detalhes_str) ou None se inválido.
    """
    match = re.fullmatch(r'(\d*)d(\d+)([+-]\d+)?', comando.strip().lower())
    if not match:
        return None
    qtd = int(match.group(1)) if match.group(1) else 1
    faces = int(match.group(2))
    mod = int(match.group(3)) if match.group(3) else 0

    if qtd < 1 or qtd > 20 or faces < 2 or faces > 100:
        return None

    rolls = [random.randint(1, faces) for _ in range(qtd)]
    total = sum(rolls) + mod
    detalhes = f"[{', '.join(str(r) for r in rolls)}]"
    if mod:
        detalhes += f" {'+' if mod > 0 else ''}{mod}"
    return total, detalhes


# ─── CONNECT / DISCONNECT ─────────────────────────────────────────────────────

@socketio.on('connect')
def handle_connect():
    print(f"🔌 Cliente conectado: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Cliente desconectado: {request.sid}")


# ─── JOIN ROOM ────────────────────────────────────────────────────────────────

@socketio.on('join_room')
def on_join(data):
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    ficha_id = data.get('ficha_id')

    usuario = _decode_token(token)
    if not usuario:
        emit('error', {'mensagem': 'Token inválido.'})
        return

    usuario_id = usuario['sub']
    nome_usuario = usuario.get('name', 'Aventureiro')

    # Entra na sala SocketIO
    join_room(sala_id)

    # Registra acesso no histórico do banco
    registrar_acesso_sala(usuario_id, sala_id, ficha_id)

    # Verifica se este usuário é o Mestre da sala
    mestre_id = buscar_mestre_da_sala(sala_id)
    is_mestre = (mestre_id == usuario_id)
    emit('status_mestre', {'isMestre': is_mestre})

    # Envia histórico de chat para o novo participante
    historico = buscar_historico_chat(sala_id)
    msgs_formatadas = [
        {'text': f"[{m['remetente']}]: {m['mensagem']}", 'remetente': m['remetente']}
        for m in historico
    ]
    emit('chat_history', {'historico': msgs_formatadas})

    # Anuncia entrada na sala para todos
    aviso = {'text': f"⚔️ {nome_usuario} entrou na sala."}
    emit('message', aviso, to=sala_id)
    salvar_mensagem_chat(sala_id, 'Sistema', f"{nome_usuario} entrou na sala.")

    print(f"✅ {nome_usuario} entrou na sala {sala_id} (mestre={is_mestre})")


# ─── SEND MESSAGE ─────────────────────────────────────────────────────────────

@socketio.on('send_message')
def handle_message(data):
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    message = (data.get('message') or '').strip()

    usuario = _decode_token(token)
    if not usuario or not message:
        return

    nome = usuario.get('name', 'Aventureiro')
    texto = f"[{nome}]: {message}"

    salvar_mensagem_chat(sala_id, nome, message)
    emit('message', {'text': texto, 'remetente': nome}, to=sala_id)


# ─── ROLL DICE ────────────────────────────────────────────────────────────────

@socketio.on('roll_dice')
def handle_roll_dice(data):
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    command = (data.get('command') or '1d20').strip()

    usuario = _decode_token(token)
    if not usuario:
        return

    nome = usuario.get('name', 'Aventureiro')
    resultado = _rolar_dados(command)

    if resultado is None:
        emit('message', {'text': f"⚠️ Comando inválido: '{command}'. Use formato como 1d20, 2d6+3."})
        return

    total, detalhes = resultado
    texto = f"🎲 {nome} rolou {command}: {detalhes} = **{total}**"
    salvar_mensagem_chat(sala_id, 'Dados', texto)
    emit('message', {'text': texto}, to=sala_id)