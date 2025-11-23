# database/db_manager.py

# --- Importações ---
import sqlite3
import os
import json
import bcrypt
# Importação relativa robusta para acessar o módulo 'monstro'
from ..core.monstro import Monstro 

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Garante que o caminho para o banco de dados seja sempre encontrado corretamente.
script_dir = os.path.dirname(os.path.abspath(__file__))
NOME_DB = os.path.join(script_dir, 'campanhas.db')

# --- Funções de Busca ---

def buscar_monstro_aleatorio():
    """Conecta ao DB, busca um monstro aleatório e retorna um objeto Monstro."""
    try:
        # 'with' garante que a conexão será fechada automaticamente
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # SQL para selecionar um registro aleatório da tabela
            cursor.execute("SELECT * FROM monstros_base ORDER BY RANDOM() LIMIT 1")
            dados_monstro = cursor.fetchone()
        
        if dados_monstro:
            # Desempacota os dados do banco na nossa classe 'Monstro'
            return Monstro(
                nome=dados_monstro[1], vida_maxima=dados_monstro[2],
                ataque_bonus=dados_monstro[3], dano_dado=dados_monstro[4],
                defesa=dados_monstro[5], xp_oferecido=dados_monstro[6],
                ouro_drop=dados_monstro[7]
            )
        return None # Retorna None se a tabela estiver vazia
    except sqlite3.Error as e:
        print(f"Erro ao buscar monstro no banco de dados: {e}")
        return None

def buscar_todos_os_itens():
    """Busca todos os itens da tabela 'itens_base'."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # Busca todos os itens, ordenados pelo preço
            cursor.execute("SELECT * FROM itens_base ORDER BY preco_ouro")
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao buscar itens no banco de dados: {e}")
        return []

def buscar_detalhes_itens(nomes_dos_itens: list):
    """Busca os detalhes de uma lista específica de nomes de itens."""
    if not nomes_dos_itens: return [] # Retorna lista vazia se a entrada for vazia
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # Cria os 'placeholders' (?) dinamicamente para a consulta 'IN'
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

# --- INÍCIO - CRUD DE MONSTROS (ESCONDERIJO DO MESTRE) ---

def criar_novo_monstro(dados):
    """
    (CREATE) Insere um novo monstro na tabela 'monstros_base'.
    'dados' é um dicionário vindo da API.
    Retorna o novo monstro como um dicionário em caso de sucesso, ou None.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            cursor.execute(
                """
                INSERT INTO monstros_base (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (dados['nome'], dados['vida_maxima'], dados['ataque_bonus'], dados['dano_dado'], dados['defesa'], dados['xp_oferecido'], dados['ouro_drop'])
            )
            novo_id = cursor.lastrowid
            cursor.execute("SELECT * FROM monstros_base WHERE id = ?", (novo_id,))
            novo_monstro_db = cursor.fetchone()
            return dict(novo_monstro_db)
    except sqlite3.IntegrityError:
        print(f"Erro de integridade: Monstro com nome '{dados['nome']}' já existe.")
        return None
    except Exception as e:
        print(f"Erro ao criar novo monstro: {e}")
        return None

def atualizar_monstro_existente(monstro_id, dados):
    """
    (UPDATE) Atualiza um monstro existente na tabela 'monstros_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE monstros_base SET
                nome = ?, vida_maxima = ?, ataque_bonus = ?, dano_dado = ?,
                defesa = ?, xp_oferecido = ?, ouro_drop = ?
                WHERE id = ?
                """,
                (dados['nome'], dados['vida_maxima'], dados['ataque_bonus'], dados['dano_dado'],
                 dados['defesa'], dados['xp_oferecido'], dados['ouro_drop'], monstro_id)
            )
            if cursor.rowcount == 0:
                print(f"Erro ao atualizar: Monstro ID {monstro_id} não encontrado.")
                return None 
            cursor.execute("SELECT * FROM monstros_base WHERE id = ?", (monstro_id,))
            monstro_atualizado_db = cursor.fetchone()
            return dict(monstro_atualizado_db)
    except sqlite3.IntegrityError:
        print(f"Erro de integridade: Nome '{dados['nome']}' já está em uso por outro monstro.")
        return None
    except Exception as e:
        print(f"Erro ao atualizar monstro: {e}")
        return None

def apagar_monstro_base(monstro_id):
    """
    (DELETE) Apaga um monstro da tabela 'monstros_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM monstros_base WHERE id = ?", (monstro_id,))
            if cursor.rowcount == 0:
                print(f"Erro ao apagar: Monstro ID {monstro_id} não encontrado.")
                return False 
            return True
    except Exception as e:
        print(f"Erro ao apagar monstro: {e}")
        return False

# --- FIM - CRUD DE MONSTROS ---


# --- INÍCIO - [NOVO] CRUD DE ITENS (ESCONDERIJO DO MESTRE) ---

def criar_novo_item(dados):
    """
    (CREATE) Insere um novo item na tabela 'itens_base'.
    'dados' é um dicionário vindo da API.
    Retorna o novo item como um dicionário em caso de sucesso, ou None.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            
            # Executa o INSERT com os dados do item
            cursor.execute(
                """
                INSERT INTO itens_base (nome, tipo, descricao, preco_ouro, dano_dado, bonus_ataque, efeito)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dados['nome'], dados['tipo'], dados.get('descricao'), 
                    dados['preco_ouro'], dados.get('dano_dado'), 
                    dados.get('bonus_ataque', 0), dados.get('efeito')
                )
            )
            
            # Pega o ID do item que acabamos de criar
            novo_id = cursor.lastrowid
            
            # Busca o item recém-criado no banco
            cursor.execute("SELECT * FROM itens_base WHERE id = ?", (novo_id,))
            novo_item_db = cursor.fetchone()
            
            # Retorna o novo item como um dicionário
            return dict(novo_item_db)
            
    except sqlite3.IntegrityError:
        # Este erro acontece se o 'nome' do item já existir (devido ao UNIQUE)
        print(f"Erro de integridade: Item com nome '{dados['nome']}' já existe.")
        return None
    except Exception as e:
        print(f"Erro ao criar novo item: {e}")
        return None

def atualizar_item_existente(item_id, dados):
    """
    (UPDATE) Atualiza um item existente na tabela 'itens_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            # Executa o comando UPDATE para o ID específico
            cursor.execute(
                """
                UPDATE itens_base SET
                nome = ?, tipo = ?, descricao = ?, preco_ouro = ?, 
                dano_dado = ?, bonus_ataque = ?, efeito = ?
                WHERE id = ?
                """,
                (
                    dados['nome'], dados['tipo'], dados.get('descricao'), 
                    dados['preco_ouro'], dados.get('dano_dado'), 
                    dados.get('bonus_ataque', 0), dados.get('efeito'), 
                    item_id
                )
            )
            
            # Verifica se alguma linha foi realmente atualizada
            if cursor.rowcount == 0:
                print(f"Erro ao atualizar: Item ID {item_id} não encontrado.")
                return None # Item com esse ID não foi encontrado

            # Busca o item que acabamos de atualizar
            cursor.execute("SELECT * FROM itens_base WHERE id = ?", (item_id,))
            item_atualizado_db = cursor.fetchone()
            
            # Retorna o item atualizado como um dicionário
            return dict(item_atualizado_db)

    except sqlite3.IntegrityError:
        # Ocorre se o Mestre tentar renomear para um nome que já existe
        print(f"Erro de integridade: Nome '{dados['nome']}' já está em uso por outro item.")
        return None
    except Exception as e:
        print(f"Erro ao atualizar item: {e}")
        return None

def apagar_item_base(item_id):
    """
    (DELETE) Apaga um item da tabela 'itens_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            
            # Executa o comando DELETE para o ID específico
            cursor.execute("DELETE FROM itens_base WHERE id = ?", (item_id,))
            
            # Verifica se alguma linha foi realmente apagada
            if cursor.rowcount == 0:
                print(f"Erro ao apagar: Item ID {item_id} não encontrado.")
                return False # Item não encontrado
                
            return True
            
    except Exception as e:
        print(f"Erro ao apagar item: {e}")
        return False

# --- FIM - CRUD DE ITENS ---


# --- INÍCIO - [NOVO] CRUD DE HABILIDADES (ESCONDERIJO DO MESTRE) ---

def criar_nova_habilidade(dados):
    """
    (CREATE) Insere uma nova habilidade na tabela 'habilidades_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            
            # Executa o INSERT com os dados da habilidade
            cursor.execute(
                """
                INSERT INTO habilidades_base (nome, descricao, efeito, custo_mana)
                VALUES (?, ?, ?, ?)
                """,
                (
                    dados['nome'], dados.get('descricao'), 
                    dados['efeito'], dados.get('custo_mana', 0)
                )
            )
            
            novo_id = cursor.lastrowid
            cursor.execute("SELECT * FROM habilidades_base WHERE id = ?", (novo_id,))
            nova_habilidade_db = cursor.fetchone()
            return dict(nova_habilidade_db)
            
    except sqlite3.IntegrityError:
        print(f"Erro de integridade: Habilidade com nome '{dados['nome']}' já existe.")
        return None
    except Exception as e:
        print(f"Erro ao criar nova habilidade: {e}")
        return None

def atualizar_habilidade_existente(habilidade_id, dados):
    """
    (UPDATE) Atualiza uma habilidade existente na 'habilidades_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            cursor.execute(
                """
                UPDATE habilidades_base SET
                nome = ?, descricao = ?, efeito = ?, custo_mana = ?
                WHERE id = ?
                """,
                (
                    dados['nome'], dados.get('descricao'), 
                    dados['efeito'], dados.get('custo_mana', 0), 
                    habilidade_id
                )
            )
            
            if cursor.rowcount == 0:
                print(f"Erro ao atualizar: Habilidade ID {habilidade_id} não encontrada.")
                return None

            cursor.execute("SELECT * FROM habilidades_base WHERE id = ?", (habilidade_id,))
            habilidade_atualizada_db = cursor.fetchone()
            return dict(habilidade_atualizada_db)

    except sqlite3.IntegrityError:
        print(f"Erro de integridade: Nome '{dados['nome']}' já está em uso por outra habilidade.")
        return None
    except Exception as e:
        print(f"Erro ao atualizar habilidade: {e}")
        return None

def apagar_habilidade_base(habilidade_id):
    """
    (DELETE) Apaga uma habilidade da tabela 'habilidades_base'.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("DELETE FROM habilidades_base WHERE id = ?", (habilidade_id,))
            if cursor.rowcount == 0:
                print(f"Erro ao apagar: Habilidade ID {habilidade_id} não encontrada.")
                return False 
            return True
    except Exception as e:
        print(f"Erro ao apagar habilidade: {e}")
        return False

# --- FIM - CRUD DE HABILIDADES ---


def buscar_fichas_por_usuario(usuario_id):
    """Busca todas as fichas de personagem que pertencem a um ID de usuário específico."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            # sqlite3.Row permite acessar os resultados por nome da coluna (como um dict)
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            cursor.execute(
                # Seleciona apenas os dados para a "lista" de fichas
                "SELECT id, nome_personagem, classe, nivel FROM fichas_personagem WHERE usuario_id = ?",
                (usuario_id,)
            )
            # Converte os resultados de 'Row' para dicionários Python
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
            # A consulta 'WHERE' verifica o ID da ficha E o ID do dono
            cursor.execute(
                "SELECT * FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            ficha = cursor.fetchone()
            if ficha:
                return dict(ficha) # Retorna a ficha como dicionário
            return None # Retorna None se a ficha não for encontrada ou não pertencer ao usuário
    except Exception as e:
        print(f"Erro ao buscar ficha por ID: {e}")
        return None

def buscar_dados_essenciais_ficha(ficha_id, usuario_id):
    """Busca o nome e a classe de uma ficha específica, verificando a posse."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            # Verificação de segurança: O usuário (token) é dono desta ficha?
            cursor.execute(
                "SELECT nome_personagem, classe FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            ficha = cursor.fetchone()
            if ficha:
                return dict(ficha)
            return None # Permissão negada ou ficha não existe
    except Exception as e:
        print(f"Erro ao buscar dados essenciais da ficha: {e}")
        return None

# --- Funções de Autenticação e Usuário ---

def registrar_novo_usuario(nome_usuario, senha_texto_puro):
    """Cria o hash da senha e insere um novo usuário no banco de dados."""
    try:
        # Converte a senha de string para bytes
        senha_bytes = senha_texto_puro.encode('utf-8')
        # Gera o 'salt' e cria o hash da senha
        senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
        
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # Insere o novo usuário (o 'role' será 'player' por padrão, como definido no db_setup.py)
            cursor.execute(
                "INSERT INTO usuarios (nome_usuario, senha_hash) VALUES (?, ?)",
                (nome_usuario, senha_hash)
            )
            return True
    except sqlite3.IntegrityError:
        # Ocorre se o 'nome_usuario' já existir (UNIQUE)
        return False
    except Exception as e:
        print(f"Erro ao registrar novo usuário: {e}")
        return False

def verificar_login(nome_usuario, senha_texto_puro):
    """
    Verifica o login. Retorna um dicionário com ID e Papel em caso de sucesso, ou None.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # ATUALIZAÇÃO: Agora buscamos o 'id', 'senha_hash' E o 'role'.
            cursor.execute(
                "SELECT id, senha_hash, role FROM usuarios WHERE nome_usuario = ?",
                (nome_usuario,)
            )
            resultado = cursor.fetchone()
        
        if resultado is None:
            return None # Usuário não encontrado

        # Desempacota os dados do banco
        user_id, senha_hash_db, user_role = resultado[0], resultado[1], resultado[2]
        senha_bytes = senha_texto_puro.encode('utf-8')

        # Compara a senha fornecida com o hash salvo no banco
        if bcrypt.checkpw(senha_bytes, senha_hash_db):
            # Sucesso! Retorna os dados do usuário para o 'servidor_api' criar o token
            return {'id': user_id, 'role': user_role}
        else:
            return None # Senha incorreta
            
    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return None

# --- Funções de Gerenciamento de Fichas ---

def criar_nova_ficha(usuario_id, nome_personagem, classe, raca, antecedente, atributos, pericias):
    """Insere uma nova ficha de personagem completa no banco de dados."""
    try:
        # Converte os dicionários Python (atributos, pericias) em strings JSON
        atributos_str_json = json.dumps(atributos)
        pericias_str_json = json.dumps(pericias)
        
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                # Insere a ficha (XP e Nível já têm valores DEFAULT na tabela)
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
        # Converte os dados recebidos (JSON/dict) em strings JSON para salvar
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
            
            # Se rowcount == 0, a ficha não foi encontrada (ou não pertencia ao usuário)
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
            # O 'WHERE' garante que um usuário só pode apagar a própria ficha
            cursor.execute(
                "DELETE FROM fichas_personagem WHERE id = ? AND usuario_id = ?",
                (ficha_id, usuario_id)
            )
            if cursor.rowcount == 0:
                return False # Ficha não encontrada ou permissão negada
            return True
    except Exception as e:
        print(f"Erro ao apagar ficha: {e}")
        return False

# --- FUNÇÃO PARA GERENCIAR XP E LEVEL UP ---
def adicionar_xp_e_upar(ficha_id, quantidade_xp):
    """
    Adiciona XP a uma ficha, processa o level-up, e retorna a ficha ATUALIZADA.
    Retorna a ficha (dict) em caso de sucesso, ou None em caso de falha.
    """
    conexao = None
    try:
        # Precisamos de uma conexão que não use 'with' para gerenciar o 'commit'
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
        subiu_de_nivel = False # Flag para avisar o frontend

        # 3. A Lógica de Level Up (loop 'while' para caso ganhe XP para >1 nível)
        while ficha['xp_atual'] >= ficha['xp_proximo_nivel']:
            subiu_de_nivel = True
            ficha['nivel'] += 1
            # Calcula o XP que "sobrou" após upar
            xp_excedente = ficha['xp_atual'] - ficha['xp_proximo_nivel']
            ficha['xp_atual'] = xp_excedente
            
            # Tabela de XP de D&D 5e (simplificada)
            xp_niveis = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000, 85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000]
            
            # Define o próximo "objetivo" de XP
            if ficha['nivel'] < 20:
                ficha['xp_proximo_nivel'] = xp_niveis[ficha['nivel']] # Pega o próximo
            else:
                ficha['xp_proximo_nivel'] = ficha['xp_atual'] + 1 # Nível Máximo

        # 4. Salva os novos dados no banco de dados.
        cursor.execute(
            "UPDATE fichas_personagem SET nivel = ?, xp_atual = ?, xp_proximo_nivel = ? WHERE id = ?",
            (ficha['nivel'], ficha['xp_atual'], ficha['xp_proximo_nivel'], ficha_id)
        )
        # Confirma a transação
        conexao.commit()
        
        # 5. Adiciona a flag de level up e retorna a ficha ATUALIZADA para o servidor.
        ficha['subiu_de_nivel'] = subiu_de_nivel
        return ficha
            
    except Exception as e:
        print(f"Erro ao adicionar XP: {e}")
        if conexao:
            conexao.rollback() # Desfaz a transação em caso de erro
        return None
    finally:
        if conexao:
            conexao.close() # Garante que a conexão seja fechada

# --- Funções de Gerenciamento de Salas ---

def criar_nova_sala(nome_sala, senha, mestre_id):
    """Cria uma nova sala de campanha no banco de dados."""
    try:
        senha_hash = None
        if senha: # Se uma senha foi fornecida
            senha_bytes = senha.encode('utf-8')
            senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
            
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                # 'mestre_id' vem do token do usuário que criou a sala
                "INSERT INTO salas (nome, senha_hash, mestre_id) VALUES (?, ?, ?)",
                (nome_sala, senha_hash, mestre_id)
            )
            return True
    except sqlite3.IntegrityError:
        return False # Nome da sala já existe
    except Exception as e:
        print(f"Erro ao criar nova sala: {e}")
        return False

def listar_salas_disponiveis():
    """Busca todas as salas e o nome do Mestre de cada uma."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            # SQL 'JOIN' para pegar o nome do mestre (da tabela 'usuarios')
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
            
        # Se a sala não existe ou não tem senha (não deveria acontecer no fluxo)
        if not resultado or not resultado[0]:
            return False 
            
        senha_hash_db = resultado[0]
        senha_bytes = senha_texto_puro.encode('utf-8')
        
        # Compara a senha com o hash
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
    (Função placeholder/simplificada)
    Busca todas as fichas ativas em uma sala.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            # ATENÇÃO: Esta query é uma simplificação.
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
            return resultado[0] if resultado else "" # Retorna a nota ou uma string vazia
    except Exception as e:
        print(f"Erro ao buscar anotações: {e}")
        return ""

def salvar_anotacoes(usuario_id, sala_id, notas):
    """Salva ou atualiza as anotações de um jogador para uma sala."""
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # 'INSERT OR REPLACE' (UPSERT) é perfeito aqui:
            # Cria se não existe, atualiza se existe (baseado na UNIQUE key (usuario_id, sala_id))
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
    
def buscar_todas_as_habilidades():
    #Busca todas as habilidades da tabela 'habilidades_base'.
    try:
        # Conecta ao banco de dados
        with sqlite3.connect(NOME_DB) as conexao:
            # Configura para retornar resultados como dicionários (opcional, mas bom para API)
            conexao.row_factory = sqlite3.Row 
            cursor = conexao.cursor()
            # Executa a query para selecionar todas as habilidades, ordenadas por nome
            cursor.execute("SELECT * FROM habilidades_base ORDER BY nome")
            # Converte o resultado em uma lista de dicionários
            habilidades = [dict(row) for row in cursor.fetchall()]
            # Retorna a lista
        return habilidades
    except sqlite3.Error as e:
        # Em caso de erro, imprime a mensagem e retorna uma lista vazia
        print(f"Erro ao buscar todas as habilidades: {e}")
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
            # O 'WHERE' garante que só o dono da ficha (ficha_id) pode apagar o item
            cursor.execute(
                "DELETE FROM inventario_sala WHERE id = ? AND ficha_id = ?",
                (item_id, ficha_id)
            )
            if cursor.rowcount == 0:
                return False # Item não encontrado ou permissão negada
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
            # Busca as mensagens em ordem de 'timestamp' (padrão)
            cursor.execute(
                "SELECT remetente, mensagem FROM historico_chat WHERE sala_id = ? ORDER BY timestamp ASC",
                (sala_id,)
            )
            # Formata as mensagens como o frontend espera
            historico = [f"[{remetente}]: {mensagem}" for remetente, mensagem in cursor.fetchall()]
            return historico
    except Exception as e:
        print(f"Erro ao buscar histórico do chat: {e}")
        return []

# --- Funções para 'Cantigas do Aventureiro' (Dashboard) ---

def buscar_dados_cantigas(usuario_id):
    """
    Busca estatísticas do usuário:
    - Tempo total de aventura (em segundos)
    - Quantidade de fichas ativas
    - Quantidade de salas visitadas (histórico único)
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            # 1. Tempo de Aventura
            cursor.execute("SELECT tempo_aventura_segundos FROM usuarios WHERE id = ?", (usuario_id,))
            tempo_res = cursor.fetchone()
            tempo_total = tempo_res['tempo_aventura_segundos'] if tempo_res else 0
            
            # 2. Fichas Ativas
            cursor.execute("SELECT COUNT(*) as total FROM fichas_personagem WHERE usuario_id = ?", (usuario_id,))
            fichas_res = cursor.fetchone()
            total_fichas = fichas_res['total'] if fichas_res else 0
            
            # 3. Salas Visitadas (Total Histórico)
            cursor.execute("SELECT COUNT(DISTINCT sala_id) as total FROM historico_salas WHERE usuario_id = ?", (usuario_id,))
            salas_res = cursor.fetchone()
            total_salas = salas_res['total'] if salas_res else 0
            
            return {
                "tempo_aventura_segundos": tempo_total,
                "total_fichas": total_fichas,
                "total_salas_visitadas": total_salas
            }
    except Exception as e:
        print(f"Erro ao buscar dados das cantigas: {e}")
        return None

def buscar_historico_salas(usuario_id):
    """
    Busca as últimas 5 salas visitadas pelo usuário.
    Retorna: Nome da Sala, Nome da Ficha usada, Data de Acesso.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            conexao.row_factory = sqlite3.Row
            cursor = conexao.cursor()
            
            cursor.execute("""
                SELECT 
                    s.id as sala_id,
                    s.nome as sala_nome,
                    f.nome_personagem as ficha_nome,
                    h.data_acesso
                FROM historico_salas h
                JOIN salas s ON h.sala_id = s.id
                LEFT JOIN fichas_personagem f ON h.ficha_id = f.id
                WHERE h.usuario_id = ?
                ORDER BY h.data_acesso DESC
                LIMIT 5
            """, (usuario_id,))
            
            historico = [dict(row) for row in cursor.fetchall()]
            return historico
    except Exception as e:
        print(f"Erro ao buscar histórico de salas: {e}")
        return []

def registrar_acesso_sala(usuario_id, sala_id, ficha_id=None):
    """
    Registra que o usuário entrou em uma sala.
    Atualiza o timestamp se já existir registro recente (opcional, aqui vamos sempre inserir novo para histórico).
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("""
                INSERT INTO historico_salas (usuario_id, sala_id, ficha_id)
                VALUES (?, ?, ?)
            """, (usuario_id, sala_id, ficha_id))
            return True
    except Exception as e:
        print(f"Erro ao registrar acesso à sala: {e}")
        return False

def atualizar_credenciais_usuario(usuario_id, novo_nome, nova_senha):
    """
    Atualiza o nome de usuário e/ou senha.
    """
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            
            updates = []
            params = []
            
            if novo_nome:
                updates.append("nome_usuario = ?")
                params.append(novo_nome)
            
            if nova_senha:
                senha_bytes = nova_senha.encode('utf-8')
                senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
                updates.append("senha_hash = ?")
                params.append(senha_hash)
            
            if not updates:
                return False
            
            params.append(usuario_id)
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
            
            cursor.execute(query, params)
            return True
    except sqlite3.IntegrityError:
        return False # Nome de usuário já existe
    except Exception as e:
        print(f"Erro ao atualizar credenciais: {e}")
        return False