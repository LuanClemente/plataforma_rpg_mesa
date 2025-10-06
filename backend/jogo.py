# backend/jogo.py

# --- Importações dos Nossos Módulos ---
# Cada importação traz uma "ferramenta" de um dos nossos módulos especializados.

# Da pasta 'database', importa a função para buscar um monstro aleatório.
from database.db_manager import buscar_monstro_aleatorio
# Da pasta 'core', importa a função que guia o jogador na criação de um novo personagem.
from core.criador_de_personagem import criar_personagem_interativo
# Da pasta 'saves', importa as funções para salvar e carregar o progresso do personagem.
from saves.saves_manager import salvar_personagem, carregar_personagem
# Da pasta 'core', importa a função principal que gerencia uma batalha.
from core.combate import iniciar_combate
# Da pasta 'core', importa a função que gerencia a experiência do jogador na loja.
from core.loja import iniciar_loja

# --- Menu Inicial do Jogo ---

# Inicializa a variável 'jogador' como None. O jogo só começará de fato quando esta variável contiver um objeto Personagem.
jogador = None
# Este loop 'while' continua até que um personagem seja criado ou carregado com sucesso.
while jogador is None:
    # Imprime o menu inicial para o usuário a cada tentativa.
    print("\n" + "="*42)
    print("--- BEM-VINDO À PLATAFORMA RPG DE MESA ---")
    print("="*42)
    print("1. Criar Novo Personagem")
    print("2. Carregar Personagem Existente")
    # Pede a escolha do usuário e '.strip()' remove espaços em branco acidentais.
    escolha_inicial = input("> ").strip()

    # Se o jogador escolher a opção '1'...
    if escolha_inicial == '1':
        # ...chama a função do módulo 'criador_de_personagem', que retorna um objeto Personagem completo.
        jogador = criar_personagem_interativo()
        # Define alguns itens e ouro iniciais para o novo herói.
        jogador.ouro = 25
        jogador.adicionar_item("Adaga")
        jogador.adicionar_item("Mapa da região")
        # Salva o personagem recém-criado imediatamente para que ele possa ser carregado no futuro.
        salvar_personagem(jogador)
    # Se o jogador escolher a opção '2'...
    elif escolha_inicial == '2':
        # ...pede o nome do personagem a ser carregado.
        nome = input("Qual o nome do personagem que deseja carregar? ")
        # Chama a função de carregamento. Se o personagem não for encontrado, ela retorna None,
        # e o loop 'while jogador is None' continuará, mostrando o menu novamente.
        jogador = carregar_personagem(nome)
    # Se a escolha for qualquer outra coisa...
    else:
        # ...informa ao usuário que a opção é inválida.
        print("Opção inválida.")

# --- Loop Principal do Jogo ---

# Esta linha só é alcançada após um personagem ser carregado ou criado com sucesso.
print(f"\n--- A aventura de {jogador.nome} começa! ---")

# Este é o loop principal do jogo. Ele continuará para sempre até que o jogador decida 'sair'.
while True:
    # A cada rodada, exibe o menu de ações principais.
    print("\n--- O que você deseja fazer? ---")
    print("1. Procurar encrenca (Combate!)")
    print("2. Ver a ficha completa do personagem")
    print("3. Visitar o Mercador Risonho (Loja)")
    print("4. Salvar progresso")
    print("Digite 'sair' para terminar a aventura.")

    # Pede a escolha do jogador.
    escolha = input("> ").strip()

    # --- Lógica de Combate ---
    if escolha == '1':
        print("\nVocê explora os arredores em busca de ação...")
        # Chama o db_manager para buscar um monstro aleatório da biblioteca.
        monstro_encontrado = buscar_monstro_aleatorio()
        
        # Se um monstro for encontrado (a biblioteca não está vazia)...
        if monstro_encontrado:
            # ...chama o módulo de combate, passando o jogador e o monstro como participantes.
            vitoria = iniciar_combate(jogador, monstro_encontrado)
            
            # Reage ao resultado do combate (True para vitória, False para derrota).
            if vitoria:
                print("Você se sente mais forte após a batalha!")
            else:
                print("Você precisa descansar para recuperar suas forças...")
            
            # Após o combate, o estado do jogador (vida, xp, ouro) pode ter mudado, então salvamos o progresso.
            salvar_personagem(jogador)
        else:
            # Se a biblioteca de monstros estiver vazia, informa ao jogador.
            print("...mas a área parece estranhamente calma. Nenhum monstro encontrado.")

    # --- Lógica de Ver a Ficha ---
    elif escolha == '2':
        # Simplesmente chama o método 'mostrar_ficha' do próprio objeto do jogador.
        jogador.mostrar_ficha()
        
    # --- Lógica da Loja ---
    elif escolha == '3':
        # Chama o módulo da loja, passando o objeto do jogador para que a loja possa interagir com seu ouro e inventário.
        iniciar_loja(jogador)

    # --- Lógica de Salvar ---
    elif escolha == '4':
        # Chama a função de salvamento do saves_manager.
        salvar_personagem(jogador)

    # --- Lógica de Sair ---
    elif escolha.lower() == 'sair':
        # Imprime uma mensagem de despedida.
        print("A sua jornada termina aqui... por enquanto.")
        # O comando 'break' interrompe o loop 'while True' e encerra o programa.
        break
        
    # --- Lógica para Escolha Inválida ---
    else:
        print("Comando desconhecido, nobre aventureiro.")