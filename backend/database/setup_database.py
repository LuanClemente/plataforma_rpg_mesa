# backend/database/setup_database.py

import sqlite3
import os

# O objetivo deste script é criar e configurar o banco de dados inicial.
# Ele deve ser executado apenas uma vez ou sempre que você quiser resetar o banco de dados.

def criar_banco_de_dados():
    """
    Cria o arquivo de banco de dados e todas as tabelas necessárias para o jogo.
    Se o banco de dados já existir, ele será sobrescrito (CUIDADO!).
    """
    # Define o caminho para o arquivo do banco de dados na mesma pasta deste script.
    db_path = os.path.join(os.path.dirname(__file__), 'campanhas.db')

    # Se o arquivo já existe, remove para garantir uma criação limpa.
    # Comente a linha abaixo se não quiser que o banco seja resetado toda vez.
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Banco de dados existente '{db_path}' removido.")

    # Conecta ao banco de dados (isso criará o arquivo .db se ele não existir).
    conexao = sqlite3.connect(db_path)
    cursor = conexao.cursor()
    print("Banco de dados criado/conectado com sucesso.")

    # --- Criar Tabela de Monstros ---
    # A coluna 'nome' é UNIQUE para evitar monstros duplicados com o mesmo nome.
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
    print("Tabela 'monstros_base' criada.")

    # --- Criar Tabela de Itens ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        tipo TEXT NOT NULL,
        descricao TEXT,
        preco_ouro INTEGER NOT NULL,
        dano_dado TEXT,
        bonus_ataque INTEGER,
        efeito TEXT
    );
    """)
    print("Tabela 'itens_base' criada.")

    # --- Criar Tabela de Habilidades ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habilidades_base (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        efeito TEXT NOT NULL,
        custo_mana INTEGER NOT NULL
    );
    """)
    print("Tabela 'habilidades_base' criada.")

    # Salva as alterações e fecha a conexão.
    conexao.commit()
    conexao.close()
    print("\nConfiguração do banco de dados concluída com sucesso!")

if __name__ == "__main__":
    # Este bloco só é executado quando o script é rodado diretamente.
    criar_banco_de_dados()