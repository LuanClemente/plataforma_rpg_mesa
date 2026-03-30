# -*- coding: utf-8 -*-
"""
Funcoes do banco para o Esconderijo do Mestre.
Adicione ao db_manager.py ou importe separadamente.
"""
import sqlite3, os

NOME_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'campanhas.db')

def _db():
    conn = sqlite3.connect(NOME_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ─── CAMPANHAS ────────────────────────────────────────────────────────────────
def listar_campanhas(criador_id):
    with _db() as c:
        rows = c.execute(
            "SELECT * FROM campanhas_mestre WHERE criador_id=? ORDER BY atualizado_em DESC",
            (criador_id,)
        ).fetchall()
        return [dict(r) for r in rows]

def buscar_campanha(campanha_id, criador_id=None):
    with _db() as c:
        q = "SELECT * FROM campanhas_mestre WHERE id=?"
        params = [campanha_id]
        if criador_id:
            q += " AND criador_id=?"
            params.append(criador_id)
        r = c.execute(q, params).fetchone()
        return dict(r) if r else None

def criar_campanha(criador_id, dados):
    with _db() as c:
        cur = c.execute("""
            INSERT INTO campanhas_mestre
            (criador_id, nome, descricao, historia, tom, nivel_min, nivel_max, sistema)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            criador_id,
            dados.get('nome','Nova Campanha'),
            dados.get('descricao',''),
            dados.get('historia',''),
            dados.get('tom','Epico'),
            dados.get('nivel_min',1),
            dados.get('nivel_max',20),
            dados.get('sistema','D&D 5e'),
        ))
        return buscar_campanha(cur.lastrowid)

def atualizar_campanha(campanha_id, criador_id, dados):
    campos = ['nome','descricao','historia','tom','nivel_min','nivel_max','sistema','status']
    sets   = ', '.join(f"{c}=?" for c in campos if c in dados)
    vals   = [dados[c] for c in campos if c in dados]
    if not sets: return None
    vals  += [campanha_id, criador_id]
    with _db() as c:
        c.execute(f"UPDATE campanhas_mestre SET {sets}, atualizado_em=datetime('now') WHERE id=? AND criador_id?", vals)
    return buscar_campanha(campanha_id)

def deletar_campanha(campanha_id, criador_id):
    with _db() as c:
        r = c.execute("DELETE FROM campanhas_mestre WHERE id=? AND criador_id=?", (campanha_id, criador_id))
        return r.rowcount > 0

# ─── GENÉRICO para sub-recursos ───────────────────────────────────────────────
def _listar(tabela, campanha_id):
    with _db() as c:
        rows = c.execute(f"SELECT * FROM {tabela} WHERE campanha_id=? ORDER BY id", (campanha_id,)).fetchall()
        return [dict(r) for r in rows]

def _buscar(tabela, item_id):
    with _db() as c:
        r = c.execute(f"SELECT * FROM {tabela} WHERE id=?", (item_id,)).fetchone()
        return dict(r) if r else None

def _deletar(tabela, item_id, campanha_id):
    with _db() as c:
        r = c.execute(f"DELETE FROM {tabela} WHERE id=? AND campanha_id=?", (item_id, campanha_id))
        return r.rowcount > 0

def _toggle_visivel(tabela, item_id, visivel):
    with _db() as c:
        c.execute(f"UPDATE {tabela} SET visivel=? WHERE id=?", (int(visivel), item_id))
    return _buscar(tabela, item_id)

# ─── MAPAS ───────────────────────────────────────────────────────────────────
def listar_mapas(campanha_id):       return _listar('campanha_mapas', campanha_id)
def buscar_mapa(mapa_id):            return _buscar('campanha_mapas', mapa_id)
def deletar_mapa(mapa_id, cid):      return _deletar('campanha_mapas', mapa_id, cid)
def toggle_mapa(mapa_id, v):         return _toggle_visivel('campanha_mapas', mapa_id, v)

def criar_mapa(campanha_id, dados):
    with _db() as c:
        cur = c.execute(
            "INSERT INTO campanha_mapas (campanha_id,nome,descricao,imagem_data,visivel,ordem) VALUES (?,?,?,?,?,?)",
            (campanha_id, dados.get('nome','Mapa'), dados.get('descricao',''),
             dados.get('imagem_data',''), 0, dados.get('ordem',0))
        )
        return buscar_mapa(cur.lastrowid)

def atualizar_mapa(mapa_id, dados):
    campos = ['nome','descricao','imagem_data','visivel','ordem']
    sets   = ', '.join(f"{c}=?" for c in campos if c in dados)
    vals   = [dados[c] for c in campos if c in dados] + [mapa_id]
    if not sets: return None
    with _db() as c:
        c.execute(f"UPDATE campanha_mapas SET {sets} WHERE id=?", vals)
    return buscar_mapa(mapa_id)

# ─── EVENTOS ─────────────────────────────────────────────────────────────────
def listar_eventos(campanha_id):     return _listar('campanha_eventos', campanha_id)
def buscar_evento(eid):              return _buscar('campanha_eventos', eid)
def deletar_evento(eid, cid):        return _deletar('campanha_eventos', eid, cid)
def toggle_evento(eid, v):           return _toggle_visivel('campanha_eventos', eid, v)

def criar_evento(campanha_id, dados):
    with _db() as c:
        cur = c.execute(
            "INSERT INTO campanha_eventos (campanha_id,titulo,descricao_pub,descricao_priv,status,visivel,ordem) VALUES (?,?,?,?,?,?,?)",
            (campanha_id, dados.get('titulo','Evento'), dados.get('descricao_pub',''),
             dados.get('descricao_priv',''), dados.get('status','futuro'), 0, dados.get('ordem',0))
        )
        return buscar_evento(cur.lastrowid)

def atualizar_evento(eid, dados):
    campos = ['titulo','descricao_pub','descricao_priv','status','visivel','ordem']
    sets   = ', '.join(f"{c}=?" for c in campos if c in dados)
    vals   = [dados[c] for c in campos if c in dados] + [eid]
    if not sets: return None
    with _db() as c:
        c.execute(f"UPDATE campanha_eventos SET {sets} WHERE id=?", vals)
    return buscar_evento(eid)

# ─── NPCS ───────────────────────────────────────────────────────────────────
def listar_npcs(campanha_id):        return _listar('campanha_npcs', campanha_id)
def buscar_npc(nid):                 return _buscar('campanha_npcs', nid)
def deletar_npc(nid, cid):           return _deletar('campanha_npcs', nid, cid)
def toggle_npc(nid, v):              return _toggle_visivel('campanha_npcs', nid, v)

def criar_npc(campanha_id, dados):
    with _db() as c:
        cur = c.execute(
            "INSERT INTO campanha_npcs (campanha_id,nome,papel,descricao_pub,descricao_priv,alinhamento,local,visivel) VALUES (?,?,?,?,?,?,?,?)",
            (campanha_id, dados.get('nome','NPC'), dados.get('papel',''),
             dados.get('descricao_pub',''), dados.get('descricao_priv',''),
             dados.get('alinhamento',''), dados.get('local',''), 0)
        )
        return buscar_npc(cur.lastrowid)

def atualizar_npc(nid, dados):
    campos = ['nome','papel','descricao_pub','descricao_priv','alinhamento','local','visivel']
    sets   = ', '.join(f"{c}=?" for c in campos if c in dados)
    vals   = [dados[c] for c in campos if c in dados] + [nid]
    if not sets: return None
    with _db() as c:
        c.execute(f"UPDATE campanha_npcs SET {sets} WHERE id=?", vals)
    return buscar_npc(nid)

# ─── QUESTS ─────────────────────────────────────────────────────────────────
def listar_quests(campanha_id):      return _listar('campanha_quests', campanha_id)
def buscar_quest(qid):               return _buscar('campanha_quests', qid)
def deletar_quest(qid, cid):         return _deletar('campanha_quests', qid, cid)
def toggle_quest(qid, v):            return _toggle_visivel('campanha_quests', qid, v)

def criar_quest(campanha_id, dados):
    with _db() as c:
        cur = c.execute(
            """INSERT INTO campanha_quests
            (campanha_id,titulo,objetivo_pub,detalhes_priv,recompensa_pub,recompensa_priv,local_priv,status,visivel)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (campanha_id, dados.get('titulo','Quest'), dados.get('objetivo_pub',''),
             dados.get('detalhes_priv',''), dados.get('recompensa_pub',''),
             dados.get('recompensa_priv',''), dados.get('local_priv',''),
             dados.get('status','ativa'), 0)
        )
        return buscar_quest(cur.lastrowid)

def atualizar_quest(qid, dados):
    campos = ['titulo','objetivo_pub','detalhes_priv','recompensa_pub','recompensa_priv','local_priv','status','visivel']
    sets   = ', '.join(f"{c}=?" for c in campos if c in dados)
    vals   = [dados[c] for c in campos if c in dados] + [qid]
    if not sets: return None
    with _db() as c:
        c.execute(f"UPDATE campanha_quests SET {sets} WHERE id=?", vals)
    return buscar_quest(qid)

# ─── ANOTAÇÕES ───────────────────────────────────────────────────────────────
def listar_anotacoes(campanha_id):   return _listar('campanha_anotacoes', campanha_id)
def buscar_anotacao(aid):            return _buscar('campanha_anotacoes', aid)
def deletar_anotacao(aid, cid):      return _deletar('campanha_anotacoes', aid, cid)
def toggle_anotacao(aid, v):         return _toggle_visivel('campanha_anotacoes', aid, v)

def criar_anotacao(campanha_id, dados):
    with _db() as c:
        cur = c.execute(
            "INSERT INTO campanha_anotacoes (campanha_id,titulo,conteudo,visivel) VALUES (?,?,?,?)",
            (campanha_id, dados.get('titulo','Anotação'), dados.get('conteudo',''), 0)
        )
        return buscar_anotacao(cur.lastrowid)

def atualizar_anotacao(aid, dados):
    campos = ['titulo','conteudo','visivel']
    sets   = ', '.join(f"{c}=?" for c in campos if c in dados)
    vals   = [dados[c] for c in campos if c in dados] + [aid]
    if not sets: return None
    with _db() as c:
        c.execute(f"UPDATE campanha_anotacoes SET {sets} WHERE id=?", vals)
    return buscar_anotacao(aid)

# ─── VÍNCULO SALA <-> CAMPANHA ────────────────────────────────────────────────
def vincular_sala_campanha(sala_id, campanha_id):
    with _db() as c:
        c.execute(
            "INSERT OR REPLACE INTO sala_campanha (sala_id, campanha_id) VALUES (?,?)",
            (sala_id, campanha_id)
        )
    return True

def buscar_campanha_da_sala(sala_id):
    with _db() as c:
        r = c.execute(
            "SELECT c.* FROM campanhas_mestre c JOIN sala_campanha s ON c.id=s.campanha_id WHERE s.sala_id=?",
            (sala_id,)
        ).fetchone()
        return dict(r) if r else None
