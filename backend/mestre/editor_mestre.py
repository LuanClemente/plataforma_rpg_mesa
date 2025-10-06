# mestre/editor_mestre.py

# Importa a biblioteca para interagir com o banco de dados SQLite.
import sqlite3

# Define o caminho para o arquivo do banco de dados.
# Este é o caminho correto, relativo à pasta 'backend', de onde executamos os scripts.
NOME_DB = "database/campanhas.db"

# --- Funções de Gerenciamento de Monstros ---

def adicionar_monstro():
    """Pede ao Mestre os dados de um novo monstro e o insere na tabela 'monstros_base'."""
    # Imprime um cabeçalho para a seção, guiando o Mestre.
    print("\n--- Adicionando Novo Monstro ---")
    # O bloco 'try' nos permite tentar executar um código que pode gerar erros.
    try:
        # Usa a função input() para pedir cada dado do monstro ao Mestre.
        # .strip() remove espaços em branco extras do início e do fim do texto digitado.
        nome = input("Nome do Monstro: ").strip()
        # int() converte o texto digitado em um número inteiro. Se não for um número, gera um erro 'ValueError'.
        vida_maxima = int(input("Vida Máxima: "))
        ataque_bonus = int(input("Bônus de Ataque: "))
        dano_dado = input("Dado de Dano (ex: 1d8): ").strip()
        defesa = int(input("Classe de Defesa (AC): "))
        xp_oferecido = int(input("XP Oferecido: "))
        ouro_drop = int(input("Ouro Descoberto: "))
        
        # Conecta-se ao banco de dados especificado em NOME_DB.
        conexao = sqlite3.connect(NOME_DB)
        # Cria o cursor, que é o objeto usado para executar os comandos SQL.
        cursor = conexao.cursor()
        # Executa o comando SQL 'INSERT' para adicionar a nova criatura.
        # Os '?' são placeholders que são substituídos de forma segura pelos valores na tupla logo abaixo.
        cursor.execute(
            "INSERT INTO monstros_base (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop)
        )
        # Salva (commita) a transação, tornando a inserção dos dados permanente no arquivo do banco de dados.
        conexao.commit()
        # Informa ao Mestre que a operação foi bem-sucedida.
        print(f"\nMonstro '{nome}' adicionado à biblioteca com sucesso!")

    # O bloco 'except' captura erros específicos que possam ter ocorrido no bloco 'try'.
    except ValueError:
        # Este erro ocorre se o Mestre digitar um texto em um campo que espera um número.
        print("\nErro: Por favor, insira um número válido para os atributos numéricos.")
    except sqlite3.IntegrityError:
        # Este erro ocorre se o Mestre tentar inserir um monstro com um 'nome' que já existe (devido à restrição UNIQUE na tabela).
        print(f"\nErro: Já existe um monstro com o nome '{nome}' na biblioteca.")
    finally:
        # O bloco 'finally' é sempre executado, tenha ocorrido um erro ou não.
        # 'if 'conexao' in locals()' verifica se a variável 'conexao' foi criada antes de tentar fechá-la.
        if 'conexao' in locals():
            # Garante que a conexão com o banco de dados seja sempre fechada para liberar o recurso.
            conexao.close()

def listar_monstros():
    """Consulta e exibe todos os monstros da tabela 'monstros_base'."""
    print("\n--- Biblioteca de Monstros ---")
    conexao = sqlite3.connect(NOME_DB)
    cursor = conexao.cursor()
    # Executa o comando SQL 'SELECT' para buscar todos os monstros. 'ORDER BY nome' organiza o resultado em ordem alfabética.
    cursor.execute("SELECT * FROM monstros_base ORDER BY nome")
    # 'fetchall()' busca todos os resultados da consulta e os retorna como uma lista de tuplas.
    monstros = cursor.fetchall()
    conexao.close()

    # Verifica se a lista retornada pelo banco de dados está vazia.
    if not monstros:
        print("A biblioteca de monstros está vazia.")
    else:
        # Imprime um cabeçalho formatado para a tabela de resultados.
        print(f"{'ID':<4} {'Nome':<20} {'Vida':<5} {'Defesa':<6} {'XP':<5}")
        print("-" * 45)
        # Itera sobre cada tupla (monstro) na lista de monstros.
        for monstro in monstros:
            # Desempacota a tupla em variáveis. Usamos '_' para ignorar valores que não vamos exibir na lista.
            id, nome, vida, _, _, defesa, xp, _ = monstro
            # Imprime os dados formatados, alinhados com o cabeçalho para uma visualização limpa.
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

        # Inicializa as variáveis específicas de tipo com valores padrão (None para texto, 0 para número).
        dano_dado, bonus_ataque, efeito = None, 0, None
        
        # Verifica o tipo do item (em minúsculas) para pedir informações adicionais relevantes.
        if tipo.lower() == 'arma':
            dano_dado = input("Dado de Dano da Arma (ex: 1d8): ").strip()
            bonus_ataque = int(input("Bônus de Ataque da Arma (ex: 0, 1): "))
        elif tipo.lower() == 'poção':
            efeito = input("Efeito do Item (ex: cura:10): ").strip()

        conexao = sqlite3.connect(NOME_DB) # Usando a constante global
        cursor = conexao.cursor()
        # Executa o comando INSERT com todas as colunas da tabela de itens, incluindo as que podem ser nulas.
        cursor.execute(
            "INSERT INTO itens_base (nome, tipo, descricao, preco_ouro, dano_dado, bonus_ataque, efeito) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, tipo, descricao, preco_ouro, dano_dado, bonus_ataque, efeito)
        )
        conexao.commit()
        print(f"\nItem '{nome}' adicionado à biblioteca com sucesso!")
    except ValueError:
        print("\nErro: Por favor, insira um número válido para preço ou bônus de ataque.")
    except sqlite3.IntegrityError:
        print(f"\nErro: Já existe um item com o nome '{nome}' na biblioteca.")
    finally:
        if 'conexao' in locals():
            conexao.close()

def listar_itens():
    """Consulta e exibe todos os itens da tabela 'itens_base'."""
    print("\n--- Biblioteca de Itens ---")
    conexao = sqlite3.connect(NOME_DB)
    cursor = conexao.cursor()
    # Busca todos os itens, ordenados primeiro por tipo e depois por nome, para agrupar itens similares.
    cursor.execute("SELECT * FROM itens_base ORDER BY tipo, nome")
    itens = cursor.fetchall()
    conexao.close()

    if not itens:
        print("A biblioteca de itens está vazia.")
    else:
        print(f"{'ID':<4} {'Nome':<25} {'Tipo':<15} {'Preço':<10}")
        print("-" * 60)
        # Itera sobre cada item na lista de resultados.
        for item in itens:
            # Desempacota todos os 8 valores da tupla para evitar erros.
            # Usamos '_' para ignorar os que não vamos exibir na lista.
            id, nome, tipo, _descricao, preco, _dano, _bonus, _efeito = item
            print(f"{id:<4} {nome:<25} {tipo:<15} {preco:<10} Ouro")

# --- Funções de Gerenciamento de Habilidades ---

def adicionar_habilidade():
    """Pede ao Mestre os dados de uma nova habilidade e a insere na tabela 'habilidades_base'."""
    print("\n--- Adicionando Nova Habilidade/Magia ---")
    try:
        nome = input("Nome da Habilidade: ").strip()
        descricao = input("Descrição: ").strip()
        efeito = input("Efeito (ex: dano:2d6:fogo, cura:15, buff:defesa:2): ").strip()
        custo_mana = int(input("Custo de Mana: "))
        
        conexao = sqlite3.connect(NOME_DB)
        cursor = conexao.cursor()
        # Executa o comando INSERT para a tabela de habilidades.
        cursor.execute(
            "INSERT INTO habilidades_base (nome, descricao, efeito, custo_mana) VALUES (?, ?, ?, ?)",
            (nome, descricao, efeito, custo_mana)
        )
        conexao.commit()
        print(f"\nHabilidade '{nome}' adicionada à biblioteca com sucesso!")
    except ValueError:
        print("\nErro: Custo de Mana deve ser um número.")
    except sqlite3.IntegrityError:
        print(f"\nErro: Já existe uma habilidade com o nome '{nome}'.")
    finally:
        if 'conexao' in locals():
            conexao.close()

def listar_habilidades():
    """Consulta e exibe todas as habilidades da tabela 'habilidades_base'."""
    print("\n--- Biblioteca de Habilidades ---")
    conexao = sqlite3.connect(NOME_DB)
    cursor = conexao.cursor()
    # Busca todas as habilidades, ordenadas pelo custo de mana e depois pelo nome.
    cursor.execute("SELECT * FROM habilidades_base ORDER BY custo_mana, nome")
    habilidades = cursor.fetchall()
    conexao.close()
    if not habilidades:
        print("A biblioteca de habilidades está vazia.")
    else:
        print(f"{'ID':<4} {'Nome':<25} {'Custo Mana':<12} {'Efeito':<20}")
        print("-" * 70)
        for hab in habilidades:
            # Desempacota a tupla de habilidade.
            id, nome, _, efeito, custo = hab
            print(f"{id:<4} {nome:<25} {custo:<12} {efeito:<20}")

# --- Loop Principal do Editor do Mestre ---
# Este loop infinito mantém o programa rodando e exibindo o menu até que o Mestre decida sair.
while True:
    # Imprime o menu de opções a cada ciclo do loop.
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
    print("\nDigite 'sair' para fechar.")
    
    # Pede a escolha do Mestre e remove espaços em branco.
    escolha = input("> ").strip()

    # Com base na escolha, chama a função correspondente.
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
    elif escolha.lower() == 'sair':
        # Se a escolha for 'sair', imprime uma mensagem de despedida e usa 'break' para sair do loop while.
        print("Fechando o painel do Mestre...")
        break
    else:
        # Se a escolha for inválida, informa o Mestre para que ele tente novamente.
        print("Opção inválida.")