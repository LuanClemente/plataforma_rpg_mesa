# core/loja.py

# --- CORREÇÃO DE IMPORTAÇÃO ---
# Alteramos as importações de relativas para absolutas, a partir da raiz 'backend'.
from backend.database.db_manager import buscar_todos_os_itens
from backend.core.personagem import Personagem

def iniciar_loja(jogador: Personagem):
    """
    Inicia e gerencia o loop de interação da loja para o jogador.
    Recebe o objeto do jogador para poder verificar seu ouro e adicionar itens.
    
    (Esta é uma função do nosso jogo de terminal original e não é usada pela API/Frontend).
    """
    # Imprime uma mensagem temática de boas-vindas para a loja.
    print("\n" + "="*40)
    print("  Bem-vindo ao Mercador Risonho!")
    print("  Aqui tenho os melhores produtos da região!")
    print("="*40)

    # Chama a função do db_manager para buscar a lista de todos os itens disponíveis para venda.
    inventario_loja = buscar_todos_os_itens()

    # Se a função retornar uma lista vazia (nenhum item no DB), exibe uma mensagem e encerra a função.
    if not inventario_loja:
        print("\nO mercador parece estar sem estoque hoje. Volte mais tarde!")
        return

    # O loop 'while True' mantém o jogador dentro da loja até que ele decida sair.
    while True:
        # Exibe a quantidade de ouro que o jogador possui no momento.
        print(f"\nVocê possui {jogador.ouro} peças de ouro.")
        print("\n--- Itens à Venda ---")
        
        # Itera sobre a lista de itens (tuplas) retornada pelo banco de dados para exibi-los.
        for i, item in enumerate(inventario_loja):
            # Formata e imprime cada item da loja de forma organizada.
            # item[1] é o nome, item[4] é o preco_ouro.
            print(f"{i + 1}. {item[1]:<25} | Preço: {item[4]} Ouro")
        
        # Pede ao jogador para fazer uma escolha.
        print("\nDigite o número do item para comprar, ou 'sair' para ir embora.")
        escolha = input("> ").strip().lower()

        # Se o jogador digitar 'sair', o loop é interrompido com 'break'.
        if escolha == 'sair':
            print("\nO mercador acena enquanto você sai. \"Volte sempre!\"")
            break
        
        # O bloco 'try...except' trata o caso de o jogador digitar um texto que não seja um número.
        try:
            # Converte a escolha do jogador para um número e subtrai 1 para corresponder ao índice da lista.
            indice_escolhido = int(escolha) - 1
            
            # Verifica se o número escolhido corresponde a um item válido na lista da loja.
            if 0 <= indice_escolhido < len(inventario_loja):
                item_selecionado = inventario_loja[indice_escolhido]
                nome_item = item_selecionado[1]
                preco_item = item_selecionado[4]

                # A verificação principal: o jogador tem ouro suficiente?
                if jogador.ouro >= preco_item:
                    # Se sim, processa a compra.
                    jogador.ouro -= preco_item
                    jogador.adicionar_item(nome_item)
                    print(f"\nVocê comprou '{nome_item}' por {preco_item} de ouro!")
                else:
                    # Se não tiver ouro suficiente, informa ao jogador.
                    print("\nVocê conta suas moedas... ouro insuficiente.")
            else:
                # Informa se o número digitado estiver fora do intervalo de opções.
                print("\nNúmero de item inválido.")
        except ValueError:
            # Informa se a entrada não puder ser convertida para um número.
            print("\nComando inválido. Por favor, digite um número ou 'sair'.")