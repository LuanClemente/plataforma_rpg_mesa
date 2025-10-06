# jogo.py

from rolador_de_dados import rolar_dados
from criador_de_personagem import criar_personagem_interativo
from gerenciador_de_personagens import salvar_personagem, carregar_personagem
# Nossos novos módulos!
from monstro import Monstro
from combate import iniciar_combate

def calcular_modificador(valor_atributo):
    return (valor_atributo - 10) // 2

# --- Menu Inicial do Jogo (sem alterações) ---
jogador = None
while jogador is None:
    print("\n--- BEM-VINDO À PLATAFORMA RPG DE MESA ---")
    print("1. Criar Novo Personagem")
    print("2. Carregar Personagem Existente")
    escolha_inicial = input("> ").strip()
    if escolha_inicial == '1':
        jogador = criar_personagem_interativo()
        jogador.ouro = 15
        jogador.adicionar_item("Adaga")
        jogador.adicionar_item("Mapa da região")
        salvar_personagem(jogador)
    elif escolha_inicial == '2':
        nome = input("Qual o nome do personagem que deseja carregar? ")
        jogador = carregar_personagem(nome)
    else:
        print("Opção inválida.")

# --- Loop Principal do Jogo ATUALIZADO ---
print(f"\n--- A aventura de {jogador.nome} começa! ---")
while True:
    print("\n--- O que você deseja fazer? ---")
    print("1. Procurar encrenca (Combate!)") # NOVA OPÇÃO
    print("2. Ver a ficha completa do personagem")
    print("3. Salvar progresso")
    print("Digite 'sair' para terminar a aventura.")

    escolha = input("> ").strip()

    if escolha == '1':
        # Cria uma instância de um monstro para a batalha
        goblin = Monstro(nome="Goblin", vida_maxima=7, ataque_bonus=4, dano_dado="1d6", defesa=12, xp_oferecido=50, ouro_drop=10)
        
        # Chama a função de combate e passa o jogador e o monstro
        vitoria = iniciar_combate(jogador, goblin)
        
        if vitoria:
            print("Você se sente mais forte após a batalha!")
            # Aqui poderíamos dar recompensas (ouro, XP, etc.)
        else:
            print("Você precisa descansar para recuperar suas forças...")
            # Aqui poderíamos aplicar penalidades ou levar o jogador para uma "cidade"
        
        # O estado do jogador (vida, etc.) foi alterado, então é uma boa ideia salvar.
        salvar_personagem(jogador)

    elif escolha == '2':
        jogador.mostrar_ficha()
    elif escolha == '3':
        salvar_personagem(jogador)
    elif escolha.lower() == 'sair':
        print("A sua jornada termina aqui... por enquanto.")
        break
    else:
        print("Comando desconhecido, nobre aventureiro.")