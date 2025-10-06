# database/db_setup.py

# Importa a biblioteca nativa do Python para interagir com bancos de dados SQLite.
import sqlite3

# Define o nome do arquivo do banco de dados, incluindo o caminho da pasta.
# Isso garante que o script funcione corretamente quando executado da raiz do 'backend'.
NOME_DB = "database/campanhas.db"

# Cria uma conexão com o banco de dados. Se o arquivo não existir, ele será criado.
conexao = sqlite3.connect(NOME_DB)

# O cursor é o objeto que usamos para executar comandos SQL no banco de dados.
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
# Informa ao usuário que a tabela foi verificada ou criada.
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
# Informa ao usuário que a tabela foi verificada ou criada.
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
# Informa ao usuário que a tabela foi verificada ou criada.
print("Tabela 'habilidades_base' verificada/criada com sucesso!")

# O comando 'commit' salva permanentemente todas as alterações feitas no banco de dados.
conexao.commit()

# O comando 'close' encerra a conexão com o banco de dados. É uma boa prática sempre fechar.
conexao.close()

# Mensagem final informando que o processo foi concluído.
print(f"Banco de dados '{NOME_DB}' verificado e atualizado.")