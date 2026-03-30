# -*- coding: utf-8 -*-
"""
Cria as tabelas do Esconderijo do Mestre no banco.
Execute UMA VEZ:
  venv\\Scripts\\python.exe criar_tabelas_campanha.py
"""
import sqlite3, os

DB = os.path.join('backend', 'database', 'campanhas.db')

SQL = """
-- Tabela principal de campanhas
CREATE TABLE IF NOT EXISTS campanhas_mestre (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    criador_id      INTEGER NOT NULL,
    nome            TEXT NOT NULL,
    descricao       TEXT DEFAULT '',
    historia        TEXT DEFAULT '',
    tom             TEXT DEFAULT 'Epico',
    nivel_min       INTEGER DEFAULT 1,
    nivel_max       INTEGER DEFAULT 20,
    sistema         TEXT DEFAULT 'D&D 5e',
    status          TEXT DEFAULT 'em_preparacao',
    criado_em       TEXT DEFAULT (datetime('now')),
    atualizado_em   TEXT DEFAULT (datetime('now'))
);

-- Mapas/grids da campanha
CREATE TABLE IF NOT EXISTS campanha_mapas (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campanha_id     INTEGER NOT NULL,
    nome            TEXT NOT NULL,
    descricao       TEXT DEFAULT '',
    imagem_data     TEXT,
    visivel         INTEGER DEFAULT 0,
    ordem           INTEGER DEFAULT 0,
    FOREIGN KEY (campanha_id) REFERENCES campanhas_mestre(id) ON DELETE CASCADE
);

-- Linha do tempo / eventos
CREATE TABLE IF NOT EXISTS campanha_eventos (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campanha_id     INTEGER NOT NULL,
    titulo          TEXT NOT NULL,
    descricao_pub   TEXT DEFAULT '',
    descricao_priv  TEXT DEFAULT '',
    status          TEXT DEFAULT 'futuro',
    visivel         INTEGER DEFAULT 0,
    ordem           INTEGER DEFAULT 0,
    FOREIGN KEY (campanha_id) REFERENCES campanhas_mestre(id) ON DELETE CASCADE
);

-- NPCs
CREATE TABLE IF NOT EXISTS campanha_npcs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campanha_id     INTEGER NOT NULL,
    nome            TEXT NOT NULL,
    papel           TEXT DEFAULT '',
    descricao_pub   TEXT DEFAULT '',
    descricao_priv  TEXT DEFAULT '',
    alinhamento     TEXT DEFAULT '',
    local           TEXT DEFAULT '',
    visivel         INTEGER DEFAULT 0,
    FOREIGN KEY (campanha_id) REFERENCES campanhas_mestre(id) ON DELETE CASCADE
);

-- Quests / Missoes
CREATE TABLE IF NOT EXISTS campanha_quests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campanha_id     INTEGER NOT NULL,
    titulo          TEXT NOT NULL,
    objetivo_pub    TEXT DEFAULT '',
    detalhes_priv   TEXT DEFAULT '',
    recompensa_pub  TEXT DEFAULT '',
    recompensa_priv TEXT DEFAULT '',
    local_priv      TEXT DEFAULT '',
    status          TEXT DEFAULT 'ativa',
    visivel         INTEGER DEFAULT 0,
    FOREIGN KEY (campanha_id) REFERENCES campanhas_mestre(id) ON DELETE CASCADE
);

-- Anotacoes livres
CREATE TABLE IF NOT EXISTS campanha_anotacoes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    campanha_id     INTEGER NOT NULL,
    titulo          TEXT NOT NULL,
    conteudo        TEXT DEFAULT '',
    visivel         INTEGER DEFAULT 0,
    FOREIGN KEY (campanha_id) REFERENCES campanhas_mestre(id) ON DELETE CASCADE
);

-- Vinculo sala <-> campanha
CREATE TABLE IF NOT EXISTS sala_campanha (
    sala_id         INTEGER PRIMARY KEY,
    campanha_id     INTEGER,
    FOREIGN KEY (campanha_id) REFERENCES campanhas_mestre(id)
);
"""

conn = sqlite3.connect(DB)
conn.executescript(SQL)
conn.commit()
conn.close()
print("Tabelas do Esconderijo criadas com sucesso!")
