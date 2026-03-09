# core/combate.py

# Importa a biblioteca 'time' para adicionar pequenas pausas e melhorar o ritmo do combate.
import time
# --- CORREÇÃO DE IMPORTAÇÃO ---
# Alteramos as importações de relativas ('.') para absolutas ('backend.')
# para garantir que os módulos sejam encontrados quando executamos o servidor da raiz do projeto.
from backend.core.rolador_de_dados import rolar_dados
from backend.core.personagem import Personagem
from backend.core.monstro import Monstro
from backend.database.db_manager import buscar_detalhes_itens, buscar_detalhes_habilidades

def calcular_modificador(valor_atributo: int) -> int:
    """Calcula o modificador de um atributo seguindo a regra do D&D 5e."""
    # A fórmula é (valor do atributo - 10) / 2, arredondado para baixo.
    return (valor_atributo - 10) // 2

def turno_do_jogador(jogador: Personagem, monstro: Monstro):
    """
    Encapsula toda a lógica do turno do jogador, apresentando um menu de escolhas táticas.
    """
    while True:
        # Apresenta o menu de ações possíveis para o jogador.
        print("\n--- SEU TURNO ---")
        print("1. Atacar com Arma")
        print("2. Usar Item")
        print("3. Usar Habilidade")
        escolha = input("> ").strip()

        # --- AÇÃO: ATACAR ---
        if escolha == '1':
            # -- Lógica de Equipamento Automático --
            dado_dano_arma, bonus_ataque_arma, melhor_arma_nome = "1d2", 0, "Punhos"
            itens_no_inventario = buscar_detalhes_itens(jogador.inventario)
            armas = [item for item in itens_no_inventario if item[2].lower() == 'arma']
            if armas:
                melhor_arma = max(armas, key=lambda item: item[6])
                melhor_arma_nome, dado_dano_arma, bonus_ataque_arma = melhor_arma[1], melhor_arma[5], melhor_arma[6]
            
            print(f"Você ataca com {melhor_arma_nome}!")
            
            # -- Lógica da Rolagem de Ataque --
            mod_ataque_forca = calcular_modificador(jogador.atributos["Força"])
            rolagem_ataque, _ = rolar_dados("d20")
            total_ataque = rolagem_ataque + mod_ataque_forca + bonus_ataque_arma
            
            print(f"Rolagem: {rolagem_ataque} + {mod_ataque_forca}(For) + {bonus_ataque_arma}(Arma) = {total_ataque}")
            
            # Compara o total do ataque com a defesa (AC) do monstro.
            if total_ataque >= monstro.defesa:
                print(f"Você ACERTOU o {monstro.nome}!")
                dano_causado, _ = rolar_dados(dado_dano_arma)
                total_dano = max(1, dano_causado + mod_ataque_forca)
                monstro.vida_atual -= total_dano
                print(f"Você causa {total_dano} de dano!")
            else:
                print(f"Você ERROU o ataque.")
            
            # 'return' encerra a função e, consequentemente, o turno do jogador.
            return

        # --- AÇÃO: USAR ITEM ---
        elif escolha == '2':
            # Filtra o inventário para encontrar apenas itens com um efeito utilizável.
            itens_utilizaveis = [item for item in buscar_detalhes_itens(jogador.inventario) if item[7] is not None]
            
            if not itens_utilizaveis:
                print("Você não tem itens utilizáveis em combate.")
                continue # Volta para o menu de escolha.

            print("\nQual item você quer usar?")
            for i, item in enumerate(itens_utilizaveis):
                print(f"{i + 1}. {item[1]}") # item[1] é o nome

            try:
                escolha_item = int(input("> ")) - 1
                if 0 <= escolha_item < len(itens_utilizaveis):
                    item_usado = itens_utilizaveis[escolha_item]
                    nome_item, efeito_item = item_usado[1], item_usado[7]

                    # Processa o efeito (ex: "cura:10").
                    tipo_efeito, valor_efeito = efeito_item.split(':')
                    if tipo_efeito.lower() == 'cura':
                        jogador.curar(int(valor_efeito))
                    
                    jogador.remover_item(nome_item)
                    print(f"Você usou '{nome_item}'.")
                    return # Encerra o turno.
                else:
                    print("Escolha inválida.")
            except (ValueError, IndexError):
                print("Escolha inválida.")

        # --- AÇÃO: USAR HABILIDADE ---
        elif escolha == '3':
            if not jogador.habilidades:
                print("Você não conhece nenhuma habilidade.")
                continue

            print("\nQual habilidade você quer usar?")
            habilidades_conhecidas = buscar_detalhes_habilidades(jogador.habilidades)
            
            for i, hab in enumerate(habilidades_conhecidas):
                print(f"{i + 1}. {hab[1]} (Custo: {hab[4]} Mana)")

            try:
                escolha_hab = int(input("> ")) - 1
                if 0 <= escolha_hab < len(habilidades_conhecidas):
                    hab_usada = habilidades_conhecidas[escolha_hab]
                    nome_hab, efeito_hab, custo_mana = hab_usada[1], hab_usada[3], hab_usada[4]

                    if jogador.mana_atual >= custo_mana:
                        jogador.mana_atual -= custo_mana
                        print(f"\nVocê usa '{nome_hab}'!")
                        
                        # Processa o efeito da habilidade.
                        partes_efeito = efeito_hab.split(':')
                        tipo_efeito = partes_efeito[0].lower()
                        valor_efeito = partes_efeito[1]

                        if tipo_efeito == 'dano':
                            dano, _ = rolar_dados(valor_efeito)
                            monstro.vida_atual -= dano
                            print(f"A magia causa {dano} de dano ao {monstro.nome}!")
                        elif tipo_efeito == 'cura':
                            jogador.curar(int(valor_efeito))
                        
                        return # Encerra o turno.
                    else:
                        print("Mana insuficiente!")
                        continue
                else:
                    print("Escolha inválida.")
            except (ValueError, IndexError):
                print("Escolha inválida.")
        else:
            print("Opção inválida.")

def turno_do_monstro(jogador: Personagem, monstro: Monstro):
    """Encapsula toda a lógica do turno do monstro."""
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
    """Executa o loop de combate principal, gerenciando os turnos e o fim da batalha."""
    print(f"\n--- UM {monstro.nome.upper()} SELVAGEM APARECE! ---")
    
    # O loop principal da batalha: continua enquanto ambos os combatentes estiverem vivos.
    while jogador.vida_atual > 0 and monstro.vida_atual > 0:
        # Exibe o status da batalha no início de cada rodada.
        print(f"\nSua Vida: {jogador.vida_atual}/{jogador.vida_maxima} | Vida do {monstro.nome}: {monstro.vida_atual}/{monstro.vida_maxima}")
        
        turno_do_jogador(jogador, monstro)
        time.sleep(1)

        # Após o turno do jogador, verifica se o monstro ainda está vivo.
        if monstro.vida_atual > 0:
            turno_do_monstro(jogador, monstro)
            time.sleep(1)

    # Quando o loop termina, verifica quem venceu.
    if jogador.vida_atual <= 0:
        print("\n--- VOCÊ FOI DERROTADO ---")
        return False # Indica derrota.
    else:
        print(f"\n--- VOCÊ DERROTOU O {monstro.nome.upper()}! ---")
        # Concede as recompensas.
        jogador.ouro += monstro.ouro_drop
        print(f"Você encontrou {monstro.ouro_drop} peças de ouro!")
        jogador.ganhar_xp(monstro.xp_oferecido)
        return True # Indica vitória.