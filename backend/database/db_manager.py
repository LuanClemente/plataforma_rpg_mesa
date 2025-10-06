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
    e retorna um objeto Monstro totalmente instanciado e pronto para o combate.
    """
    # O bloco 'try...except' garante que, se houver um erro de banco de dados, o programa não irá quebrar.
    try:
        # Estabelece a conexão com o arquivo do banco de dados usando o caminho absoluto.
        conexao = sqlite3.connect(NOME_DB)
        # Cria o cursor para executar comandos.
        cursor = conexao.cursor()
        # Executa uma consulta SQL para buscar um monstro aleatório.
        cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
        # 'fetchone()' busca apenas um resultado da consulta.
        dados_monstro = cursor.fetchone()
        # Fecha a conexão para liberar o recurso.
        conexao.close()
        # Verifica se um monstro foi realmente encontrado (a tabela poderia estar vazia).
        if dados_monstro:
            # "Hidrata" um objeto Monstro: cria uma instância da classe usando os dados da tupla do DB.
            monstro_encontrado = Monstro(
                nome=dados_monstro[1], vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3], dano_dado=dados_monstro[4],
                defesa=dados_monstro[5], xp_oferecido=dados_monstro[6],
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
    """Busca todos os itens da tabela 'itens_base' para serem usados, por exemplo, na loja."""
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
    """Busca no banco de dados os detalhes de uma lista específica de nomes de itens."""
    if not nomes_dos_itens:
        return []
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Prepara os placeholders ('?') para a consulta. Teremos um '?' para cada nome na lista.
        placeholders = ', '.join('?' for _ in nomes_dos_itens)
        # A cláusula 'WHERE nome IN (...)' busca todas as linhas cujo nome está na lista fornecida.
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
    """Busca no banco de dados os detalhes de uma lista específica de nomes de habilidades."""
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

def buscar_todos_os_monstros():
    """Busca todos os monstros da tabela 'monstros_base'."""
    try:
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Executa a consulta SQL para selecionar todas as colunas de todos os monstros, ordenados por nome.
        cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
        # Pega todos os resultados.
        monstros = cursor.fetchall()
        # Fecha a conexão.
        conexao.close()
        # Retorna a lista de monstros.
        return monstros
    except sqlite3.Error as e:
        # Em caso de erro, imprime a mensagem e retorna uma lista vazia.
        print(f"Erro ao buscar todos os monstros: {e}")
        return []

# A função abaixo estava indentada incorretamente. Agora está no nível correto.
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
        print(f"Tentativa de registrar usuário já existente: {nome_usuario}")
        return False
    except Exception as e:
        # Captura qualquer outro erro que possa acontecer durante o processo.
        print(f"Erro ao registrar novo usuário: {e}")
        return False