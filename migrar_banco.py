"""
Script de migração: expande monstros_base com campos D&D e popula 802 criaturas oficiais.
Execute uma única vez:
  venv\Scripts\python.exe migrar_banco.py
"""
import sqlite3, os, openpyxl

DB = os.path.join(os.path.dirname(__file__), 'backend', 'database', 'campanhas.db')

def migrar():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # 1. Verificar se colunas novas já existem
    cur.execute("PRAGMA table_info(monstros_base)")
    colunas_existentes = [row[1] for row in cur.fetchall()]
    print("Colunas atuais:", colunas_existentes)

    novas_colunas = [
        ("tamanho",       "TEXT DEFAULT 'Medium'"),
        ("tipo",          "TEXT DEFAULT 'Unknown'"),
        ("alinhamento",   "TEXT DEFAULT '—'"),
        ("ca",            "INTEGER DEFAULT 10"),
        ("deslocamento",  "TEXT DEFAULT '30'"),
        ("for_attr",      "INTEGER DEFAULT 10"),
        ("des_attr",      "INTEGER DEFAULT 10"),
        ("con_attr",      "INTEGER DEFAULT 10"),
        ("intel_attr",    "INTEGER DEFAULT 10"),
        ("sab_attr",      "INTEGER DEFAULT 10"),
        ("car_attr",      "INTEGER DEFAULT 10"),
        ("saving_throws", "TEXT DEFAULT ''"),
        ("skills",        "TEXT DEFAULT ''"),
        ("resistencias",  "TEXT DEFAULT ''"),
        ("sentidos",      "TEXT DEFAULT ''"),
        ("idiomas",       "TEXT DEFAULT ''"),
        ("cr",            "TEXT DEFAULT '0'"),
        ("habilidades",   "TEXT DEFAULT ''"),
        ("fonte",         "TEXT DEFAULT 'Custom'"),
        ("oficial",       "INTEGER DEFAULT 0"),
    ]

    for col, typedef in novas_colunas:
        if col not in colunas_existentes:
            cur.execute(f"ALTER TABLE monstros_base ADD COLUMN {col} {typedef}")
            print(f"  + Coluna adicionada: {col}")

    conn.commit()

    # 2. Popular com criaturas do XLSX
    xlsx_path = os.path.join(os.path.dirname(__file__), 'Monster_Spreadsheet__D_D5e_.xlsx')
    if not os.path.exists(xlsx_path):
        print(f"\nERRO: Coloque o arquivo 'Monster_Spreadsheet__D_D5e_.xlsx' na pasta raiz do projeto!")
        return

    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb['Official Stats']

    def val(row, c, default=''):
        v = ws.cell(row, c).value
        if v is None or str(v).strip() in ('', 'None', 'none'): return default
        return str(v).strip()

    def intval(row, c, default=0):
        v = ws.cell(row, c).value
        try: return int(float(v)) if v is not None else default
        except: return default

    inseridos = 0
    ignorados = 0

    for row in range(2, ws.max_row + 1):
        nome = val(row, 1)
        if not nome:
            continue

        hp = intval(row, 6, 1)
        ca = intval(row, 5, 10)

        try:
            cur.execute("""
                INSERT OR IGNORE INTO monstros_base
                (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop,
                 tamanho, tipo, alinhamento, ca, deslocamento,
                 for_attr, des_attr, con_attr, intel_attr, sab_attr, car_attr,
                 saving_throws, skills, resistencias, sentidos, idiomas,
                 cr, habilidades, fonte, oficial)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                nome, hp, 0, '1d6', ca, 0, 0,
                val(row, 2, 'Medium'),
                val(row, 3, 'Unknown'),
                val(row, 4, '—'),
                ca,
                val(row, 7, '30'),
                intval(row, 8, 10), intval(row, 9, 10), intval(row, 10, 10),
                intval(row, 11, 10), intval(row, 12, 10), intval(row, 13, 10),
                val(row, 14), val(row, 15), val(row, 16),
                val(row, 17, 'Normal'), val(row, 18, '—'),
                val(row, 19, '0'), val(row, 20), val(row, 21, 'Official'),
                1
            ))
            if cur.rowcount > 0:
                inseridos += 1
            else:
                ignorados += 1
        except Exception as e:
            print(f"  Erro na linha {row} ({nome}): {e}")

    conn.commit()
    conn.close()
    print(f"\n✅ Migração concluída!")
    print(f"   {inseridos} criaturas inseridas")
    print(f"   {ignorados} ignoradas (já existiam)")

if __name__ == '__main__':
    migrar()