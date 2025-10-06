import sqlite3
import os

# Pega o caminho absoluto da pasta onde o script está (a pasta 'database').
script_dir = os.path.dirname(os.path.abspath(__file__))
# Garante que a pasta exista. 'exist_ok=True' faz com que não dê erro se a pasta já existir.
os.makedirs(script_dir, exist_ok=True) 
# O nome do DB agora é construído a partir deste caminho seguro.
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# O resto do código é o mesmo
conexao = sqlite3.connect(NOME_DB)
cursor = conexao.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS monstros_base (...);
""")
print("Tabela 'monstros_base' verificada/criada com sucesso!")

cursor.execute("""
CREATE TABLE IF NOT EXISTS itens_base (...);
""")
print("Tabela 'itens_base' verificada/criada com sucesso!")

cursor.execute("""
CREATE TABLE IF NOT EXISTS habilidades_base (...);
""")
print("Tabela 'habilidades_base' criada com sucesso!")

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_usuario TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL
);
""")
print("Tabela 'usuarios' verificada/criada com sucesso!")

conexao.commit()
conexao.close()
print(f"Banco de dados '{NOME_DB}' configurado.")