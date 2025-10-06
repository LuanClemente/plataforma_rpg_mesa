# mestre/editor_mestre.py

# Importa a biblioteca para interagir com o banco de dados SQLite.
import sqlite3
# Importa a biblioteca 'os' para nos ajudar a manipular caminhos de arquivos de forma inteligente.
import os

# --- LÓGICA DE CAMINHO ABSOLUTO E ROBUSTO ---
# Descobre o caminho do diretório onde este script (editor_mestre.py) está.
script_dir = os.path.dirname(os.path.abspath(__file__))
# Constrói o caminho para a pasta raiz do backend (subindo um nível a partir de 'mestre').
backend_dir = os.path.join(script_dir, '..')
# Constrói o caminho final e absoluto para o arquivo do banco de dados.
NOME_DB = os.path.join(backend_dir, 'database', 'campanhas.db')

# --- Funções de Gerenciamento de Monstros ---

def adicionar_monstro():
    """Pede ao Mestre os dados de um novo monstro e o insere na tabela 'monstros_base'."""
    print("\n--- Adicionando Novo Monstro ---")
    try:
        nome = input("Nome do Monstro: ").strip()
        vida_maxima = int(input("Vida Máxima: "))
        ataque_bonus = int(input("Bônus de Ataque: "))
        dano_dado = input("Dado de Dano (ex: 1d8): ").strip()
        defesa = int(input("Classe de Defesa (AC): "))
        xp_oferecido = int(input("XP Oferecido: "))
        ouro_drop = int(input("Ouro Descoberto: "))
        
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO monstros_base (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop)
            )
        print(f"\nMonstro '{nome}' adicionado à biblioteca com sucesso!")
    except ValueError:
        print("\nErro: Por favor, insira um número válido para os atributos numéricos.")
    except sqlite3.IntegrityError:
        print(f"\nErro: Já existe um monstro com o nome '{nome}' na biblioteca.")

def listar_monstros():
    """Consulta e exibe todos os monstros da tabela 'monstros_base'."""
    print("\n--- Biblioteca de Monstros ---")
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
            monstros = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return

    if not monstros:
        print("A biblioteca de monstros está vazia.")
    else:
        print(f"{'ID':<4} {'Nome':<20} {'Vida':<5} {'Defesa':<6} {'XP':<5}")
        print("-" * 50)
        for monstro in monstros:
            id, nome, vida, _, _, defesa, xp, _ = monstro
            print(f"{id:<4} {nome:<20} {vida:<5} {defesa:<6} {xp:<5}")

# --- Funções de Gerenciamento de Itens ---

def adicionar_item():
    """Pede ao Mestre os dados de um novo item e o insere na tabela 'itens_base'."""
    print("\n--- Adicionando Novo Item ---")
    try:
        nome = input("Nome do Item: ").strip()
        tipo = input("Tipo do Item (Arma, Poção, Armadura, etc.): ").strip()
        descricao = input("Descrição: ").strip()
        preco_ouro = int(input("Preço em Ouro: "))

        dano_dado, bonus_ataque, efeito = None, 0, None
        
        if tipo.lower() == 'arma':
            dano_dado = input("Dado de Dano da Arma (ex: 1d8): ").strip()
            bonus_ataque = int(input("Bônus de Ataque da Arma (ex: 0, 1): "))
        elif tipo.lower() == 'poção':
            efeito = input("Efeito do Item (ex: cura:10): ").strip()

        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO itens_base (nome, tipo, descricao, preco_ouro, dano_dado, bonus_ataque, efeito) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nome, tipo, descricao, preco_ouro, dano_dado, bonus_ataque, efeito)
            )
        print(f"\nItem '{nome}' adicionado à biblioteca com sucesso!")
    except ValueError:
        print("\nErro: Por favor, insira um número válido para preço ou bônus de ataque.")
    except sqlite3.IntegrityError:
        print(f"\nErro: Já existe um item com o nome '{nome}' na biblioteca.")

def listar_itens():
    """Consulta e exibe todos os itens da tabela 'itens_base'."""
    print("\n--- Biblioteca de Itens ---")
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM itens_base ORDER BY tipo, nome")
            itens = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return

    if not itens:
        print("A biblioteca de itens está vazia.")
    else:
        print(f"{'ID':<4} {'Nome':<25} {'Tipo':<15} {'Preço':<10}")
        print("-" * 60)
        for item in itens:
            id, nome, tipo, _, preco, _, _, _ = item
            print(f"{id:<4} {nome:<25} {tipo:<15} {preco:<10} Ouro")

# --- Funções de Gerenciamento de Habilidades ---

def adicionar_habilidade():
    """Pede ao Mestre os dados de uma nova habilidade e a insere na tabela 'habilidades_base'."""
    print("\n--- Adicionando Nova Habilidade/Magia ---")
    try:
        nome = input("Nome da Habilidade: ").strip()
        descricao = input("Descrição: ").strip()
        efeito = input("Efeito (ex: dano:2d6:fogo, cura:15): ").strip()
        custo_mana = int(input("Custo de Mana: "))
        
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute(
                "INSERT INTO habilidades_base (nome, descricao, efeito, custo_mana) VALUES (?, ?, ?, ?)",
                (nome, descricao, efeito, custo_mana)
            )
        print(f"\nHabilidade '{nome}' adicionada à biblioteca com sucesso!")
    except ValueError:
        print("\nErro: Custo de Mana deve ser um número.")
    except sqlite3.IntegrityError:
        print(f"\nErro: Já existe uma habilidade com o nome '{nome}'.")

def listar_habilidades():
    """Consulta e exibe todas as habilidades da tabela 'habilidades_base'."""
    print("\n--- Biblioteca de Habilidades ---")
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            cursor.execute("SELECT * FROM habilidades_base ORDER BY custo_mana, nome")
            habilidades = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return

    if not habilidades:
        print("A biblioteca de habilidades está vazia.")
    else:
        print(f"{'ID':<4} {'Nome':<25} {'Custo Mana':<12} {'Efeito':<20}")
        print("-" * 70)
        for hab in habilidades:
            id, nome, _, efeito, custo = hab
            print(f"{id:<4} {nome:<25} {custo:<12} {efeito:<20}")

# --- NOVA FUNÇÃO DE GERENCIAMENTO DE USUÁRIOS ---
# Esta função foi movida para fora do 'while' loop, para o lugar correto.
def listar_usuarios():
    """Consulta e exibe todos os usuários registrados no banco de dados."""
    print("\n--- Lista de Usuários Registrados ---")
    try:
        with sqlite3.connect(NOME_DB) as conexao:
            cursor = conexao.cursor()
            # Seleciona apenas o ID e o nome do usuário para não expor a senha hasheada.
            cursor.execute("SELECT id, nome_usuario FROM usuarios ORDER BY nome_usuario")
            usuarios = cursor.fetchall()

        if not usuarios:
            print("Nenhum usuário registrado ainda.")
        else:
            print(f"{'ID':<4} {'Nome de Usuário':<25}")
            print("-" * 30)
            for usuario in usuarios:
                print(f"{usuario[0]:<4} {usuario[1]:<25}")
    except Exception as e:
        print(f"Ocorreu um erro ao listar usuários: {e}")


# --- Loop Principal do Editor do Mestre ---
while True:
    print("\n" + "="*35)
    print("--- PAINEL DE CONTROLE DO MESTRE ---")
    print("="*35)
    print("\n-- Gerenciar Monstros --")
    print("1. Adicionar Monstro")
    print("2. Listar Monstros")
    print("\n-- Gerenciar Itens --")
    print("3. Adicionar Item")
    print("4. Listar Itens")
    print("\n-- Gerenciar Habilidades --")
    print("5. Adicionar Habilidade")
    print("6. Listar Habilidades")
    # --- NOVA SEÇÃO NO MENU ---
    print("\n-- Gerenciar Usuários --")
    print("7. Listar Usuários")
    print("\nDigite 'sair' para fechar.")
    
    escolha = input("> ").strip()

    if escolha == '1':
        adicionar_monstro()
    elif escolha == '2':
        listar_monstros()
    elif escolha == '3':
        adicionar_item()
    elif escolha == '4':
        listar_itens()
    elif escolha == '5':
        adicionar_habilidade()
    elif escolha == '6':
        listar_habilidades()
    # --- NOVA OPÇÃO NO MENU ---
    elif escolha == '7':
        listar_usuarios()
    elif escolha.lower() == 'sair':
        print("Fechando o painel do Mestre...")
        break
    else:
        print("Opção inválida.")