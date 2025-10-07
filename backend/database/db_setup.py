# database/db_setup.py

# Importa as bibliotecas necessárias para interagir com o banco de dados e o sistema de arquivos.
import sqlite3
import os

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Pega o caminho absoluto da pasta onde este script está (a pasta 'database').
script_dir = os.path.dirname(os.path.abspath(__file__))
# Garante que a pasta 'database' exista. 'exist_ok=True' faz com que não dê erro se a pasta já foi criada.
os.makedirs(script_dir, exist_ok=True) 
# O nome do DB agora é construído a partir deste caminho seguro, garantindo que o arquivo seja criado no lugar certo.
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# Estabelece a conexão com o arquivo do banco de dados.
conexao = sqlite3.connect(NOME_DB)
# O cursor é o objeto que usamos para executar comandos SQL.
cursor = conexao.cursor()

# --- Tabela: monstros_base ---
# Armazena a biblioteca de todos os monstros possíveis.
cursor.execute("""
CREATE TABLE IF NOT EXISTS monstros_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    vida_maxima INTEGER NOT NULL,
    ataque_bonus INTEGER NOT NULL,
    dano_dado TEXT NOT NULL,
    defesa INTEGER NOT NULL,
    xp_oferecido INTEGER NOT NULL,
    ouro_drop INTEGER NOT NULL
);
""")
print("Tabela 'monstros_base' verificada/criada com sucesso!")

# --- Tabela: itens_base ---
# Armazena a biblioteca de todos os itens possíveis.
cursor.execute("""
CREATE TABLE IF NOT EXISTS itens_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL,
    descricao TEXT,
    preco_ouro INTEGER NOT NULL,
    dano_dado TEXT,
    bonus_ataque INTEGER DEFAULT 0,
    efeito TEXT
);
""")
print("Tabela 'itens_base' verificada/criada com sucesso!")

# --- Tabela: habilidades_base ---
# Armazena a biblioteca de todas as magias e habilidades possíveis.
cursor.execute("""
CREATE TABLE IF NOT EXISTS habilidades_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    efeito TEXT NOT NULL,
    custo_mana INTEGER NOT NULL DEFAULT 0
);
""")
print("Tabela 'habilidades_base' verificada/criada com sucesso!")

# --- Tabela: usuarios ---
# Armazena os dados de login dos usuários da plataforma.
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_usuario TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL
);
""")
print("Tabela 'usuarios' verificada/criada com sucesso!")

# O comando 'commit' salva permanentemente todas as alterações (criação de tabelas) no banco de dados.
conexao.commit()

# O comando 'close' encerra a conexão com o banco de dados.
conexao.close()

# Mensagem final informando que o processo foi concluído.
print(f"Banco de dados '{NOME_DB}' configurado com sucesso.")