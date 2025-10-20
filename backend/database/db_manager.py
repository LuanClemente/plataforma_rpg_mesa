# database/db_manager.py

# --- Importações ---
import sqlite3
import os
import json
import bcrypt
# CORREÇÃO DE IMPORTAÇÃO: Movido para usar o caminho absoluto do pacote.
from backend.core.monstro import Monstro 

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Garante que o caminho para o banco de dados seja sempre encontrado corretamente.
script_dir = os.path.dirname(os.path.abspath(__file__))
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# --- Funções de Busca ---

def buscar_monstro_aleatorio():
    """Conecta ao DB, busca um monstro aleatório e retorna um objeto Monstro."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
            dados_monstro = cursor.fetchone()
        
        if dados_monstro:
            return Monstro(
                nome=dados_monstro[1], vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3], dano_dado=dados_monstro[4],
                defesa=dados_monstro[5], xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
        return None
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        return None

def buscar_todos_os_itens():
    """Busca todos os itens da tabela 'itens_base'."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM itens_base ORDER BY preco_ouro")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens no banco de dados: {e}")
        return []

def buscar_detalhes_itens(nomes_dos_itens: list):
    """Busca os detalhes de uma lista específica de nomes de itens."""
    if not nomes_dos_itens: return []
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            placeholders = ', '.join('?' for _ in nomes_dos_itens)
            query = f"SELECT * FROM itens_base WHERE nome IN ({placeholders})"
            cursor.execute(query, nomes_dos_itens)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de itens: {e}")
        return []

def buscar_detalhes_habilidades(nomes_das_habilidades: list):
    """Busca os detalhes de uma lista específica de nomes de habilidades."""
    if not nomes_das_habilidades: return []
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            placeholders = ', '.join('?' for _ in nomes_das_habilidades)
            query = f"SELECT * FROM habilidades_base WHERE nome IN ({placeholders})"
            cursor.execute(query, nomes_das_habilidades)
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar detalhes de habilidades: {e}")
        return []

def buscar_todos_os_monstros():
    """Busca todos os monstros da tabela 'monstros_base'."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar todos os monstros: {e}")
        return []

def buscar_fichas_por_usuario(usuario_id):
    """Busca todas as fichas de personagem que pertencem a um ID de usuário específico."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_personagem, classe, nivel FROM fichas_personagem WHERE usuario_id = ?",
                (usuario_id,)
            )
            fichas = [dict(row) for row in cursor.fetchall()]
            return fichas
    except Exception as e:
        print(f"Erro ao buscar fichas por usuário: {e}")
        return []

def buscar_ficha_por_id(ficha_id, usuario_id):
    """Busca os detalhes completos de uma única ficha, verificando a posse."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT * FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            ficha = cursor.fetchone()
            if ficha:
                return dict(ficha)
            return None
    except Exception as e:
        print(f"Erro ao buscar ficha por ID: {e}")
        return None

def buscar_dados_essenciais_ficha(ficha_id, usuario_id):
    """Busca o nome e a classe de uma ficha específica, verificando a posse."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT nome_personagem, classe FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            ficha = cursor.fetchone()
            if ficha:
                return dict(ficha)
            return None
    except Exception as e:
        print(f"Erro ao buscar dados essenciais da ficha: {e}")
        return None

# --- Funções de Autenticação e Usuário ---

def registrar_novo_usuario(nome_usuario, senha_texto_puro):
    """Cria o hash da senha e insere um novo usuário no banco de dados."""
    try:
        senha_bytes = senha_texto_puro.encode('utf-8')
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO usuarios (nome_usuario, senha_hash) VALUES (?, ?)",
                (nome_usuario, senha_hash)
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao registrar novo usuário: {e}")
        return False

def verificar_login(nome_usuario, senha_texto_puro):
    """Verifica se o usuário existe e a senha está correta. Retorna o ID do usuário ou None."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, senha_hash FROM usuarios WHERE nome_usuario = ?",
                (nome_usuario,)
            )
            resultado = cursor.fetchone()
        if resultado is None:
            return None
        user_id, senha_hash_db = resultado[0], resultado[1]
        senha_bytes = senha_texto_puro.encode('utf-8')
        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            return user_id
        else:
            return None
    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return None

# --- Funções de Gerenciamento de Fichas ---

def criar_nova_ficha(usuario_id, nome_personagem, classe, raca, antecedente, atributos, pericias):
    """Insere uma nova ficha de personagem completa no banco de dados."""
    try:
        atributos_str_json = json.dumps(atributos)
        pericias_str_json = json.dumps(pericias)
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO fichas_personagem (usuario_id, nome_personagem, classe, raca, antecedente, nivel, atributos_json, pericias_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (usuario_id, nome_personagem, classe, raca, antecedente, 1, atributos_str_json, pericias_str_json)
            )
        return True
    except Exception as e:
        print(f"Erro ao criar nova ficha: {e}")
        return False

def atualizar_ficha(ficha_id, usuario_id, novos_dados):
    """Atualiza os dados de uma ficha existente no banco de dados."""
    try:
        atributos_str_json = json.dumps(novos_dados['atributos'])
        pericias_str_json = json.dumps(novos_dados['pericias'])
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                UPDATE fichas_personagem 
                SET nome_personagem = ?, classe = ?, raca = ?, antecedente = ?, 
                    nivel = ?, atributos_json = ?, pericias_json = ?
                WHERE id = ? AND usuario_id = ?
            """, (
                novos_dados['nome_personagem'], novos_dados['classe'], novos_dados['raca'],
                novos_dados['antecedente'], novos_dados['nivel'], atributos_str_json,
                pericias_str_json, ficha_id, usuario_id
            ))
            if cursor.rowcount == 0:
                return False
        return True
    except Exception as e:
        print(f"Erro ao atualizar ficha: {e}")
        return False

def apagar_ficha(ficha_id, usuario_id):
    """Apaga uma ficha do banco de dados, verificando se pertence ao usuário correto."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            if cursor.rowcount == 0:
                return False
        return True
    except Exception as e:
        print(f"Erro ao apagar ficha: {e}")
        return False

# --- NOVA FUNÇÃO PARA GERENCIAR XP E LEVEL UP ---
def adicionar_xp_e_upar(ficha_id, quantidade_xp):
    """
    Adiciona XP a uma ficha, processa o level-up, e retorna a ficha ATUALIZADA.
    Retorna a ficha (dict) em caso de sucesso, ou None em caso de falha.
    """
    conexao = None
    try:
        conexao = sqlite3.connect(NOME_DB)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        
        # 1. Busca os dados atuais da ficha.
        cursor.execute(
            "SELECT id, usuario_id, nome_personagem, classe, raca, antecedente, nivel, xp_atual, xp_proximo_nivel, atributos_json, pericias_json FROM fichas_personagem WHERE id = ?",
            (ficha_id,)
        )
        ficha_data = cursor.fetchone()
        if not ficha_data:
            return None # Ficha não encontrada

        # 2. Converte para um dicionário mutável e calcula o novo XP.
        ficha = dict(ficha_data)
        ficha['xp_atual'] += quantidade_xp
        subiu_de_nivel = False

        # 3. A Lógica de Level Up
        while ficha['xp_atual'] >= ficha['xp_proximo_nivel']:
            subiu_de_nivel = True
            ficha['nivel'] += 1
            xp_excedente = ficha['xp_atual'] - ficha['xp_proximo_nivel']
            ficha['xp_atual'] = xp_excedente
            # (Lógica de D&D 5e para XP do próximo nível - simplificada)
            xp_niveis = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
            if ficha['nivel'] < 20:
                ficha['xp_proximo_nivel'] = xp_niveis[ficha['nivel']] # Pega o próximo
            else:
                ficha['xp_proximo_nivel'] = ficha['xp_atual'] + 1 # Max Lvl

        # 4. Salva os novos dados no banco de dados.
        cursor.execute(
            "UPDATE fichas_personagem SET nivel = ?, xp_atual = ?, xp_proximo_nivel = ? WHERE id = ?",
            (ficha['nivel'], ficha['xp_atual'], ficha['xp_proximo_nivel'], ficha_id)
        )
        conexao.commit()
        
        # 5. Adiciona a flag de level up e retorna a ficha ATUALIZADA para o servidor.
        ficha['subiu_de_nivel'] = subiu_de_nivel
        return ficha
            
    except Exception as e:
        print(f"Erro ao adicionar XP: {e}")
        if conexao:
            conexao.rollback()
        return None
    finally:
        if conexao:
            conexao.close()

# --- Funções de Gerenciamento de Salas ---

def criar_nova_sala(nome_sala, senha, mestre_id):
    """Cria uma nova sala de campanha no banco de dados."""
    try:
        senha_hash = None
        if senha:
            senha_bytes = senha.encode('utf-8')
            senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO salas (nome, senha_hash, mestre_id) VALUES (?, ?, ?)",
                (nome_sala, senha_hash, mestre_id)
            )
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao criar nova sala: {e}")
        return False

def listar_salas_disponiveis():
    """Busca todas as salas e o nome do Mestre de cada uma."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute("""
                SELECT s.id, s.nome, u.nome_usuario as mestre_nome, s.senha_hash IS NOT NULL as tem_senha
                FROM salas s
                JOIN usuarios u ON s.mestre_id = u.id
            """)
            salas = [dict(row) for row in cursor.fetchall()]
            return salas
    except Exception as e:
        print(f"Erro ao listar salas: {e}")
        return []

def verificar_senha_da_sala(sala_id, senha_texto_puro):
    """Verifica se a senha fornecida para uma sala corresponde ao hash no DB."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT senha_hash FROM salas WHERE id = ?",
                (sala_id,)
            )
            resultado = cursor.fetchone()
        if not resultado or not resultado[0]:
            return False
        senha_hash_db = resultado[0]
        senha_bytes = senha_texto_puro.encode('utf-8')
        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            return True
        else:
            return False
    except Exception as e:
        print(f"Erro ao verificar senha da sala: {e}")
        return False
        
def buscar_mestre_da_sala(sala_id):
    """Busca o ID do usuário que é o Mestre de uma sala específica."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT mestre_id FROM salas WHERE id = ?",
                (sala_id,)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else None
    except Exception as e:
        print(f"Erro ao buscar mestre da sala: {e}")
        return None

def buscar_jogadores_na_sala(sala_id):
    """
    Busca todas as fichas ativas em uma sala.
    (Esta é uma simplificação. Em um sistema real, precisaríamos de uma tabela
    que associe fichas a salas ativamente). Por enquanto, vamos assumir que
    todas as fichas do mestre estão na sala para fins de demonstração.
    Uma abordagem melhor seria ter uma tabela `sala_jogadores`.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            # ATENÇÃO: Esta query é uma simplificação. O ideal seria consultar uma tabela de "sessão".
            # Por agora, vamos retornar todas as fichas para popular a UI do mestre.
            cursor.execute("SELECT id, nome_personagem FROM fichas_personagem")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        print(f"Erro ao buscar jogadores na sala: {e}")
        return []
# --- Funções para Anotações ---
def buscar_anotacoes(usuario_id, sala_id):
    """Busca as anotações de um jogador para uma sala específica."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT notas FROM anotacoes_jogador WHERE usuario_id = ? AND sala_id = ?",
                (usuario_id, sala_id)
            )
            resultado = cursor.fetchone()
            return resultado[0] if resultado else ""
    except Exception as e:
        print(f"Erro ao buscar anotações: {e}")
        return ""

def salvar_anotacoes(usuario_id, sala_id, notas):
    """Salva ou atualiza as anotações de um jogador para uma sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO anotacoes_jogador (usuario_id, sala_id, notas) VALUES (?, ?, ?)",
                (usuario_id, sala_id, notas)
            )
        return True
    except Exception as e:
        print(f"Erro ao salvar anotações: {e}")
        return False
    
# --- Funções para Inventário de Sala ---
def buscar_inventario_sala(ficha_id, sala_id):
    """Busca o inventário de um personagem específico em uma sala específica."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT id, nome_item, descricao FROM inventario_sala WHERE ficha_id = ? AND sala_id = ?",
                (ficha_id, sala_id)
            )
            itens = [dict(row) for row in cursor.fetchall()]
            return itens
    except Exception as e:
        print(f"Erro ao buscar inventário da sala: {e}")
        return []

def adicionar_item_sala(ficha_id, sala_id, nome_item, descricao):
    """Adiciona um novo item ao inventário de um personagem na sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO inventario_sala (ficha_id, sala_id, nome_item, descricao) VALUES (?, ?, ?, ?)",
                (ficha_id, sala_id, nome_item, descricao)
            )
        return True
    except Exception as e:
        print(f"Erro ao adicionar item na sala: {e}")
        return False

def apagar_item_sala(item_id, ficha_id):
    """Apaga um item do inventário da sala, verificando a posse."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "DELETE FROM inventario_sala WHERE id = ? AND ficha_id = ?",
                (item_id, ficha_id)
            )
            if cursor.rowcount == 0:
                return False
        return True
    except Exception as e:
        print(f"Erro ao apagar item da sala: {e}")
        return False
    
# --- Funções para Histórico de Chat ---
def salvar_mensagem_chat(sala_id, remetente, mensagem):
    """Salva uma nova mensagem no histórico da sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO historico_chat (sala_id, remetente, mensagem) VALUES (?, ?, ?)",
                (sala_id, remetente, mensagem)
            )
        return True
    except Exception as e:
        print(f"Erro ao salvar mensagem do chat: {e}")
        return False

def buscar_historico_chat(sala_id):
    """Busca todas as mensagens do histórico de uma sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "SELECT remetente, mensagem FROM historico_chat WHERE sala_id = ? ORDER BY timestamp ASC",
                (sala_id,)
            )
            historico = [f"[{remetente}]: {mensagem}" for remetente, mensagem in cursor.fetchall()]
            return historico
    except Exception as e:
        print(f"Erro ao buscar histórico do chat: {e}")
        return []