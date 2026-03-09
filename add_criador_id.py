"""
Rode UMA VEZ para adicionar coluna criador_id na tabela monstros_base:
  venv\Scripts\python.exe add_criador_id.py
"""
import sqlite3, os
db = os.path.join('backend', 'database', 'campanhas.db')
conn = sqlite3.connect(db)
try:
    conn.execute("ALTER TABLE monstros_base ADD COLUMN criador_id INTEGER DEFAULT NULL")
    conn.commit()
    print("✅ Coluna criador_id adicionada!")
except Exception as e:
    print(f"(já existe ou erro: {e})")
conn.close()
