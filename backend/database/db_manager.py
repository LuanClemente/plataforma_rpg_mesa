# database/db_manager.py

# Importa as bibliotecas necessárias.
import sqlite3
import os
from core.monstro import Monstro
import bcrypt
import json

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Garante que o caminho para o banco de dados seja sempre encontrado corretamente.
script_dir = os.path.dirname(os.path.abspath(__file__))
NOME_DB = os.path.join(script_dir, 'campanhas.db')


def buscar_monstro_aleatorio():
    """Conecta ao DB, busca um monstro aleatório e retorna um objeto Monstro."""
    try:
        # O 'with' gerencia a conexão, garantindo que ela seja fechada no final.
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
            dados_monstro = cursor.fetchone()
        
        if dados_monstro:
            # Cria a instância do objeto Monstro com os dados da tupla do DB.
            return Monstro(
                nome=dados_monstro[1], vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3], dano_dado=dados_monstro[4],
                defesa=dados_monstro[5], xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
        else:
            return None
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        return None

def buscar_todos_os_itens():
    """Busca todos os itens da tabela 'itens_base'."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM itens_base ORDER BY preco_ouro")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens no banco de dados: {e}")
        return []

def buscar_detalhes_itens(nomes_dos_itens: list):
    """Busca os detalhes de uma lista específica de nomes de itens."""
    if not nomes_dos_itens:
        return []
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            placeholders = ', '.join('?' for _ in nomes_dos_itens)
            query = f"SELECT * FROM itens_base WHERE nome IN ({placeholders})"
            cursor.execute(query, nomes_dos_itens)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de itens: {e}")
        return []

def buscar_detalhes_habilidades(nomes_das_habilidades: list):
    """Busca os detalhes de uma lista específica de nomes de habilidades."""
    if not nomes_das_habilidades:
        return []
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            placeholders = ', '.join('?' for _ in nomes_das_habilidades)
            query = f"SELECT * FROM habilidades_base WHERE nome IN ({placeholders})"
            cursor.execute(query, nomes_das_habilidades)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de habilidades: {e}")
        return []

def buscar_todos_os_monstros():
    """Busca todos os monstros da tabela 'monstros_base'."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar todos os monstros: {e}")
        return []

def registrar_novo_usuario(nome_usuario, senha_texto_puro):
    """Cria o hash da senha e insere um novo usuário no banco de dados."""
    try:
        senha_bytes = senha_texto_puro.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome_usuario, senha_hash) VALUES (?, ?)",
                (nome_usuario, senha_hash)
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao registrar novo usuário: {e}")
        return False


def criar_nova_ficha(usuario_id, nome_personagem, classe, raca, antecedente, atributos, pericias):
    """Insere uma nova ficha de personagem completa no banco de dados."""
    try:
        # Converte os dicionários/listas para strings JSON para armazenamento.
        atributos_str_json = json.dumps(atributos)
        pericias_str_json = json.dumps(pericias)

        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # --- CORREÇÃO APLICADA AQUI ---
            # O comando INSERT agora inclui as novas colunas: raca, antecedente, pericias_json
            cursor.execute(
                "INSERT INTO fichas_personagem (usuario_id, nome_personagem, classe, raca, antecedente, nivel, atributos_json, pericias_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                # E a tupla de valores agora contém todos os 8 parâmetros.
                (usuario_id, nome_personagem, classe, raca, antecedente, 1, atributos_str_json, pericias_str_json)
            )
        return True
    except Exception as e:
        print(f"Erro ao criar nova ficha: {e}")
        return False

def buscar_fichas_por_usuario(usuario_id):
    """Busca todas as fichas de personagem que pertencem a um ID de usuário específico."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            # Para retornar dicionários em vez de tuplas, o que facilita no servidor.
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_personagem, classe, nivel FROM fichas_personagem WHERE usuario_id = ?",
                (usuario_id,)
            )
            # fetchall() com row_factory retorna uma lista de objetos parecidos com dicionários.
            fichas = [dict(row) for row in cursor.fetchall()]
        return fichas
    except Exception as e:
        print(f"Erro ao buscar fichas por usuário: {e}")
        return []
# --- FUNÇÃO ATUALIZADA ---
def verificar_login(nome_usuario, senha_texto_puro):
    """
    Verifica se o usuário existe e a senha está correta.
    Retorna o ID do usuário em caso de sucesso, ou None em caso de falha.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # 1. ATUALIZAÇÃO: Agora buscamos o 'id' junto com a 'senha_hash'.
            cursor.execute(
                "SELECT id, senha_hash FROM usuarios WHERE nome_usuario = ?",
                (nome_usuario,)
            )
            resultado = cursor.fetchone()

        # Se o usuário não for encontrado, 'resultado' será None.
        if resultado is None:
            return None

        # Desempacota o resultado da busca.
        user_id, senha_hash_db = resultado[0], resultado[1]
        # Converte a senha fornecida pelo usuário para bytes.
        senha_bytes = senha_texto_puro.encode('utf-8')

        # Compara a senha fornecida com o hash guardado no banco de dados.
        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            # 2. ATUALIZAÇÃO: Se a senha corresponder, retornamos o ID do usuário.
            return user_id
        else:
            # Se a senha não corresponder, retornamos None.
            return None
            
    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return None
    
    