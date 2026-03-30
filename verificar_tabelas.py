import sqlite3

NOME_DB = 'backend/database/campanhas.db'

try:
    conn = sqlite3.connect(NOME_DB)
    cursor = conn.cursor()
    
    # Verificar se a tabela historico_salas existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='historico_salas'")
    existe = cursor.fetchone()
    
    if existe:
        print("✓ Tabela 'historico_salas' EXISTE")
        
        # Mostrar estrutura da tabela
        cursor.execute("PRAGMA table_info(historico_salas)")
        colunas = cursor.fetchall()
        print("\nColunas:")
        for col in colunas:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("✗ Tabela 'historico_salas' NÃO EXISTE")
    
    conn.close()
    
except Exception as e:
    print(f"Erro: {e}")
