# -*- coding: utf-8 -*-
"""
EXEMPLO: Como Integrar o Logger no servidor_api.py

Copie e cole os imports e exemplos de uso no seu código.
"""

# ========================
# 1. ADD IMPORTS NO TOPO
# ========================
from logging_config import logger, log_conexao, log_evento_socket, log_batalha, log_erro, log_debug

# ========================
# 2. EVENTOS DE CONEXÃO
# ========================

# Em handle_connect():
@socketio.on('connect')
def handle_connect():
    print(f"🔌 Cliente conectado: {request.sid}")
    # ADD ISSO:
    logger.info(f"[CONNECT] SID: {request.sid}")


# Em handle_disconnect():
@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Cliente desconectado! SID: {request.sid}")
    # ADD ISSO:
    log_conexao(
        evento="[DISCONNECT]",
        sid=request.sid,
        info_extra="Cliente finalizou conexão"
    )
    
    sala_para_remover_de = None
    jogador_removido_info = None
    
    for sala_id, jogadores in salas_ativas.items():
        # ADD LOG:
        log_debug("disconnect", f"Verificando sala {sala_id}, {len(jogadores)} jogadores")
        
        if request.sid in jogadores:
            sala_para_remover_de = str(sala_id)
            jogador_removido_info = jogadores.pop(request.sid)
            # ADD LOG:
            log_conexao(
                evento="[DISCONNECT - REMOVIDO DE SALA]",
                sala_id=sala_id,
                info_extra=f"Jogador: {jogador_removido_info['nome_personagem']}"
            )
            if not jogadores:
                del salas_ativas[sala_id]
            break


# ========================
# 3. EVENTOS DE SOCKET
# ========================

# Em handle_join_room():
@socketio.on('join_room')
def handle_join_room(data):
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    ficha_id = data.get('ficha_id')
    
    # LOG INICIAL:
    log_evento_socket(
        evento="JOIN_ROOM",
        sala_id=sala_id,
        payload_resumo=f"ficha_id={ficha_id}"
    )
    
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        
        # LOG COM MAIS CONTEXTO:
        log_conexao(
            evento="[JOIN_ROOM SUCESSO]",
            user_id=user_id,
            sala_id=sala_id,
            sid=request.sid
        )
        
    except jwt.ExpiredSignatureError:
        # LOG DE ERRO:
        log_erro(
            modulo="join_room",
            user_id=None,
            sala_id=sala_id,
            erro_msg="Token expirado"
        )
        socketio.emit('join_error', {'mensagem': 'Token expirado.'}, room=request.sid)
    except Exception as e:
        # LOG DE ERRO COM EXCEPTION:
        log_erro(
            modulo="join_room",
            sala_id=sala_id,
            erro_msg=f"Exception: {str(e)}"
        )
        socketio.emit('join_error', {'mensagem': f'Erro ao entrar na sala: {e}'}, room=request.sid)


# ========================
# 4. EVENTOS DE BATALHA
# ========================

# Em handle_batalha_iniciar():
@socketio.on('batalha_iniciar')
def handle_batalha_iniciar(data):
    token = data.get('token')
    sala_id = str(data.get('sala_id'))
    monstros_ids = data.get('monstros_ids', [])
    
    try:
        user_data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = int(user_data['sub'])
        
        # LOG DE INÍCIO:
        log_batalha(
            fase="INICIACAO",
            sala_id=sala_id,
            detalhes=f"Mestre:{user_id}, {len(monstros_ids)} monstros selecionados: {monstros_ids}"
        )
        
        # ... resto do código ...
        
        batalhas_ativas[sala_id] = {
            'fase': 'iniciativa',
            'monstros': monstros,
            'jogadores': jogadores,
            # ... etc
        }
        
        # LOG DE SUCESSO:
        log_batalha(
            fase="CRIADA",
            sala_id=sala_id,
            detalhes=f"{len(monstros)} monstros vs {len(jogadores)} jogadores"
        )
        
        socketio.emit('batalha_iniciada', {
            'batalha': _batalha_publica(sala_id),
            'batalha_mestre': batalhas_ativas[sala_id],
        }, to=sala_id)
        
    except Exception as e:
        # LOG DE ERRO:
        log_erro(
            modulo="batalha_iniciar",
            user_id=None,
            sala_id=sala_id,
            erro_msg=f"{type(e).__name__}: {str(e)}"
        )
        socketio.emit('batalha_erro', {'mensagem': str(e)}, room=request.sid)


# Em handle_batalha_player_iniciativa():
@socketio.on('batalha_player_iniciativa')
def handle_batalha_player_iniciativa(data):
    sala_id = str(data.get('sala_id'))
    valor = data.get('valor')
    
    log_debug(
        modulo="batalha_iniciativa",
        msg=f"Sala:{sala_id}, Rolagem: {valor}"
    )
    # ... resto do código ...


# ========================
# 5. OPERAÇÕES COM FICHA
# ========================

# Em handle_dar_xp():
@socketio.on('mestre_dar_xp')
def handle_dar_xp(data):
    sala_id = str(data.get('sala_id'))
    alvo_id_str = data.get('alvo_id')
    quantidade_str = data.get('quantidade')
    
    log_evento_socket(
        evento="MESTRE_DAR_XP",
        sala_id=sala_id,
        payload_resumo=f"alvo={alvo_id_str}, xp={quantidade_str}"
    )
    
    try:
        # ... código ...
        log_debug(
            modulo="dar_xp",
            msg=f"XP distribuído: {quantidade_str} para alvo {alvo_id_str}"
        )
    except Exception as e:
        log_erro(
            modulo="dar_xp",
            sala_id=sala_id,
            erro_msg=str(e)
        )


# ========================
# 6. EXEMPLO: BUSCAR LOGS
# ========================

def buscar_erros_ultima_hora():
    """
    Exemplo de como buscar erros dos últimos logs
    (poderia ser uma rota futura)
    """
    import time
    
    try:
        with open('backend/logs/app.log', 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        
        agora = time.time()
        uma_hora_atras = agora - 3600
        
        linhas_erro = [
            l for l in linhas 
            if '[ERROR]' in l or '[ERRO]' in l
        ]
        
        return linhas_erro[-20:]  # Últimas 20 linhas de erro
    except Exception as e:
        print(f"Erro ao buscar logs: {e}")
        return []
