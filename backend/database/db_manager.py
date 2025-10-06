# database/db_manager.py

import sqlite3
from core.monstro import Monstro # Já existente

NOME_DB = "database/campanhas.db" # Corrigindo o caminho para ser relativo à raiz do backend

def buscar_monstro_aleatorio():
    # ... (código da função existente, sem alterações)
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
        dados_monstro = cursor.fetchone()
        conexao.close()
        if dados_monstro:
            return Monstro(
                nome=dados_monstro[1], vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3], dano_dado=dados_monstro[4],
                defesa=dados_monstro[5], xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
        return None
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        return None

# --- NOVA FUNÇÃO PARA A LOJA ---
def buscar_todos_os_itens():
    """
    Busca todos os itens da tabela 'itens_base' e os retorna.
    """
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Busca todos os itens, ordenados pelo preço para uma lista mais organizada.
        cursor.execute("SELECT * FROM itens_base ORDER BY preco_ouro")
        itens = cursor.fetchall()
        conexao.close()
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens no banco de dados: {e}")
        return [] # Retorna uma lista vazia em caso de erro.
    
    # --- FUNÇÃO PARA BUSCAR DETALHES DE ITENS ---
def buscar_detalhes_itens(nomes_dos_itens: list):
    """
    Busca no banco de dados os detalhes de uma lista específica de itens.
    """
    if not nomes_dos_itens:
        return []
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Prepara os placeholders (?) para a consulta. Teremos um '?' para cada item na lista.
        placeholders = ', '.join('?' for _ in nomes_dos_itens)
        # A cláusula 'WHERE nome IN (...)' busca todas as linhas cujo nome está na lista.
        query = f"SELECT * FROM itens_base WHERE nome IN ({placeholders})"
        cursor.execute(query, nomes_dos_itens)
        itens = cursor.fetchall()
        conexao.close()
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de itens: {e}")
        return []