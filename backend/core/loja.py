# core/loja.py

# A loja precisa saber como buscar os itens no DB e interagir com o jogador.
from database.db_manager import buscar_todos_os_itens
from core.personagem import Personagem

def iniciar_loja(jogador: Personagem):
    """
    Inicia o loop de interação da loja para o jogador.
    """
    print("\n" + "="*40)
    print("  Bem-vindo ao Mercador Risonho!")
    print("  Aqui tenho os melhores produtos da região!")
    print("="*40)

    # Busca o inventário da loja no banco de dados.
    inventario_loja = buscar_todos_os_itens()

    if not inventario_loja:
        print("\nO mercador parece estar sem estoque hoje. Volte mais tarde!")
        return

    while True:
        print(f"\nVocê possui {jogador.ouro} peças de ouro.")
        print("\n--- Itens à Venda ---")
        # Mostra cada item numerado. Os dados vêm numa tupla: (id, nome, tipo, desc, preco)
        for i, item in enumerate(inventario_loja):
            print(f"{i + 1}. {item[1]:<25} | Preço: {item[4]} Ouro")
        
        print("\nDigite o número do item para comprar, ou 'sair' para ir embora.")
        escolha = input("> ").strip().lower()

        if escolha == 'sair':
            print("\nO mercador acena enquanto você sai. \"Volte sempre!\"")
            break
        
        try:
            indice_escolhido = int(escolha) - 1
            if 0 <= indice_escolhido < len(inventario_loja):
                item_selecionado = inventario_loja[indice_escolhido]
                nome_item = item_selecionado[1]
                preco_item = item_selecionado[4]

                # Verifica se o jogador tem ouro suficiente.
                if jogador.ouro >= preco_item:
                    # Processa a compra
                    jogador.ouro -= preco_item
                    jogador.adicionar_item(nome_item)
                    print(f"\nVocê comprou '{nome_item}' por {preco_item} de ouro!")
                else:
                    print("\nVocê conta suas moedas... ouro insuficiente.")
            else:
                print("\nNúmero de item inválido.")
        except ValueError:
            print("\nComando inválido. Por favor, digite um número ou 'sair'.")