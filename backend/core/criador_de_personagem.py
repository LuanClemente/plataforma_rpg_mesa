# core/criador_de_personagem.py

# Importa a classe 'Personagem' do módulo vizinho 'personagem.py' (dentro do mesmo pacote 'core').
# O '.' no início indica que a importação é relativa ao pacote atual.
from .personagem import Personagem

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
    # A função input() pausa o programa e espera o usuário digitar e pressionar Enter.
    # .strip() remove espaços em branco acidentais do início e do fim.
    nome = input("Qual o nome do seu herói? ").strip()
    classe = input(f"Qual a classe de {nome}? (Ex: Guerreiro, Mago, Ladino) ").strip()
    
    # Cria uma instância inicial do personagem com nível 1 e os dados fornecidos.
    # Neste ponto, os atributos (Força, Destreza, etc.) ainda estão com o valor padrão de 10.
    novo_personagem = Personagem(nome=nome, classe=classe, nivel=1)
    
    # --- Seção de Distribuição de Pontos de Atributo ---
    
    # Define uma quantidade de pontos bônus que o jogador pode distribuir.
    pontos_para_distribuir = 6
    # Pega a lista de nomes dos atributos (['Força', 'Destreza', ...]) do dicionário do personagem.
    atributos_disponiveis = list(novo_personagem.atributos.keys())
    
    # Imprime as instruções para o jogador.
    print("\n--- Distribua seus Pontos de Atributo ---")
    print(f"Você tem {pontos_para_distribuir} pontos para adicionar aos seus atributos (base 10).")
    
    # O loop 'while' continua enquanto o jogador ainda tiver pontos para gastar.
    while pontos_para_distribuir > 0:
        # Mostra a ficha atual do personagem para que o jogador veja o estado dos atributos.
        novo_personagem.mostrar_ficha()
        
        # Informa quantos pontos ainda restam.
        print(f"\nPontos restantes: {pontos_para_distribuir}")
        print("Em qual atributo você quer adicionar um ponto?")
        
        # A função 'enumerate' nos dá o índice (i) e o valor (attr) ao mesmo tempo.
        # Usamos isso para criar um menu numerado de atributos para o jogador escolher.
        for i, attr in enumerate(atributos_disponiveis):
            # Imprime, por exemplo, "1. Força".
            print(f"{i + 1}. {attr}")

        # O bloco 'try...except' lida com a possibilidade de o jogador digitar um texto em vez de um número.
        try:
            # Pede ao jogador para escolher um número.
            escolha = int(input("> ")) - 1 # Subtrai 1 para o número do menu (começa em 1) corresponder ao índice da lista (começa em 0).
            
            # Verifica se o número escolhido está dentro do intervalo válido de índices da lista.
            if 0 <= escolha < len(atributos_disponiveis):
                # Pega o nome do atributo correspondente ao número escolhido.
                atributo_escolhido = atributos_disponiveis[escolha]
                
                # Aumenta o valor do atributo escolhido no dicionário do personagem.
                novo_personagem.atributos[atributo_escolhido] += 1
                
                # Diminui a quantidade de pontos que ainda podem ser distribuídos.
                pontos_para_distribuir -= 1
                # Informa ao jogador a ação que foi realizada.
                print(f"Você adicionou um ponto em {atributo_escolhido}.")
            else:
                # Informa ao jogador se o número digitado for inválido (ex: 7 ou -1).
                print("Escolha inválida. Por favor, digite um número da lista.")
        except ValueError:
            # Informa ao jogador se ele digitou algo que não pode ser convertido em número.
            print("Entrada inválida. Por favor, digite um número.")
            
    # Mensagem final após a distribuição de todos os pontos.
    print("\n--- Personagem Criado com Sucesso! ---")
    # Mostra a ficha finalizada para o jogador.
    novo_personagem.mostrar_ficha()
    
    # Retorna o objeto 'Personagem' completo e customizado, pronto para ser usado no jogo principal.
    return novo_personagem