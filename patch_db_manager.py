# -*- coding: utf-8 -*-
"""
Adiciona funcoes ausentes no db_manager.py sem quebrar nada.
Execute UMA VEZ:
  venv\\Scripts\\python.exe patch_db_manager.py
"""
import os, re

CAMINHO = os.path.join('backend', 'database', 'db_manager.py')

with open(CAMINHO, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# ─── 1. buscar_todos_os_monstros com filtros ─────────────────────────────────
ANTIGA = '''def buscar_todos_os_monstros():
    """Busca todos os monstros da tabela 'monstros_base'."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar todos os monstros: {e}")
        return []'''

NOVA = '''def buscar_todos_os_monstros(nome=None, oficial=None, tipo=None, criador_id=None):
    """Busca monstros com filtros opcionais."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            query = "SELECT * FROM monstros_base WHERE 1=1"
            params = []
            if nome:
                query += " AND nome LIKE ?"
                params.append(f"%{nome}%")
            if oficial is not None:
                query += " AND oficial = ?"
                params.append(int(oficial))
            if tipo:
                query += " AND tipo LIKE ?"
                params.append(f"%{tipo}%")
            if criador_id:
                query += " AND criador_id = ?"
                params.append(int(criador_id))
            query += " ORDER BY nome LIMIT 200"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstros: {e}")
        return []

def buscar_monstro_por_id(monstro_id):
    """Busca um monstro completo por ID."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base WHERE id = ?", (monstro_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Erro buscar monstro por id: {e}")
        return None

def buscar_tipos_monstros():
    """Retorna lista de tipos unicos para filtro."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT DISTINCT tipo FROM monstros_base WHERE tipo IS NOT NULL ORDER BY tipo"
            )
            return [row[0] for row in cursor.fetchall() if row[0]]
    except sqlite3.Error as e:
        return []'''

if ANTIGA in conteudo:
    conteudo = conteudo.replace(ANTIGA, NOVA)
    print("OK: buscar_todos_os_monstros atualizada + 2 funcoes novas adicionadas")
elif 'def buscar_monstro_por_id' in conteudo:
    print("OK: buscar_monstro_por_id ja existe, nada a fazer")
else:
    # Inserir antes do CRUD de monstros
    inserir_antes = '# --- INÍCIO - CRUD DE MONSTROS'
    if inserir_antes not in conteudo:
        inserir_antes = 'def criar_novo_monstro'
    extras = '''
def buscar_monstro_por_id(monstro_id):
    """Busca um monstro completo por ID."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base WHERE id = ?", (monstro_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Erro buscar monstro por id: {e}")
        return None

def buscar_tipos_monstros():
    """Retorna lista de tipos unicos para filtro."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT DISTINCT tipo FROM monstros_base WHERE tipo IS NOT NULL ORDER BY tipo"
            )
            return [row[0] for row in cursor.fetchall() if row[0]]
    except sqlite3.Error as e:
        return []

'''
    conteudo = conteudo.replace(inserir_antes, extras + inserir_antes)
    print("OK: funcoes inseridas antes do CRUD")

# ─── 2. buscar_item_por_id e buscar_categorias_itens ─────────────────────────
for fn, impl in [
    ('buscar_item_por_id', '''
def buscar_item_por_id(item_id):
    """Busca um item completo por ID."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM itens_base WHERE id = ?", (item_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as e:
        return None
'''),
    ('buscar_categorias_itens', '''
def buscar_categorias_itens():
    """Retorna categorias unicas de itens."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT DISTINCT categoria FROM itens_base WHERE categoria IS NOT NULL ORDER BY categoria"
            )
            return [r[0] for r in cursor.fetchall() if r[0]]
    except Exception:
        return []
'''),
]:
    if f'def {fn}' not in conteudo:
        conteudo += impl
        print(f"OK: {fn} adicionada no final")
    else:
        print(f"OK: {fn} ja existe")

with open(CAMINHO, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("\nPatch concluido! Rode o servidor novamente.")