# database/db_manager.py

# Importa a biblioteca para interagir com o banco de dados SQLite.
import sqlite3
# Importa a biblioteca 'os' para nos ajudar a construir caminhos de arquivo robustos.
import os
# Importa a classe 'Monstro' para que possamos criar um objeto Monstro com os dados do DB.
from core.monstro import Monstro
# Importa a biblioteca 'bcrypt' para lidar com a segurança das senhas.
import bcrypt

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Descobre o caminho absoluto para a pasta onde este script está localizado (a pasta 'database').
script_dir = os.path.dirname(os.path.abspath(__file__))
# Constrói o caminho para o arquivo do banco de dados, garantindo que ele seja encontrado
# independentemente de onde o programa que chama este módulo foi executado.
NOME_DB = os.path.join(script_dir, 'campanhas.db')


def buscar_monstro_aleatorio():
    """
    Conecta ao banco de dados, busca um monstro aleatório da tabela 'monstros_base'
    e retorna um objeto Monstro totalmente instanciado.
    """
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
        dados_monstro = cursor.fetchone()
        conexao.close()
        if dados_monstro:
            monstro_encontrado = Monstro(
                nome=dados_monstro[1], vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3], dano_dado=dados_monstro[4],
                defesa=dados_monstro[5], xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
            return monstro_encontrado
        else:
            return None
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        return None

def buscar_todos_os_itens():
    """Busca todos os itens da tabela 'itens_base' para serem usados na loja."""
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM itens_base ORDER BY preco_ouro")
        itens = cursor.fetchall()
        conexao.close()
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens no banco de dados: {e}")
        return []

def buscar_detalhes_itens(nomes_dos_itens: list):
    """Busca no banco de dados os detalhes de uma lista específica de nomes de itens."""
    if not nomes_dos_itens:
        return []
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        placeholders = ', '.join('?' for _ in nomes_dos_itens)
        query = f"SELECT * FROM itens_base WHERE nome IN ({placeholders})"
        cursor.execute(query, nomes_dos_itens)
        itens = cursor.fetchall()
        conexao.close()
        return itens
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de itens: {e}")
        return []

def buscar_detalhes_habilidades(nomes_das_habilidades: list):
    """Busca no banco de dados os detalhes de uma lista específica de nomes de habilidades."""
    if not nomes_das_habilidades:
        return []
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        placeholders = ', '.join('?' for _ in nomes_das_habilidades)
        query = f"SELECT * FROM habilidades_base WHERE nome IN ({placeholders})"
        cursor.execute(query, nomes_das_habilidades)
        habilidades = cursor.fetchall()
        conexao.close()
        return habilidades
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de habilidades: {e}")
        return []

def buscar_todos_os_monstros():
    """Busca todos os monstros da tabela 'monstros_base'."""
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
        monstros = cursor.fetchall()
        conexao.close()
        return monstros
    except sqlite3.Error as e:
        print(f"Erro ao buscar todos os monstros: {e}")
        return []

def registrar_novo_usuario(nome_usuario, senha_texto_puro):
    """
    Cria o hash da senha e insere um novo usuário no banco de dados.
    Retorna True em caso de sucesso, False em caso de falha (ex: usuário já existe).
    """
    try:
        # Transforma a senha (string) em bytes (padrão utf-8), que é o formato que o bcrypt espera.
        senha_bytes = senha_texto_puro.encode('utf-8')
        # Gera o "sal" e cria o hash da senha. O hash é um código irreversível gerado a partir da senha.
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())

        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Insere o nome de usuário e a SENHA HASHEADA (não a senha original!) na tabela.
        cursor.execute(
            "INSERT INTO usuarios (nome_usuario, senha_hash) VALUES (?, ?)",
            (nome_usuario, senha_hash)
        )
        conexao.commit()
        conexao.close()
        # Se chegou até aqui, o registro foi bem-sucedido.
        return True
    except sqlite3.IntegrityError:
        # Este erro acontece se o 'nome_usuario' já existir (devido à restrição UNIQUE na tabela).
        return False
    except Exception as e:
        # Captura qualquer outro erro que possa acontecer durante o processo.
        print(f"Erro ao registrar novo usuário: {e}")
        return False

# --- FUNÇÃO CORRIGIDA ---
# A indentação desta função foi corrigida. Ela agora está no nível principal do arquivo.
def verificar_login(nome_usuario, senha_texto_puro):
    """
    Verifica se o nome de usuário existe e se a senha fornecida corresponde ao hash no banco de dados.
    Retorna True se o login for válido, False caso contrário.
    """
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()

        # Busca o hash da senha para o nome de usuário fornecido.
        cursor.execute(
            "SELECT senha_hash FROM usuarios WHERE nome_usuario = ?",
            (nome_usuario,) # A vírgula é importante para que o Python entenda que é uma tupla de um elemento.
        )
        resultado = cursor.fetchone() # Pega o primeiro (e único) resultado.
        conexao.close()

        # Se 'resultado' for None, significa que o usuário não foi encontrado.
        if resultado is None:
            return False

        # Extrai o hash da senha (que está no primeiro índice da tupla).
        senha_hash_db = resultado[0]
        # Transforma a senha que o usuário digitou em bytes.
        senha_bytes = senha_texto_puro.encode('utf-8')

        # A MÁGICA DO BCRYPT: bcrypt.checkpw() compara a senha em texto puro com o hash do banco de dados.
        # Retorna True se corresponderem, False caso contrário. É a forma segura de verificar senhas.
        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            # A senha está correta! Login válido.
            return True
        else:
            # A senha está incorreta. Login inválido.
            return False
            
    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return False