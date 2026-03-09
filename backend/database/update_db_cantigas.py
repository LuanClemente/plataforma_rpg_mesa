import sqlite3
import os

# Caminho do Banco de Dados
script_dir = os.path.dirname(os.path.abspath(__file__))
NOME_DB = os.path.join(script_dir, 'campanhas.db')

def atualizar_banco():
    print(f"Conectando ao banco: {NOME_DB}")
    conexao = sqlite3.connect(NOME_DB)
    cursor = conexao.cursor()

    # 1. Adicionar coluna 'tempo_aventura_segundos' na tabela 'usuarios'
    try:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN tempo_aventura_segundos INTEGER DEFAULT 0")
        print("Coluna 'tempo_aventura_segundos' adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("Coluna 'tempo_aventura_segundos' já existe.")
        else:
            print(f"Erro ao adicionar coluna: {e}")

    # 2. Criar tabela 'historico_salas'
    print("Criando tabela 'historico_salas'...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historico_salas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        sala_id INTEGER NOT NULL,
        ficha_id INTEGER,
        data_acesso DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
        FOREIGN KEY (sala_id) REFERENCES salas (id),
        FOREIGN KEY (ficha_id) REFERENCES fichas_personagem (id)
    );
    """)
    print("Tabela 'historico_salas' verificada/criada com sucesso!")

    conexao.commit()
    conexao.close()
    print("Atualização do banco de dados concluída.")

if __name__ == "__main__":
    atualizar_banco()
