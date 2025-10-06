# monstro.py

class Monstro:
    def __init__(self, nome, vida_maxima, ataque_bonus, dano_dado, defesa, xp_oferecido, ouro_drop):
        self.nome = nome
        self.vida_maxima = vida_maxima
        self.vida_atual = vida_maxima
        self.ataque_bonus = ataque_bonus
        self.dano_dado = dano_dado
        self.defesa = defesa
        # --- ATRIBUTOS DE RECOMPENSA ---
        self.xp_oferecido = xp_oferecido
        self.ouro_drop = ouro_drop