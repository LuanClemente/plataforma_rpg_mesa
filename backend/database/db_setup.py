# database/db_setup.py

# Importa as bibliotecas necessárias para interagir com o banco de dados e o sistema de arquivos.
import sqlite3
import os

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Garante que o caminho para o banco de dados seja sempre encontrado corretamente.
script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(script_dir, exist_ok=True) 
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# --- ETAPA DE DEMOLIÇÃO (GARANTIA DE LIMPEZA) ---
# Antes de fazer qualquer coisa, verificamos se o arquivo de banco de dados antigo existe.
if os.path.exists(NOME_DB):
    # Se existir, nós o removemos para garantir uma reconstrução limpa.
    os.remove(NOME_DB)
    print(f"AVISO: Arquivo de banco de dados antigo '{NOME_DB}' encontrado e removido.")
    print("Iniciando reconstrução do zero...")

# --- ETAPA DE CONSTRUÇÃO ---
# Agora, temos certeza de que estamos criando um arquivo novo e limpo.
conexao = sqlite3.connect(NOME_DB)
cursor = conexao.cursor()

print("\n--- Criando Tabelas ---")

# --- Tabela: monstros_base ---
cursor.execute("""
CREATE TABLE monstros_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, vida_maxima INTEGER NOT NULL,
    ataque_bonus INTEGER NOT NULL, dano_dado TEXT NOT NULL, defesa INTEGER NOT NULL,
    xp_oferecido INTEGER NOT NULL, ouro_drop INTEGER NOT NULL
);
""")
print("Tabela 'monstros_base' criada com sucesso!")

# --- Tabela: itens_base ---
cursor.execute("""
CREATE TABLE itens_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, tipo TEXT NOT NULL,
    descricao TEXT, preco_ouro INTEGER NOT NULL, dano_dado TEXT,
    bonus_ataque INTEGER DEFAULT 0, efeito TEXT
);
""")
print("Tabela 'itens_base' criada com sucesso!")

cursor.execute("""
CREATE TABLE IF NOT EXISTS salas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    senha_hash TEXT, -- Pode ser nulo para salas públicas
    mestre_id INTEGER NOT NULL,
    FOREIGN KEY (mestre_id) REFERENCES usuarios (id)
);
""")
print("Tabela 'salas' verificada/criada com sucesso!")

# --- Tabela: habilidades_base ---
cursor.execute("""
CREATE TABLE habilidades_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT,
    efeito TEXT NOT NULL, custo_mana INTEGER NOT NULL DEFAULT 0
);
""")
print("Tabela 'habilidades_base' criada com sucesso!")

# --- Tabela: usuarios ---
cursor.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome_usuario TEXT NOT NULL UNIQUE, senha_hash TEXT NOT NULL
);
""")
print("Tabela 'usuarios' criada com sucesso!")

# --- TABELA: historico_chat ---
# Armazena todas as mensagens e eventos de cada sala.
cursor.execute("""
CREATE TABLE IF NOT EXISTS historico_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    remetente TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas (id)
);
""")
print("Tabela 'historico_chat' verificada/criada com sucesso!")

# --- Tabela: fichas_personagem (COM A COLUNA FALTANDO ADICIONADA) ---
cursor.execute("""
CREATE TABLE fichas_personagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome_personagem TEXT NOT NULL,
    classe TEXT NOT NULL,
    raca TEXT,
    antecedente TEXT,
    nivel INTEGER NOT NULL DEFAULT 1,
    atributos_json TEXT NOT NULL,
    pericias_json TEXT,  -- <-- A COLUNA QUE FALTAVA FOI ADICIONADA AQUI!
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);
""")
print("Tabela 'fichas_personagem' criada com sucesso!")

# Salva permanentemente todas as alterações no arquivo do banco de dados.
conexao.commit()
# Encerra a conexão.
conexao.close()

print(f"\nBanco de dados '{NOME_DB}' reconstruído com sucesso.")