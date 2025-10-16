# database/db_manager.py

# --- Importações ---
import sqlite3
import os
import json
import bcrypt
# CORREÇÃO: Movido o import para o topo, junto com os outros.
from core.monstro import Monstro 

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
script_dir = os.path.dirname(os.path.abspath(__file__))
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# --- Funções de Busca ---

def buscar_monstro_aleatorio():
    """Conecta ao DB, busca um monstro aleatório e retorna um objeto Monstro."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
            dados_monstro = cursor.fetchone()
        
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
    if not nomes_dos_itens: return []
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
    if not nomes_das_habilidades: return []
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

def buscar_fichas_por_usuario(usuario_id):
    """Busca todas as fichas de personagem que pertencem a um ID de usuário específico."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_personagem, classe, nivel FROM fichas_personagem WHERE usuario_id = ?",
                (usuario_id,)
            )
            fichas = [dict(row) for row in cursor.fetchall()]
            return fichas
    except Exception as e:
        print(f"Erro ao buscar fichas por usuário: {e}")
        return []

def buscar_ficha_por_id(ficha_id, usuario_id):
    """Busca os detalhes completos de uma única ficha, verificando a posse."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT * FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            ficha = cursor.fetchone()
            if ficha:
                return dict(ficha) # Retorna a ficha como um dicionário.
            return None # Retorna None se não encontrar.
    except Exception as e:
        print(f"Erro ao buscar ficha por ID: {e}")
        return None

# --- Funções de Autenticação e Usuário ---

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

# --- CORREÇÃO DE INDENTAÇÃO ---
# Esta função estava indentada dentro de 'registrar_novo_usuario'.
# Foi movida para o nível principal (sem recuo).
def verificar_login(nome_usuario, senha_texto_puro):
    """Verifica se o usuário existe e a senha está correta. Retorna o ID do usuário ou None."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, senha_hash FROM usuarios WHERE nome_usuario = ?",
                (nome_usuario,)
            )
            resultado = cursor.fetchone()

        if resultado is None:
            return None

        user_id, senha_hash_db = resultado[0], resultado[1]
        senha_bytes = senha_texto_puro.encode('utf-8')

        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            return user_id
        else:
            return None
    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return None

# --- Funções de Gerenciamento de Fichas ---

def criar_nova_ficha(usuario_id, nome_personagem, classe, raca, antecedente, atributos, pericias):
    """Insere uma nova ficha de personagem completa no banco de dados."""
    try:
        atributos_str_json = json.dumps(atributos)
        pericias_str_json = json.dumps(pericias)
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO fichas_personagem (usuario_id, nome_personagem, classe, raca, antecedente, nivel, atributos_json, pericias_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (usuario_id, nome_personagem, classe, raca, antecedente, 1, atributos_str_json, pericias_str_json)
            )
        return True
    except Exception as e:
        print(f"Erro ao criar nova ficha: {e}")
        return False

def atualizar_ficha(ficha_id, usuario_id, novos_dados):
    """Atualiza os dados de uma ficha existente no banco de dados."""
    try:
        atributos_str_json = json.dumps(novos_dados['atributos'])
        pericias_str_json = json.dumps(novos_dados['pericias'])
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE fichas_personagem 
                SET nome_personagem = ?, classe = ?, raca = ?, antecedente = ?, 
                    nivel = ?, atributos_json = ?, pericias_json = ?
                WHERE id = ? AND usuario_id = ?
            """, (
                novos_dados['nome_personagem'], novos_dados['classe'], novos_dados['raca'],
                novos_dados['antecedente'], novos_dados['nivel'], atributos_str_json,
                pericias_str_json, ficha_id, usuario_id
            ))
            if cursor.rowcount == 0:
                return False
        return True
    except Exception as e:
        print(f"Erro ao atualizar ficha: {e}")
        return False

# --- CORREÇÃO DE INDENTAÇÃO ---
# Esta função estava indentada dentro de 'buscar_historico_chat'.
# Foi movida para o nível principal (sem recuo).
def apagar_ficha(ficha_id, usuario_id):
    """Apaga uma ficha do banco de dados, verificando se pertence ao usuário correto."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            if cursor.rowcount == 0:
                return False
        return True
    except Exception as e:
        print(f"Erro ao apagar ficha: {e}")
        return False

# --- Funções de Gerenciamento de Salas ---

def criar_nova_sala(nome_sala, senha, mestre_id):
    """Cria uma nova sala de campanha no banco de dados."""
    try:
        senha_hash = None
        if senha:
            senha_bytes = senha.encode('utf-8')
            senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO salas (nome, senha_hash, mestre_id) VALUES (?, ?, ?)",
                (nome_sala, senha_hash, mestre_id)
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao criar nova sala: {e}")
        return False

def listar_salas_disponiveis():
    """Busca todas as salas e o nome do Mestre de cada uma."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT s.id, s.nome, u.nome_usuario as mestre_nome, s.senha_hash IS NOT NULL as tem_senha
                FROM salas s
                JOIN usuarios u ON s.mestre_id = u.id
            """)
            salas = [dict(row) for row in cursor.fetchall()]
            return salas
    except Exception as e:
        print(f"Erro ao listar salas: {e}")
        return []

def verificar_senha_da_sala(sala_id, senha_texto_puro):
    """Verifica se a senha fornecida para uma sala corresponde ao hash no DB."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT senha_hash FROM salas WHERE id = ?",
                (sala_id,)
            )
            resultado = cursor.fetchone()
        if not resultado or not resultado[0]:
            return False
        senha_hash_db = resultado[0]
        senha_bytes = senha_texto_puro.encode('utf-8')
        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            return True
        else:
            return False
    except Exception as e:
        print(f"Erro ao verificar senha da sala: {e}")
        return False
        
        # --- NOVA FUNÇÃO PARA BUSCAR NOME DA FICHA ---
def buscar_dados_essenciais_ficha(ficha_id, usuario_id):
    """Busca o nome e a classe de uma ficha específica, verificando a posse."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT nome_personagem, classe FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            ficha = cursor.fetchone()
            if ficha:
                return dict(ficha)
            return None
    except Exception as e:
        print(f"Erro ao buscar dados essenciais da ficha: {e}")
        return None
    
# --- Funções para Histórico de Chat ---

def salvar_mensagem_chat(sala_id, remetente, mensagem):
    """Salva uma nova mensagem no histórico da sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO historico_chat (sala_id, remetente, mensagem) VALUES (?, ?, ?)",
                (sala_id, remetente, mensagem)
            )
        return True
    except Exception as e:
        print(f"Erro ao salvar mensagem do chat: {e}")
        return False

def buscar_historico_chat(sala_id):
    """Busca todas as mensagens do histórico de uma sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT remetente, mensagem FROM historico_chat WHERE sala_id = ? ORDER BY timestamp ASC",
                (sala_id,)
            )
            historico = [f"[{remetente}]: {mensagem}" for remetente, mensagem in cursor.fetchall()]
            return historico
    except Exception as e:
        print(f"Erro ao buscar histórico do chat: {e}")
        return []