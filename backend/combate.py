# combate.py
from rolador_de_dados import rolar_dados
from personagem import Personagem
from monstro import Monstro
import time

def calcular_modificador(valor_atributo): return (valor_atributo - 10) // 2

def iniciar_combate(jogador: Personagem, monstro: Monstro):
    print(f"\n--- UM {monstro.nome.upper()} SELVAGEM APARECE! ---")
    
    while jogador.vida_atual > 0 and monstro.vida_atual > 0:
        # Turno do jogador (lógica interna sem alterações)
        print("\n--- SEU TURNO ---")
        # ... (código do turno do jogador permanece o mesmo)
        mod_ataque = calcular_modificador(jogador.atributos["Força"])
        rolagem_ataque, _ = rolar_dados("d20")
        total_ataque = rolagem_ataque + mod_ataque
        
        if total_ataque >= monstro.defesa:
            dado_dano = "1d4" if "Adaga" in jogador.inventario else "1d2"
            mod_dano = mod_ataque
            dano_causado, _ = rolar_dados(dado_dano)
            total_dano = max(1, dano_causado + mod_dano)
            monstro.vida_atual -= total_dano
            print(f"Você ACERTOU e causou {total_dano} de dano!")
        else:
            print(f"Você ERROU o ataque.")
        time.sleep(1)

        # Turno do monstro (lógica interna sem alterações)
        if monstro.vida_atual > 0:
            print(f"\n--- TURNO DO {monstro.nome.upper()} ---")
            # ... (código do turno do monstro permanece o mesmo)
            rolagem_ataque_monstro, _ = rolar_dados("d20")
            total_ataque_monstro = rolagem_ataque_monstro + monstro.ataque_bonus
            defesa_jogador = 10 + calcular_modificador(jogador.atributos["Destreza"])
            
            if total_ataque_monstro >= defesa_jogador:
                dano_causado, _ = rolar_dados(monstro.dano_dado)
                jogador.vida_atual -= dano_causado
                print(f"O {monstro.nome} ACERTOU e causou {dano_causado} de dano!")
            else:
                print(f"O {monstro.nome} ERROU o ataque.")
            time.sleep(1)

    # --- Fim do Combate ATUALIZADO ---
    if jogador.vida_atual <= 0:
        print("\n--- VOCÊ FOI DERROTADO ---")
        return False
    else:
        print(f"\n--- VOCÊ DERROTOU O {monstro.nome.upper()}! ---")
        # Concede as recompensas!
        jogador.ouro += monstro.ouro_drop
        print(f"Você encontrou {monstro.ouro_drop} peças de ouro!")
        # Chama o método para ganhar XP, que por sua vez, pode chamar o level up.
        jogador.ganhar_xp(monstro.xp_oferecido)
        return True