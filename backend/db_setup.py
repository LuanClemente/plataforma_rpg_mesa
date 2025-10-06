# db_setup.py

# Importa a biblioteca para interagir com o banco de dados SQLite.
import sqlite3

# Define o nome do arquivo que será o nosso banco de dados.
NOME_DB = "campanhas.db"

# Cria uma conexão com o banco de dados.
# Se o arquivo não existir, ele será criado automaticamente.
conexao = sqlite3.connect(NOME_DB)

# Cria um "cursor". Pense no cursor como a mão que vai escrever e ler
# os comandos e dados no banco de dados.
cursor = conexao.cursor()

# --- CRIAÇÃO DA TABELA DE MONSTROS PADRÃO ---
# Aqui, usamos a linguagem SQL (Structured Query Language) para dar comandos ao DB.
# 'CREATE TABLE IF NOT EXISTS' cria a tabela apenas se ela ainda não existir.
# Isso evita erros se rodarmos o script mais de uma vez.
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
# Explicação das colunas:
# id: Um número de identificação único para cada monstro (gerado automaticamente).
# nome: O nome do monstro (não pode se repetir).
# TEXT: Significa que o campo guarda texto.
# INTEGER: Significa que o campo guarda um número inteiro.
# NOT NULL: Garante que o campo não pode ser deixado em branco.

print("Tabela 'monstros_base' criada com sucesso!")

# --- AQUI PODERÍAMOS CRIAR OUTRAS TABELAS (itens_base, etc.) ---
# Por agora, vamos focar apenas nos monstros.

# O comando 'commit' salva permanentemente todas as mudanças que fizemos.
conexao.commit()

# É uma boa prática sempre fechar a conexão quando terminamos de usá-la.
conexao.close()

print(f"Banco de dados '{NOME_DB}' configurado.")