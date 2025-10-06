# jogo.py

from database.db_manager import buscar_monstro_aleatorio
from core.criador_de_personagem import criar_personagem_interativo
from saves.saves_manager import salvar_personagem, carregar_personagem
from core.combate import iniciar_combate
# Importamos nossa nova função da loja!
from core.loja import iniciar_loja

# --- Menu Inicial do Jogo (sem alterações) ---
jogador = None
while jogador is None:
    # ... (código do menu inicial permanece o mesmo)
    print("\n--- BEM-VINDO À PLATAFORMA RPG DE MESA ---")
    print("1. Criar Novo Personagem")
    print("2. Carregar Personagem Existente")
    escolha_inicial = input("> ").strip()
    if escolha_inicial == '1':
        jogador = criar_personagem_interativo()
        jogador.ouro = 25 # Começando com um pouco mais de ouro
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
    print("3. Visitar o Mercador Risonho (Loja)") # NOVA OPÇÃO
    print("4. Salvar progresso")
    print("Digite 'sair' para terminar a aventura.")

    escolha = input("> ").strip()

    if escolha == '1':
        # ... (código do combate, sem alterações)
        monstro_encontrado = buscar_monstro_aleatorio()
        if monstro_encontrado:
            vitoria = iniciar_combate(jogador, monstro_encontrado)
            if vitoria: print("Você se sente mais forte após a batalha!")
            else: print("Você precisa descansar para recuperar suas forças...")
            salvar_personagem(jogador)
        else:
            print("...mas a área parece estranhamente calma. Nenhum monstro encontrado.")

    elif escolha == '2':
        jogador.mostrar_ficha()
        
    elif escolha == '3':
        # Chama a função da loja que acabamos de criar!
        iniciar_loja(jogador)

    elif escolha == '4':
        salvar_personagem(jogador)

    elif escolha.lower() == 'sair':
        print("A sua jornada termina aqui... por enquanto.")
        break
    else:
        print("Comando desconhecido, nobre aventureiro.")