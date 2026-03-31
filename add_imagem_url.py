"""
Adiciona coluna imagem_url na tabela monstros_base.
Execute UMA VEZ:
  venv\Scripts\python.exe add_imagem_url.py
"""
import sqlite3, os
DB = os.path.join('backend', 'database', 'campanhas.db')
conn = sqlite3.connect(DB)
cur  = conn.cursor()
cur.execute("PRAGMA table_info(monstros_base)")
cols = [r[1] for r in cur.fetchall()]
if 'imagem_url' not in cols:
    cur.execute("ALTER TABLE monstros_base ADD COLUMN imagem_url TEXT DEFAULT NULL")
    conn.commit()
    print("✅ Coluna imagem_url adicionada!")
else:
    print("✅ Coluna imagem_url já existe.")
conn.close()