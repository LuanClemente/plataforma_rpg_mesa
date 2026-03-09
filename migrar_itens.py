"""
Migracao: popula 238 itens oficiais D&D na tabela itens_base.
Execute UMA VEZ:
  venv\Scripts\python.exe migrar_itens.py
"""
import sqlite3, os, openpyxl

DB   = os.path.join(os.path.dirname(__file__), 'backend', 'database', 'campanhas.db')
XLSX = os.path.join(os.path.dirname(__file__), 'equipamentos_lista.xlsx')

def migrar():
    if not os.path.exists(XLSX):
        print(f"ERRO: '{XLSX}' nao encontrado! Coloque o arquivo na raiz do projeto.")
        return

    conn = sqlite3.connect(DB)
    cur  = conn.cursor()

    # Garantir colunas novas (pode ja existir do script anterior)
    cur.execute("PRAGMA table_info(itens_base)")
    existentes = [r[1] for r in cur.fetchall()]
    for col, typedef in [
        ("categoria",    "TEXT DEFAULT 'Adventuring Gear'"),
        ("subcategoria", "TEXT DEFAULT '-'"),
        ("peso",         "REAL DEFAULT 0"),
        ("fonte",        "TEXT DEFAULT 'Custom'"),
        ("oficial",      "INTEGER DEFAULT 0"),
        ("criador_id",   "INTEGER DEFAULT NULL"),
    ]:
        if col not in existentes:
            cur.execute(f"ALTER TABLE itens_base ADD COLUMN {col} {typedef}")
            print(f"  + Coluna adicionada: {col}")
    conn.commit()

    # Ler planilha com data_only + read_only para evitar travar em formulas
    print("Lendo planilha...")
    wb = openpyxl.load_workbook(XLSX, data_only=True, read_only=True)
    ws = wb['Master']

    inseridos = ignorados = 0
    seen = set()

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[2] or not isinstance(row[2], str):
            continue
        nome = str(row[2]).strip()
        if not nome or nome in seen or nome == 'Item':
            continue
        seen.add(nome)

        categoria    = str(row[0] or 'Adventuring Gear').strip()
        subcategoria = str(row[1] or '-').strip()
        fonte        = str(row[7] or 'PHB 2024').strip()

        try: preco = float(row[4]) if row[4] else 0
        except: preco = 0
        try: peso = float(row[3]) if row[3] and str(row[3]) != '-' else 0
        except: peso = 0

        try:
            cur.execute("""
                INSERT OR IGNORE INTO itens_base
                (nome, tipo, descricao, preco_ouro, dano_dado, bonus_ataque, efeito,
                 categoria, subcategoria, peso, fonte, oficial)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
            """, (nome, categoria, '', preco, '—', 0, '', categoria, subcategoria, peso, fonte, 1))

            if cur.rowcount > 0: inseridos += 1
            else: ignorados += 1
        except Exception as e:
            print(f"  Erro ({nome}): {e}")

    wb.close()
    conn.commit()
    conn.close()

    print(f"\nMigracao concluida!")
    print(f"   {inseridos} itens inseridos")
    print(f"   {ignorados} ignorados (ja existiam)")

if __name__ == '__main__':
    migrar()