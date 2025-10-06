# core/combate.py
import time
from .rolador_de_dados import rolar_dados
from .personagem import Personagem
from .monstro import Monstro
from database.db_manager import buscar_detalhes_itens

def calcular_modificador(valor_atributo): return (valor_atributo - 10) // 2

def turno_do_jogador(jogador: Personagem, monstro: Monstro):
    """Encapsula toda a lógica do turno do jogador."""
    while True:
        print("\n--- SEU TURNO ---")
        print("1. Atacar")
        print("2. Usar Item")
        escolha = input("> ").strip()

        if escolha == '1':
            # --- Lógica de Ataque (movida para cá) ---
            # ... (código de equipamento e ataque que já tínhamos)
            dado_dano_arma, bonus_ataque_arma, melhor_arma_nome = "1d2", 0, "Punhos"
            itens_no_inventario = buscar_detalhes_itens(jogador.inventario)
            armas = [item for item in itens_no_inventario if item[2].lower() == 'arma']
            if armas:
                melhor_arma = max(armas, key=lambda item: item[6])
                melhor_arma_nome, dado_dano_arma, bonus_ataque_arma = melhor_arma[1], melhor_arma[5], melhor_arma[6]
            
            print(f"Você ataca com {melhor_arma_nome}!")
            mod_ataque_forca = calcular_modificador(jogador.atributos["Força"])
            rolagem_ataque, _ = rolar_dados("d20")
            total_ataque = rolagem_ataque + mod_ataque_forca + bonus_ataque_arma
            
            print(f"Rolagem: {rolagem_ataque} + {mod_ataque_forca}(For) + {bonus_ataque_arma}(Arma) = {total_ataque}")
            
            if total_ataque >= monstro.defesa:
                print(f"Você ACERTOU o {monstro.nome}!")
                dano_causado, _ = rolar_dados(dado_dano_arma)
                total_dano = max(1, dano_causado + mod_ataque_forca)
                monstro.vida_atual -= total_dano
                print(f"Você causa {total_dano} de dano!")
            else:
                print(f"Você ERROU o ataque.")
            return # Encerra o turno do jogador

        elif escolha == '2':
            # --- NOVA LÓGICA DE USAR ITEM ---
            itens_consumiveis = []
            detalhes_inventario = buscar_detalhes_itens(jogador.inventario)
            for item in detalhes_inventario:
                # item[7] é a nossa nova coluna 'efeito'
                if item[7] is not None:
                    itens_consumiveis.append(item)
            
            if not itens_consumiveis:
                print("Você não tem itens utilizáveis em combate.")
                continue # Volta para o menu de escolha (Atacar/Usar Item)

            print("\nQual item você quer usar?")
            for i, item in enumerate(itens_consumiveis):
                print(f"{i + 1}. {item[1]}") # item[1] é o nome

            try:
                escolha_item = int(input("> ")) - 1
                if 0 <= escolha_item < len(itens_consumiveis):
                    item_usado = itens_consumiveis[escolha_item]
                    nome_item = item_usado[1]
                    efeito_item = item_usado[7]

                    # Processa o efeito
                    tipo_efeito, valor_efeito = efeito_item.split(':')
                    if tipo_efeito.lower() == 'cura':
                        jogador.curar(int(valor_efeito))
                    
                    jogador.remover_item(nome_item)
                    print(f"Você usou '{nome_item}'.")
                    return # Encerra o turno do jogador
                else:
                    print("Escolha inválida.")
            except (ValueError, IndexError):
                print("Escolha inválida.")
        else:
            print("Opção inválida.")

def turno_do_monstro(jogador: Personagem, monstro: Monstro):
    """Encapsula a lógica do turno do monstro."""
    # ... (código do turno do monstro, sem alterações)
    print(f"\n--- TURNO DO {monstro.nome.upper()} ---")
    rolagem_ataque_monstro, _ = rolar_dados("d20")
    total_ataque_monstro = rolagem_ataque_monstro + monstro.ataque_bonus
    defesa_jogador = 10 + calcular_modificador(jogador.atributos["Destreza"])
    if total_ataque_monstro >= defesa_jogador:
        dano_causado, _ = rolar_dados(monstro.dano_dado)
        jogador.vida_atual -= dano_causado
        print(f"O {monstro.nome} ACERTOU e causou {dano_causado} de dano!")
    else:
        print(f"O {monstro.nome} ERROU o ataque.")

def iniciar_combate(jogador: Personagem, monstro: Monstro):
    """Executa o loop de combate principal, agora mais organizado."""
    print(f"\n--- UM {monstro.nome.upper()} SELVAGEM APARECE! ---")
    
    while jogador.vida_atual > 0 and monstro.vida_atual > 0:
        print(f"\nSua Vida: {jogador.vida_atual}/{jogador.vida_maxima} | Vida do {monstro.nome}: {monstro.vida_atual}/{monstro.vida_maxima}")
        
        turno_do_jogador(jogador, monstro)
        time.sleep(1)

        if monstro.vida_atual > 0:
            turno_do_monstro(jogador, monstro)
            time.sleep(1)

    if jogador.vida_atual <= 0:
        print("\n--- VOCÊ FOI DERROTADO ---")
        return False
    else:
        print(f"\n--- VOCÊ DERROTOU O {monstro.nome.upper()}! ---")
        jogador.ouro += monstro.ouro_drop
        print(f"Você encontrou {monstro.ouro_drop} peças de ouro!")
        jogador.ganhar_xp(monstro.xp_oferecido)
        return True