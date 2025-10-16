# core/criador_de_personagem.py

# --- CORREÇÃO DE IMPORTAÇÃO ---
# Alteramos a importação de relativa ('.') para absoluta ('backend.')
# Isso permite que este script seja chamado corretamente a partir da raiz do projeto.
from backend.core.personagem import Personagem

def criar_personagem_interativo():
    """
    Guia o usuário através de um processo interativo de criação de personagem no console,
    incluindo a distribuição de pontos de atributo.
    Ao final, retorna o objeto Personagem recém-criado.
    """
    # Imprime um cabeçalho para indicar o início do processo de criação.
    print("\n" + "="*29)
    print("--- CRIAÇÃO DE PERSONAGEM ---")
    print("="*29)
    
    # Pede ao usuário para inserir o nome e a classe do seu herói.
    nome = input("Qual o nome do seu herói? ").strip()
    classe = input(f"Qual a classe de {nome}? (Ex: Guerreiro, Mago, Ladino) ").strip()
    
    # Cria uma instância inicial do personagem com nível 1.
    novo_personagem = Personagem(nome=nome, classe=classe, nivel=1)
    
    # --- Seção de Distribuição de Pontos de Atributo ---
    pontos_para_distribuir = 6
    atributos_disponiveis = list(novo_personagem.atributos.keys())
    
    print("\n--- Distribua seus Pontos de Atributo ---")
    print(f"Você tem {pontos_para_distribuir} pontos para adicionar aos seus atributos (base 10).")
    
    # O loop 'while' continua enquanto o jogador ainda tiver pontos para gastar.
    while pontos_para_distribuir > 0:
        # Mostra a ficha atual do personagem.
        novo_personagem.mostrar_ficha()
        
        print(f"\nPontos restantes: {pontos_para_distribuir}")
        print("Em qual atributo você quer adicionar um ponto?")
        
        # Cria um menu numerado de atributos.
        for i, attr in enumerate(atributos_disponiveis):
            print(f"{i + 1}. {attr}")

        try:
            # Pede ao jogador para escolher um número.
            escolha = int(input("> ")) - 1 # Converte a escolha base 1 para o índice base 0.
            
            # Verifica se a escolha é válida.
            if 0 <= escolha < len(atributos_disponiveis):
                atributo_escolhido = atributos_disponiveis[escolha]
                novo_personagem.atributos[atributo_escolhido] += 1
                pontos_para_distribuir -= 1
                print(f"Você adicionou um ponto em {atributo_escolhido}.")
            else:
                print("Escolha inválida. Por favor, digite um número da lista.")
        except ValueError:
            # Captura o erro se o usuário digitar algo que não seja um número.
            print("Entrada inválida. Por favor, digite um número.")
            
    print("\n--- Personagem Criado com Sucesso! ---")
    novo_personagem.mostrar_ficha()
    
    # Retorna o objeto 'Personagem' completo e customizado.
    return novo_personagem