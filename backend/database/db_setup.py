# database/db_setup.py

# Importa as bibliotecas necessárias para interagir com o banco de dados e o sistema de arquivos.
import sqlite3
import os

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
script_dir = os.path.dirname(os.path.abspath(__file__))
os.makedirs(script_dir, exist_ok=True) 
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# --- ETAPA DE DEMOLIÇÃO (GARANTIA DE LIMPEZA) ---
# Remove o banco de dados antigo para garantir uma reconstrução limpa.
if os.path.exists(NOME_DB):
    os.remove(NOME_DB)
    print(f"AVISO: Arquivo de banco de dados antigo '{NOME_DB}' encontrado e removido.")
    print("Iniciando reconstrução do zero...")

# --- ETAPA DE CONSTRUÇÃO ---
conexao = sqlite3.connect(NOME_DB)
cursor = conexao.cursor()

print("\n--- Criando Tabelas ---")

# --- Tabelas "Mãe" (Sem dependências externas) ---

cursor.execute("""
CREATE TABLE monstros_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, vida_maxima INTEGER NOT NULL,
    ataque_bonus INTEGER NOT NULL, dano_dado TEXT NOT NULL, defesa INTEGER NOT NULL,
    xp_oferecido INTEGER NOT NULL, ouro_drop INTEGER NOT NULL
);
""")
print("Tabela 'monstros_base' criada com sucesso!")

cursor.execute("""
CREATE TABLE itens_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, tipo TEXT NOT NULL,
    descricao TEXT, preco_ouro INTEGER NOT NULL, dano_dado TEXT,
    bonus_ataque INTEGER DEFAULT 0, efeito TEXT
);
""")
print("Tabela 'itens_base' criada com sucesso!")

cursor.execute("""
CREATE TABLE habilidades_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL UNIQUE, descricao TEXT,
    efeito TEXT NOT NULL, custo_mana INTEGER NOT NULL DEFAULT 0
);
""")
print("Tabela 'habilidades_base' criada com sucesso!")

cursor.execute("""
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nome_usuario TEXT NOT NULL UNIQUE, senha_hash TEXT NOT NULL
);
""")
print("Tabela 'usuarios' (Mãe) criada com sucesso!")

# --- Tabelas "Filhas" (Com dependências / Foreign Keys) ---
# A ordem aqui é crucial.

cursor.execute("""
CREATE TABLE salas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    senha_hash TEXT, -- Pode ser nulo para salas públicas
    mestre_id INTEGER NOT NULL,
    FOREIGN KEY (mestre_id) REFERENCES usuarios (id) -- Depende de 'usuarios'
);
""")
print("Tabela 'salas' (Filha de usuarios) criada com sucesso!")

cursor.execute("""
CREATE TABLE fichas_personagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome_personagem TEXT NOT NULL,
    classe TEXT NOT NULL,
    raca TEXT,
    antecedente TEXT,
    nivel INTEGER NOT NULL DEFAULT 1,
    xp_atual INTEGER NOT NULL DEFAULT 0, -- Coluna de XP
    xp_proximo_nivel INTEGER NOT NULL DEFAULT 300, -- Coluna de XP
    atributos_json TEXT NOT NULL,
    pericias_json TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id) -- Depende de 'usuarios'
);
""")
print("Tabela 'fichas_personagem' (Filha de usuarios) criada com sucesso!")

cursor.execute("""
CREATE TABLE historico_chat (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sala_id INTEGER NOT NULL,
    remetente TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sala_id) REFERENCES salas (id) -- Depende de 'salas'
);
""")
print("Tabela 'historico_chat' (Filha de salas) criada com sucesso!")

cursor.execute("""
CREATE TABLE anotacoes_jogador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    sala_id INTEGER NOT NULL,
    notas TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id), -- Depende de 'usuarios'
    FOREIGN KEY (sala_id) REFERENCES salas (id), -- Depende de 'salas'
    UNIQUE(usuario_id, sala_id)
);
""")
print("Tabela 'anotacoes_jogador' (Filha de usuarios e salas) criada com sucesso!")

cursor.execute("""
CREATE TABLE inventario_sala (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ficha_id INTEGER NOT NULL,
    sala_id INTEGER NOT NULL,
    nome_item TEXT NOT NULL,
    descricao TEXT,
    FOREIGN KEY (ficha_id) REFERENCES fichas_personagem (id), -- Depende de 'fichas_personagem'
    FOREIGN KEY (sala_id) REFERENCES salas (id) -- Depende de 'salas'
);
""")
print("Tabela 'inventario_sala' (Filha de fichas e salas) criada com sucesso!")

# Salva permanentemente todas as alterações no arquivo do banco de dados.
conexao.commit()
# Encerra a conexão.
conexao.close()

print(f"\nBanco de dados '{NOME_DB}' reconstruído com sucesso.")