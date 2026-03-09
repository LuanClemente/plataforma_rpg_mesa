# Este é um script utilitário para ser executado manualmente no terminal.
# Ele promove um usuário ao role 'mestre' no banco de dados.

import sqlite3
import sys
import os

# --- Lógica de Caminho ---
# (Esta lógica encontra o caminho para o script atual)
script_dir = os.path.dirname(os.path.abspath(__file__)) 

# CORREÇÃO 1: O NOME DO BANCO DE DADOS
# Atualizamos o nome do arquivo .db para 'campanhas.db', 
# exatamente como está no seu db_setup.py.
# O caminho agora é: backend/utils/ -> (sobe para 'backend') -> 
# entra em 'database' -> acessa 'campanhas.db'
DB_PATH = os.path.join(script_dir, '..', 'database', 'campanhas.db')

def promote_user(username):
    """
    Atualiza o 'role' de um usuário para 'mestre' no banco de dados.
    (O parâmetro 'username' aqui é o nome que você digita no terminal)
    """
    
    # Validação inicial: Verifica se o nome de usuário foi fornecido
    if not username:
        print("Erro: Nenhum nome de usuário fornecido.")
        print("Uso: python -m utils.promote_user <nome_do_usuario>")
        return

    conn = None
    try:
        # 1. Conecta ao banco de dados (agora no caminho correto)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # CORREÇÃO 2: O NOME DA COLUNA
        # Atualizamos a consulta SQL para usar 'nome_usuario' 
        # em vez de 'username'.
        # O '?' será substituído pelo 'username' que você passou como argumento.
        cursor.execute("SELECT * FROM usuarios WHERE nome_usuario = ?", (username,))
        user = cursor.fetchone()

        if user:
            # 3. Se o usuário existir, atualiza o 'role' dele para 'mestre'
            # (Usando 'nome_usuario' aqui também)
            cursor.execute("UPDATE usuarios SET role = 'mestre' WHERE nome_usuario = ?", (username,))
            conn.commit()
            print(f"Sucesso! O usuário '{username}' foi promovido a Mestre.")
        else:
            # 4. Se não existir, informa o erro
            print(f"Erro: Usuário '{username}' não encontrado no banco de dados.")

    except sqlite3.Error as e:
        print(f"Ocorreu um erro no banco de dados: {e}")
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro
            
    finally:
        if conn:
            conn.close() # Sempre fecha a conexão

# Bloco de execução principal (continua o mesmo)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        username_to_promote = sys.argv[1]
        promote_user(username_to_promote)
    else:
        print("Erro: Forneça o nome de usuário que deseja promover.")
        print("Uso: python -m utils.promote_user <nome_do_usuario>")