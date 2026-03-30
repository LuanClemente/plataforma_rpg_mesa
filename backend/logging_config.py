# -*- coding: utf-8 -*-
"""
Sistema de Logging Centralizado para a Plataforma RPG
- Salva logs em arquivo com rotação automática por tamanho
- Limite: 5MB por arquivo, máximo 5 backups
- Formato: [TIMESTAMP] [LEVEL] [MODULE] [USER_ID] Message
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Diretório de logs
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOGS_DIR, 'app.log')

def setup_logging():
    """Configura o logger com rotação de arquivos."""
    logger = logging.getLogger('rpg_mesa')
    
    # Evita duplicação de handlers
    if logger.hasHandlers():
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Formato detalhado
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # RotatingFileHandler: max 5MB por arquivo, até 5 backups
    # app.log, app.log.1, app.log.2, etc
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5,               # Mantém últimos 5 backups
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Console handler (opcional, para ver logs no terminal também)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info('=' * 80)
    logger.info(f'Logger inicializado em {datetime.now()}')
    logger.info(f'Arquivo de logs: {LOG_FILE}')
    logger.info('=' * 80)
    
    return logger

# Criar logger global
logger = setup_logging()

def log_conexao(evento, user_id=None, sala_id=None, sid=None, info_extra=None):
    """Log de eventos de conexão."""
    ctx = f"[User:{user_id}] [Sala:{sala_id}] [SID:{sid}]" if any([user_id, sala_id, sid]) else ""
    msg = f"{evento} {ctx}".strip()
    if info_extra:
        msg += f" | {info_extra}"
    logger.info(msg)

def log_evento_socket(evento, sala_id, user_id=None, payload_resumo=None):
    """Log de eventos do Socket.IO."""
    ctx = f"[Evento:{evento}] [Sala:{sala_id}] [User:{user_id}]"
    if payload_resumo:
        ctx += f" | {payload_resumo}"
    logger.info(ctx)

def log_batalha(fase, sala_id, detalhes):
    """Log de eventos de batalha."""
    logger.info(f"[BATALHA] [Sala:{sala_id}] [Fase:{fase}] | {detalhes}")

def log_erro(modulo, user_id=None, sala_id=None, erro_msg=None):
    """Log de erros."""
    ctx = f"[ERRO] [{modulo}]"
    if user_id:
        ctx += f" [User:{user_id}]"
    if sala_id:
        ctx += f" [Sala:{sala_id}]"
    logger.error(f"{ctx} | {erro_msg if erro_msg else 'Erro desconhecido'}")

def log_debug(modulo, msg):
    """Log de debug."""
    logger.debug(f"[{modulo}] {msg}")

def log_warning(modulo, msg, user_id=None):
    """Log de warning."""
    ctx = f"[{modulo}]" + (f" [User:{user_id}]" if user_id else "")
    logger.warning(f"{ctx} {msg}")
