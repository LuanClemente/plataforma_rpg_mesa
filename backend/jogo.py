# jogo.py

# Importamos a nossa nova função do db_manager
from db_manager import buscar_monstro_aleatorio
from criador_de_personagem import criar_personagem_interativo
from gerenciador_de_personagens import salvar_personagem, carregar_personagem
from combate import iniciar_combate

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
    print("1. Procurar encrenca (Combate!)")
    print("2. Ver a ficha completa do personagem")
    print("3. Salvar progresso")
    print("Digite 'sair' para terminar a aventura.")

    escolha = input("> ").strip()

    if escolha == '1':
        # --- LÓGICA DE COMBATE TOTALMENTE DINÂMICA ---
        print("\nVocê explora os arredores em busca de ação...")
        
        # Chamamos nossa nova função para buscar um monstro aleatório no DB.
        monstro_encontrado = buscar_monstro_aleatorio()
        
        # Verificamos se um monstro foi realmente encontrado.
        if monstro_encontrado:
            # Se sim, iniciamos o combate com a criatura que o DB nos deu!
            vitoria = iniciar_combate(jogador, monstro_encontrado)
            
            if vitoria:
                print("Você se sente mais forte após a batalha!")
            else:
                print("Você precisa descansar para recuperar suas forças...")
            
            # Após o combate, salvamos o estado do jogador (vida, xp, ouro, etc.)
            salvar_personagem(jogador)
        else:
            # Se não, informamos ao jogador que nada aconteceu.
            print("...mas a área parece estranhamente calma. Nenhum monstro encontrado.")

    elif escolha == '2':
        jogador.mostrar_ficha()
    elif escolha == '3':
        salvar_personagem(jogador)
    elif escolha.lower() == 'sair':
        print("A sua jornada termina aqui... por enquanto.")
        break
    else:
        print("Comando desconhecido, nobre aventureiro.")