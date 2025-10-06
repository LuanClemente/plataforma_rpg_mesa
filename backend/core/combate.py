# core/combate.py

# Importa a biblioteca 'time' para adicionar pequenas pausas e melhorar o ritmo do combate.
import time
# Importa nossas funções e classes dos outros módulos do pacote 'core'.
# O '.' no início significa "do mesmo pacote/pasta atual".
from .rolador_de_dados import rolar_dados
from .personagem import Personagem
from .monstro import Monstro
# Importa as funções de busca do nosso gerenciador de banco de dados.
from database.db_manager import buscar_detalhes_itens, buscar_detalhes_habilidades

def calcular_modificador(valor_atributo: int) -> int:
    """Calcula o modificador de um atributo seguindo a regra do D&D 5e."""
    # A fórmula é (valor do atributo - 10) / 2, arredondado para baixo.
    # O operador '//' faz uma divisão de inteiros, que já executa o arredondamento.
    return (valor_atributo - 10) // 2

def turno_do_jogador(jogador: Personagem, monstro: Monstro):
    """
    Encapsula toda a lógica do turno do jogador, apresentando um menu de escolhas táticas.
    O loop 'while True' continua até o jogador realizar uma ação válida que encerre seu turno (usando 'return').
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
            # Define os valores padrão para um ataque desarmado.
            dado_dano_arma, bonus_ataque_arma, melhor_arma_nome = "1d2", 0, "Punhos"
            # Busca no banco de dados os detalhes de todos os itens no inventário do jogador.
            itens_no_inventario = buscar_detalhes_itens(jogador.inventario)
            # Filtra a lista para conter apenas os itens do tipo 'Arma'.
            armas = [item for item in itens_no_inventario if item[2].lower() == 'arma']
            # Se o jogador possuir alguma arma...
            if armas:
                # ...encontra a melhor arma. 'max()' com 'key' permite encontrar o item com o maior valor em um índice específico.
                # item[6] é a coluna 'bonus_ataque' na nossa tupla de dados do item.
                melhor_arma = max(armas, key=lambda item: item[6])
                # Atualiza as variáveis de combate com os dados da melhor arma encontrada.
                melhor_arma_nome, dado_dano_arma, bonus_ataque_arma = melhor_arma[1], melhor_arma[5], melhor_arma[6]
            
            print(f"Você ataca com {melhor_arma_nome}!")
            
            # -- Lógica da Rolagem de Ataque --
            # Calcula o modificador de Força do jogador.
            mod_ataque_forca = calcular_modificador(jogador.atributos["Força"])
            # Rola um d20 para o ataque.
            rolagem_ataque, _ = rolar_dados("d20")
            # O total do ataque é a soma da rolagem, do modificador de Força e do bônus da arma.
            total_ataque = rolagem_ataque + mod_ataque_forca + bonus_ataque_arma
            
            print(f"Rolagem: {rolagem_ataque} + {mod_ataque_forca}(For) + {bonus_ataque_arma}(Arma) = {total_ataque}")
            
            # Compara o total do ataque com a defesa (AC) do monstro.
            if total_ataque >= monstro.defesa:
                print(f"Você ACERTOU o {monstro.nome}!")
                # Rola o dado de dano da arma equipada.
                dano_causado, _ = rolar_dados(dado_dano_arma)
                # O dano total é a soma do dano da arma e do modificador de Força (garantindo no mínimo 1).
                total_dano = max(1, dano_causado + mod_ataque_forca)
                # Subtrai a vida do monstro.
                monstro.vida_atual -= total_dano
                print(f"Você causa {total_dano} de dano!")
            else:
                print(f"Você ERROU o ataque.")
            
            # 'return' encerra a função e, consequentemente, o turno do jogador.
            return

        # --- AÇÃO: USAR ITEM ---
        elif escolha == '2':
            # Filtra o inventário para encontrar apenas itens que têm um efeito utilizável em combate.
            itens_utilizaveis = [item for item in buscar_detalhes_itens(jogador.inventario) if item[7] is not None]
            
            if not itens_utilizaveis:
                print("Você não tem itens utilizáveis em combate.")
                # 'continue' pula para a próxima iteração do loop, mostrando o menu novamente.
                continue

            print("\nQual item você quer usar?")
            # Mostra uma lista numerada de itens utilizáveis.
            for i, item in enumerate(itens_utilizaveis):
                print(f"{i + 1}. {item[1]}") # item[1] é o nome

            try:
                escolha_item = int(input("> ")) - 1
                if 0 <= escolha_item < len(itens_utilizaveis):
                    # Pega os dados do item escolhido.
                    item_usado = itens_utilizaveis[escolha_item]
                    nome_item, efeito_item = item_usado[1], item_usado[7]

                    # Processa o efeito (ex: "cura:10").
                    tipo_efeito, valor_efeito = efeito_item.split(':')
                    if tipo_efeito.lower() == 'cura':
                        # Chama o método 'curar' do próprio personagem.
                        jogador.curar(int(valor_efeito))
                    
                    # Remove o item consumido do inventário do jogador.
                    jogador.remover_item(nome_item)
                    print(f"Você usou '{nome_item}'.")
                    return # Encerra o turno do jogador
                else:
                    print("Escolha inválida.")
            except (ValueError, IndexError):
                print("Escolha inválida.")

        # --- AÇÃO: USAR HABILIDADE ---
        elif escolha == '3':
            # Verifica se o personagem conhece alguma habilidade.
            if not jogador.habilidades:
                print("Você não conhece nenhuma habilidade.")
                continue

            print("\nQual habilidade você quer usar?")
            # Busca os detalhes de todas as habilidades que o personagem conhece.
            habilidades_conhecidas = buscar_detalhes_habilidades(jogador.habilidades)
            
            # Mostra as habilidades numeradas com seu custo de mana.
            for i, hab in enumerate(habilidades_conhecidas):
                print(f"{i + 1}. {hab[1]} (Custo: {hab[4]} Mana)")

            try:
                escolha_hab = int(input("> ")) - 1
                if 0 <= escolha_hab < len(habilidades_conhecidas):
                    hab_usada = habilidades_conhecidas[escolha_hab]
                    nome_hab, efeito_hab, custo_mana = hab_usada[1], hab_usada[3], hab_usada[4]

                    # Verifica se o jogador tem mana suficiente para usar a habilidade.
                    if jogador.mana_atual >= custo_mana:
                        # Subtrai o custo de mana.
                        jogador.mana_atual -= custo_mana
                        print(f"\nVocê usa '{nome_hab}'!")
                        
                        # Processa o efeito da habilidade (ex: "dano:2d6:fogo").
                        partes_efeito = efeito_hab.split(':')
                        tipo_efeito = partes_efeito[0].lower()
                        valor_efeito = partes_efeito[1]

                        if tipo_efeito == 'dano':
                            dano, _ = rolar_dados(valor_efeito)
                            monstro.vida_atual -= dano
                            print(f"A magia causa {dano} de dano ao {monstro.nome}!")
                        elif tipo_efeito == 'cura':
                            jogador.curar(int(valor_efeito))
                        
                        return # Encerra o turno do jogador
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
    # A defesa do jogador é calculada com base em 10 + seu modificador de Destreza.
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
    
    # O loop principal da batalha: continua enquanto ambos os combatentes tiverem mais de 0 de vida.
    while jogador.vida_atual > 0 and monstro.vida_atual > 0:
        # Exibe o status da batalha no início de cada rodada.
        print(f"\nSua Vida: {jogador.vida_atual}/{jogador.vida_maxima} | Vida do {monstro.nome}: {monstro.vida_atual}/{monstro.vida_maxima}")
        
        # Chama a função que gerencia o turno do jogador.
        turno_do_jogador(jogador, monstro)
        # Pausa de 1 segundo para dar ritmo à batalha.
        time.sleep(1)

        # Após o turno do jogador, verifica se o monstro ainda está vivo.
        if monstro.vida_atual > 0:
            # Se sim, chama a função que gerencia o turno do monstro.
            turno_do_monstro(jogador, monstro)
            time.sleep(1)

    # Quando o loop termina, verifica quem venceu.
    if jogador.vida_atual <= 0:
        print("\n--- VOCÊ FOI DERROTADO ---")
        return False # Retorna False para indicar derrota.
    else:
        print(f"\n--- VOCÊ DERROTOU O {monstro.nome.upper()}! ---")
        # Concede as recompensas ao jogador.
        jogador.ouro += monstro.ouro_drop
        print(f"Você encontrou {monstro.ouro_drop} peças de ouro!")
        # Chama o método que gerencia o ganho de XP e possíveis level ups.
        jogador.ganhar_xp(monstro.xp_oferecido)
        return True # Retorna True para indicar vitória.