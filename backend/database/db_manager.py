# database/db_manager.py

# Importa a biblioteca para interagir com o banco de dados SQLite.
import sqlite3
# Importa a classe 'Monstro' para que possamos criar um objeto Monstro com os dados do DB.
from core.monstro import Monstro

# Define o caminho para o arquivo do banco de dados, relativo à pasta raiz 'backend'.
NOME_DB = "database/campanhas.db"

def buscar_monstro_aleatorio():
    """
    Conecta ao banco de dados, busca um monstro aleatório da tabela 'monstros_base'
    e retorna um objeto Monstro totalmente instanciado e pronto para o combate.
    """
    # O bloco 'try...except' garante que, se houver um erro de banco de dados, o programa não irá quebrar.
    try:
        # Estabelece a conexão com o arquivo do banco de dados.
        conexao = sqlite3.connect(NOME_DB)
        # Cria o cursor para executar comandos.
        cursor = conexao.cursor()

        # Executa uma consulta SQL para buscar um monstro aleatório.
        # - SELECT * FROM monstros_base: Seleciona todas as colunas da tabela de monstros.
        # - ORDER BY RANDOM(): Embaralha todas as linhas da tabela aleatoriamente.
        # - LIMIT 1: Pega apenas a primeira linha do resultado embaralhado.
        cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
        
        # 'fetchone()' busca apenas um resultado da consulta.
        dados_monstro = cursor.fetchone()
        
        # Fecha a conexão para liberar o recurso.
        conexao.close()

        # Verifica se um monstro foi realmente encontrado (a tabela poderia estar vazia).
        if dados_monstro:
            # "Hidrata" um objeto Monstro: cria uma instância da classe usando os dados da tupla do DB.
            # Os dados vêm na ordem das colunas: [0]=id, [1]=nome, [2]=vida_maxima, etc.
            monstro_encontrado = Monstro(
                nome=dados_monstro[1],
                vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3],
                dano_dado=dados_monstro[4],
                defesa=dados_monstro[5],
                xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
            # Retorna o objeto Monstro criado.
            return monstro_encontrado
        else:
            # Se nenhum monstro for encontrado, retorna None.
            return None
            
    except sqlite3.Error as e:
        # Se ocorrer qualquer erro relacionado ao SQLite, imprime uma mensagem de erro.
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        # Retorna None para indicar que a operação falhou.
        return None

def buscar_todos_os_itens():
    """
    Busca todos os itens da tabela 'itens_base' para serem usados, por exemplo, na loja.
    """
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Busca todos os itens, ordenados pelo preço para que a lista da loja apareça organizada.
        cursor.execute("SELECT * FROM itens_base ORDER BY preco_ouro")
        # 'fetchall()' busca todos os resultados da consulta e os retorna como uma lista de tuplas.
        itens = cursor.fetchall()
        conexao.close()
        # Retorna a lista completa de itens.
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens no banco de dados: {e}")
        # Retorna uma lista vazia em caso de erro, para que o programa não quebre.
        return []

def buscar_detalhes_itens(nomes_dos_itens: list):
    """
    Busca no banco de dados os detalhes de uma lista específica de nomes de itens.
    É usado para obter as propriedades dos itens que o jogador carrega no inventário.
    """
    # Se a lista de nomes de itens estiver vazia, retorna uma lista vazia para evitar uma consulta inútil.
    if not nomes_dos_itens:
        return []
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Prepara os placeholders ('?') para a consulta. Teremos um '?' para cada nome na lista.
        # Ex: Se a lista for ['Adaga', 'Poção'], placeholders será '?, ?'.
        placeholders = ', '.join('?' for _ in nomes_dos_itens)
        # A cláusula 'WHERE nome IN (...)' é uma forma eficiente de buscar todas as linhas cujo nome está na lista fornecida.
        query = f"SELECT * FROM itens_base WHERE nome IN ({placeholders})"
        # Executa a query, passando a lista de nomes para preencher os placeholders de forma segura.
        cursor.execute(query, nomes_dos_itens)
        itens = cursor.fetchall()
        conexao.close()
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de itens: {e}")
        return []

def buscar_detalhes_habilidades(nomes_das_habilidades: list):
    """
    Busca no banco de dados os detalhes de uma lista específica de nomes de habilidades.
    É usado para obter as propriedades (custo, efeito) das habilidades que um personagem conhece.
    """
    # Exatamente a mesma lógica da função de buscar itens, mas aplicada à tabela de habilidades.
    if not nomes_das_habilidades:
        return []
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Prepara os placeholders para a consulta de habilidades.
        placeholders = ', '.join('?' for _ in nomes_das_habilidades)
        # A consulta agora é na tabela 'habilidades_base'.
        query = f"SELECT * FROM habilidades_base WHERE nome IN ({placeholders})"
        # Executa a query com a lista de nomes de habilidades.
        cursor.execute(query, nomes_das_habilidades)
        habilidades = cursor.fetchall()
        conexao.close()
        return habilidades
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de habilidades: {e}")
        return []