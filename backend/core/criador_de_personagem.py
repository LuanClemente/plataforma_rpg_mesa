# Importamos a nossa classe Personagem, pois vamos criar um objeto dela.
from .personagem import Personagem

def criar_personagem_interativo():
    """
    Guia o usuário através do processo de criação de personagem
    e retorna o objeto Personagem criado.
    """
    print("\n--- CRIAÇÃO DE PERSONAGEM ---")
    
    # Pede ao usuário para inserir o nome e a classe.
    nome = input("Qual o nome do seu herói? ")
    classe = input(f"Qual a classe de {nome}? (Ex: Guerreiro, Mago, Ladino) ")
    
    # Cria uma instância inicial do personagem com nível 1.
    # Os atributos ainda estão com o valor padrão de 10.
    novo_personagem = Personagem(nome=nome, classe=classe, nivel=1)
    
    # --- Distribuição de Pontos ---
    pontos_para_distribuir = 6  # Exemplo: 6 pontos para distribuir
    atributos_disponiveis = list(novo_personagem.atributos.keys())
    
    print("\n--- Distribua seus Pontos de Atributo ---")
    print(f"Você tem {pontos_para_distribuir} pontos para adicionar aos seus atributos.")
    print("Cada atributo começa com o valor base 10.")
    
    # Loop para distribuir os pontos.
    while pontos_para_distribuir > 0:
        print("\nAtributos atuais:")
        novo_personagem.mostrar_ficha() # Mostra a ficha para o usuário ver os valores
        
        print("\nEm qual atributo você quer adicionar um ponto?")
        # Mostra os atributos numerados para facilitar a escolha.
        for i, attr in enumerate(atributos_disponiveis):
            print(f"{i + 1}. {attr}")

        try:
            # Pede ao usuário para escolher um número.
            escolha = int(input("> ")) - 1 # Subtrai 1 para corresponder ao índice da lista
            
            # Verifica se a escolha é válida.
            if 0 <= escolha < len(atributos_disponiveis):
                # Pega o nome do atributo escolhido.
                atributo_escolhido = atributos_disponiveis[escolha]
                
                # Aumenta o valor do atributo no dicionário do personagem.
                novo_personagem.atributos[atributo_escolhido] += 1
                
                # Diminui os pontos restantes.
                pontos_para_distribuir -= 1
                print(f"Você adicionou um ponto em {atributo_escolhido}. Restam {pontos_para_distribuir} pontos.")
            else:
                print("Escolha inválida. Por favor, digite um número da lista.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")
            
    print("\n--- Personagem Criado com Sucesso! ---")
    novo_personagem.mostrar_ficha()
    
    # Retorna o objeto personagem totalmente configurado.
    return novo_personagem

# Bloco de teste (opcional, mas bom para testar o arquivo isoladamente)
if __name__ == '__main__':
    criar_personagem_interativo()