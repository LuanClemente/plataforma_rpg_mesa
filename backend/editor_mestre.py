# editor_mestre.py

import sqlite3

# O nome do nosso banco de dados.
NOME_DB = "campanhas.db"

def adicionar_monstro():
    """
    Pede ao Mestre os dados de um novo monstro e o insere no banco de dados.
    """
    print("\n--- Adicionando Novo Monstro ---")
    try:
        # Pede ao Mestre para inserir cada um dos atributos do monstro.
        nome = input("Nome do Monstro: ").strip()
        vida_maxima = int(input("Vida Máxima: "))
        ataque_bonus = int(input("Bônus de Ataque: "))
        dano_dado = input("Dado de Dano (ex: 1d8): ").strip()
        defesa = int(input("Classe de Defesa (AC): "))
        xp_oferecido = int(input("XP Oferecido: "))
        ouro_drop = int(input("Ouro Descoberto: "))

        # Conecta ao banco de dados.
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()

        # O comando SQL INSERT é usado para adicionar uma nova linha a uma tabela.
        # Usamos '?' como placeholders para os valores. Isso é uma prática de segurança
        # crucial para prevenir ataques de "SQL Injection".
        cursor.execute("""
            INSERT INTO monstros_base (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop))

        # Salva (commita) as mudanças.
        conexao.commit()
        print(f"\nMonstro '{nome}' adicionado à biblioteca com sucesso!")

    except ValueError:
        # Captura o erro se o Mestre digitar um texto onde um número é esperado.
        print("\nErro: Por favor, insira um número válido para os atributos numéricos.")
    except sqlite3.IntegrityError:
        # Captura o erro se o Mestre tentar adicionar um monstro com um nome que já existe.
        # Isso acontece por causa do 'UNIQUE' que definimos na criação da tabela.
        print(f"\nErro: Já existe um monstro com o nome '{nome}' na biblioteca.")
    finally:
        # Garante que a conexão seja fechada, mesmo que um erro ocorra.
        if 'conexao' in locals():
            conexao.close()

def listar_monstros():
    """
    Consulta o banco de dados e lista todos os monstros da biblioteca base.
    """
    print("\n--- Biblioteca de Monstros ---")
    conexao = sqlite3.connect(NOME_DB)
    cursor = conexao.cursor()

    # O comando SQL SELECT é usado para buscar dados. '*' significa 'todas as colunas'.
    cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
    
    # cursor.fetchall() busca todos os resultados da nossa consulta.
    monstros = cursor.fetchall()
    conexao.close()

    if not monstros:
        print("A biblioteca de monstros está vazia.")
    else:
        # Imprime um cabeçalho para a nossa tabela.
        print(f"{'ID':<4} {'Nome':<20} {'Vida':<5} {'Defesa':<6} {'XP':<5}")
        print("-" * 45)
        # Itera sobre cada monstro encontrado e imprime suas informações.
        # Os monstros vêm como tuplas, ex: (1, 'Goblin', 7, ...)
        for monstro in monstros:
            # Desempacota a tupla em variáveis para facilitar o acesso.
            id, nome, vida, _, _, defesa, xp, _ = monstro
            print(f"{id:<4} {nome:<20} {vida:<5} {defesa:<6} {xp:<5}")

# --- Loop Principal do Editor do Mestre ---
while True:
    print("\n--- Painel de Controle do Mestre ---")
    print("1. Adicionar Novo Monstro")
    print("2. Listar Monstros da Biblioteca")
    print("Digite 'sair' para fechar.")
    
    escolha = input("> ").strip()

    if escolha == '1':
        adicionar_monstro()
    elif escolha == '2':
        listar_monstros()
    elif escolha.lower() == 'sair':
        print("Fechando o painel do Mestre...")
        break
    else:
        print("Opção inválida.")